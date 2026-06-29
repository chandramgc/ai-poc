#!/usr/bin/env python3
"""
Phase 2: File Analysis
Analyzes batched project files to produce GraphNode and GraphEdge objects for the knowledge graph.
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import sys

# Paths
PROJECT_ROOT = "/Users/girish/MyDrive/Workspace/ai-poc"
INTERMEDIATE_DIR = os.path.join(PROJECT_ROOT, ".understand-anything/intermediate")
BATCHES_FILE = os.path.join(INTERMEDIATE_DIR, "batches.json")
OUTPUT_DIR = INTERMEDIATE_DIR

@dataclass
class GraphNode:
    id: str
    type: str
    name: str
    filePath: str
    summary: str
    tags: List[str]
    complexity: str = "moderate"
    languageNotes: str = ""

@dataclass
class GraphEdge:
    source: str
    target: str
    type: str
    weight: float = 1.0

class FileAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.import_cache: Dict[str, Set[str]] = {}

    def add_node(self, node: GraphNode):
        """Add a node to the graph"""
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0):
        """Add an edge to the graph"""
        edge = GraphEdge(source=source, target=target, type=edge_type, weight=weight)
        self.edges.append(edge)

    def read_file(self, file_path: str) -> Optional[str]:
        """Read file contents"""
        full_path = os.path.join(self.project_root, file_path)
        try:
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            pass
        return None

    def analyze_java_file(self, file_path: str, content: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Analyze Java file"""
        nodes = []
        edges = []
        
        # Create file node
        file_id = f"file:{file_path}"
        file_node = GraphNode(
            id=file_id,
            type="file",
            name=Path(file_path).stem,
            filePath=file_path,
            summary=f"Java source file",
            tags=["java"],
            complexity="moderate",
            languageNotes="Java source file"
        )
        nodes.append(file_node)
        
        # Extract package
        package_match = re.search(r'package\s+([\w.]+);', content)
        if package_match:
            package_name = package_match.group(1)
            file_node.tags.append(f"package:{package_name}")
        
        # Extract class definitions
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+([\w.]+))?(?:\s+implements\s+([\w\s,.]+))?'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends = match.group(2)
            implements = match.group(3)
            
            class_id = f"class:{file_path}:{class_name}"
            class_node = GraphNode(
                id=class_id,
                type="class",
                name=class_name,
                filePath=file_path,
                summary=f"Class {class_name}",
                tags=["java", "class"],
                complexity="moderate"
            )
            nodes.append(class_node)
            edges.append(GraphEdge(source=file_id, target=class_id, type="contains"))
            
            # Add inheritance edge
            if extends and extends != "Object":
                edges.append(GraphEdge(source=class_id, target=f"class:{extends}", type="extends"))
        
        # Extract interface definitions
        interface_pattern = r'(?:public\s+)?interface\s+(\w+)(?:\s+extends\s+([\w\s,.]+))?'
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            interface_id = f"interface:{file_path}:{interface_name}"
            interface_node = GraphNode(
                id=interface_id,
                type="interface",
                name=interface_name,
                filePath=file_path,
                summary=f"Interface {interface_name}",
                tags=["java", "interface"],
                complexity="simple"
            )
            nodes.append(interface_node)
            edges.append(GraphEdge(source=file_id, target=interface_id, type="contains"))
        
        # Extract methods
        method_pattern = r'(?:public|private|protected)?\s+(?:static\s+)?(?:synchronized\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            
            if method_name not in ['if', 'for', 'while', 'switch', 'catch']:
                method_id = f"method:{file_path}:{method_name}"
                method_node = GraphNode(
                    id=method_id,
                    type="function",
                    name=method_name,
                    filePath=file_path,
                    summary=f"Method {method_name} returning {return_type}",
                    tags=["java", "method"],
                    complexity="moderate"
                )
                nodes.append(method_node)
                edges.append(GraphEdge(source=file_id, target=method_id, type="contains"))
        
        # Extract annotations
        annotation_pattern = r'@(\w+)'
        annotations = set()
        for match in re.finditer(annotation_pattern, content):
            annotations.add(match.group(1))
        
        if annotations:
            file_node.tags.extend([f"annotation:{ann}" for ann in annotations])
            
            # Spring Boot specific
            if "SpringBootApplication" in annotations:
                file_node.tags.append("entry-point")
            if "RestController" in annotations or "Controller" in annotations:
                file_node.tags.append("controller")
            if "Service" in annotations:
                file_node.tags.append("service")
            if "Repository" in annotations:
                file_node.tags.append("repository")
        
        # Extract imports
        import_pattern = r'import\s+(static\s+)?([\w.]+);'
        imports = []
        for match in re.finditer(import_pattern, content):
            import_name = match.group(2)
            imports.append(import_name)
        
        if imports:
            file_node.tags.append(f"imports:{len(imports)}")
        
        return nodes, edges

    def analyze_gradle_file(self, file_path: str, content: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Analyze Gradle file"""
        nodes = []
        edges = []
        
        file_id = f"file:{file_path}"
        file_node = GraphNode(
            id=file_id,
            type="config",
            name=Path(file_path).stem,
            filePath=file_path,
            summary="Gradle build configuration",
            tags=["gradle", "config", "build"],
            complexity="moderate"
        )
        nodes.append(file_node)
        
        # Extract plugins
        plugin_pattern = r"id\s+['\"]([^'\"]+)['\"]"
        plugins = []
        for match in re.finditer(plugin_pattern, content):
            plugin_name = match.group(1)
            plugins.append(plugin_name)
            file_node.tags.append(f"plugin:{plugin_name}")
        
        # Extract dependencies
        dep_pattern = r"(?:implementation|testImplementation|compileOnly|runtimeOnly)\s+['\"]([^'\"]+)['\"]"
        dependencies = []
        for match in re.finditer(dep_pattern, content):
            dep_name = match.group(1)
            dependencies.append(dep_name)
        
        if dependencies:
            file_node.tags.append(f"dependencies:{len(dependencies)}")
        
        return nodes, edges

    def analyze_config_file(self, file_path: str, content: str, language: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Analyze configuration files (YAML, JSON, XML, properties)"""
        nodes = []
        edges = []
        
        file_id = f"file:{file_path}"
        config_type = language.upper()
        file_node = GraphNode(
            id=file_id,
            type="config",
            name=Path(file_path).stem,
            filePath=file_path,
            summary=f"{config_type} configuration file",
            tags=[language, "config"],
            complexity="simple"
        )
        nodes.append(file_node)
        
        try:
            if language == "json":
                data = json.loads(content)
                file_node.tags.append(f"keys:{len(data) if isinstance(data, dict) else 'array'}")
            elif language == "yaml":
                # Simple YAML key extraction
                keys = set(re.findall(r'^(\w+):', content, re.MULTILINE))
                file_node.tags.append(f"keys:{len(keys)}")
        except:
            pass
        
        return nodes, edges

    def analyze_markdown_file(self, file_path: str, content: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Analyze Markdown documentation"""
        nodes = []
        edges = []
        
        file_id = f"file:{file_path}"
        file_node = GraphNode(
            id=file_id,
            type="document",
            name=Path(file_path).stem,
            filePath=file_path,
            summary="Markdown documentation",
            tags=["markdown", "documentation"],
            complexity="simple"
        )
        nodes.append(file_node)
        
        # Extract headings
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        if headings:
            file_node.tags.extend([f"section:{h[:30]}" for h in headings[:10]])
        
        # Check for code blocks
        code_blocks = len(re.findall(r'```', content))
        if code_blocks:
            file_node.tags.append(f"code_blocks:{code_blocks // 2}")
        
        return nodes, edges

    def analyze_python_file(self, file_path: str, content: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Analyze Python file"""
        nodes = []
        edges = []
        
        file_id = f"file:{file_path}"
        file_node = GraphNode(
            id=file_id,
            type="file",
            name=Path(file_path).stem,
            filePath=file_path,
            summary="Python source file",
            tags=["python"],
            complexity="moderate"
        )
        nodes.append(file_node)
        
        # Extract class definitions
        class_pattern = r'^class\s+(\w+)(?:\(([^)]+)\))?:'
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            bases = match.group(2)
            
            class_id = f"class:{file_path}:{class_name}"
            class_node = GraphNode(
                id=class_id,
                type="class",
                name=class_name,
                filePath=file_path,
                summary=f"Python class {class_name}",
                tags=["python", "class"],
                complexity="moderate"
            )
            nodes.append(class_node)
            edges.append(GraphEdge(source=file_id, target=class_id, type="contains"))
        
        # Extract function definitions
        func_pattern = r'^def\s+(\w+)\s*\([^)]*\):'
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            if not func_name.startswith('_'):
                func_id = f"function:{file_path}:{func_name}"
                func_node = GraphNode(
                    id=func_id,
                    type="function",
                    name=func_name,
                    filePath=file_path,
                    summary=f"Python function {func_name}",
                    tags=["python", "function"],
                    complexity="moderate"
                )
                nodes.append(func_node)
                edges.append(GraphEdge(source=file_id, target=func_id, type="contains"))
        
        # Extract imports
        import_pattern = r'^(?:from|import)\s+(.+?)(?:\s+import\s+(.+))?$'
        imports = []
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1)
            imports.append(module)
        
        if imports:
            file_node.tags.append(f"imports:{len(imports)}")
        
        return nodes, edges

    def analyze_batch(self, batch: Dict) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Analyze a single batch"""
        all_nodes = []
        all_edges = []
        
        batch_index = batch.get('batchIndex', 0)
        files_info = batch.get('files', [])
        import_data = batch.get('batchImportData', {})
        neighbor_map = batch.get('neighborMap', {})
        
        # Process each file in the batch
        for file_info in files_info:
            file_path = file_info.get('path')
            language = file_info.get('language')
            
            content = self.read_file(file_path)
            if not content:
                continue
            
            # Analyze based on language
            nodes = []
            edges = []
            
            if language == 'java':
                nodes, edges = self.analyze_java_file(file_path, content)
            elif language == 'gradle':
                nodes, edges = self.analyze_gradle_file(file_path, content)
            elif language in ['yaml', 'json', 'xml', 'properties']:
                nodes, edges = self.analyze_config_file(file_path, content, language)
            elif language == 'markdown':
                nodes, edges = self.analyze_markdown_file(file_path, content)
            elif language == 'python':
                nodes, edges = self.analyze_python_file(file_path, content)
            else:
                # Generic file node
                file_id = f"file:{file_path}"
                file_node = GraphNode(
                    id=file_id,
                    type="file",
                    name=Path(file_path).stem,
                    filePath=file_path,
                    summary=f"{language.capitalize()} file",
                    tags=[language] if language != 'unknown' else [],
                    complexity="simple"
                )
                nodes.append(file_node)
                edges.append(GraphEdge(source=file_id, target=file_id, type="self"))
            
            # Add import edges for files in this batch
            file_path_key = file_path
            if file_path_key in import_data:
                file_id = f"file:{file_path}"
                for imported_path in import_data[file_path_key]:
                    target_id = f"file:{imported_path}"
                    edges.append(GraphEdge(source=file_id, target=target_id, type="imports", weight=0.8))
            
            all_nodes.extend(nodes)
            all_edges.extend(edges)
        
        # Add cross-batch edges from neighbor map
        for file_path, neighbors in neighbor_map.items():
            source_id = f"file:{file_path}"
            for neighbor in neighbors:
                target_path = neighbor.get('path')
                symbols = neighbor.get('symbols', [])
                target_id = f"file:{target_path}"
                
                edge_type = "calls" if symbols else "imports"
                all_edges.append(GraphEdge(source=source_id, target=target_id, type=edge_type, weight=0.6))
        
        return all_nodes, all_edges


def process_all_batches():
    """Process all batches and write output files"""
    
    # Load batches
    print("Loading batches.json...")
    with open(BATCHES_FILE, 'r') as f:
        data = json.load(f)
    
    batches = data.get('batches', [])
    total_batches = len(batches)
    
    print(f"Total batches to process: {total_batches}")
    
    analyzer = FileAnalyzer(PROJECT_ROOT)
    
    # Track statistics
    total_nodes = 0
    total_edges = 0
    processed_batches = 0
    failed_batches = 0
    
    # Process each batch
    for batch_idx, batch in enumerate(batches):
        batch_index = batch.get('batchIndex', batch_idx)
        
        try:
            # Analyze batch
            nodes, edges = analyzer.analyze_batch(batch)
            
            # Prepare output
            output_data = {
                "batchIndex": batch_index,
                "nodes": [asdict(node) for node in nodes],
                "edges": [asdict(edge) for edge in edges],
                "statistics": {
                    "nodeCount": len(nodes),
                    "edgeCount": len(edges),
                    "nodeTypes": {}
                }
            }
            
            # Count node types
            for node in nodes:
                node_type = node.type
                output_data["statistics"]["nodeTypes"][node_type] = \
                    output_data["statistics"]["nodeTypes"].get(node_type, 0) + 1
            
            # Write output file
            output_file = os.path.join(OUTPUT_DIR, f"batch-{batch_index}.json")
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            total_nodes += len(nodes)
            total_edges += len(edges)
            processed_batches += 1
            
            # Progress report every 50 batches
            if (batch_idx + 1) % 50 == 0:
                print(f"Progress: {batch_idx + 1}/{total_batches} batches processed")
                print(f"  Total nodes: {total_nodes}, Total edges: {total_edges}")
            
        except Exception as e:
            failed_batches += 1
            print(f"Error processing batch {batch_index}: {str(e)}")
    
    # Final report
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)
    print(f"Batches processed: {processed_batches}/{total_batches}")
    print(f"Failed batches: {failed_batches}")
    print(f"Total nodes extracted: {total_nodes}")
    print(f"Total edges extracted: {total_edges}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60)


if __name__ == "__main__":
    process_all_batches()
