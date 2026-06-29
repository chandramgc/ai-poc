#!/usr/bin/env python3
"""
Phase 4: Architecture Analysis (Enhanced)
Identifies architectural layers from the assembled graph with improved categorization.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Configuration
GRAPH_FILE = Path("/Users/girish/MyDrive/Workspace/ai-poc/.understand-anything/intermediate/assembled-graph.json")
OUTPUT_FILE = Path("/Users/girish/MyDrive/Workspace/ai-poc/.understand-anything/intermediate/layers.json")

# Layer definitions with detection rules
LAYER_DEFINITIONS = {
    "entry-point": {
        "name": "Entry Point",
        "description": "Application bootstrap and main entry point",
        "patterns": [
            r"Application\.java$",
            r"Main\.java$",
        ],
        "tags_patterns": [
            r"@SpringBootApplication",
        ],
        "nodeIds": []
    },
    "http": {
        "name": "HTTP Layer",
        "description": "REST controllers and HTTP request handlers",
        "patterns": [
            r"/controller/.*\.java$",
        ],
        "tags_patterns": [
            r"@RestController",
            r"@RequestMapping",
            r"@GetMapping|@PostMapping|@PutMapping|@DeleteMapping|@PatchMapping",
            r"annotation:RestController",
        ],
        "nodeIds": []
    },
    "service": {
        "name": "Service Layer",
        "description": "Business logic and service implementations",
        "patterns": [
            r"/service/.*\.java$",
        ],
        "tags_patterns": [
            r"@Service",
            r"annotation:Service",
        ],
        "nodeIds": []
    },
    "data": {
        "name": "Data Layer",
        "description": "Repositories and data access logic",
        "patterns": [
            r"/repository/.*\.java$",
            r"/mapper/.*\.java$",
            r"/persistence/.*\.java$",
        ],
        "tags_patterns": [
            r"@Repository",
            r"@Mapper",
            r"annotation:Repository",
        ],
        "nodeIds": []
    },
    "dto": {
        "name": "Data Transfer Objects",
        "description": "DTOs, request/response models, and data classes",
        "patterns": [
            r"/dto/.*\.java$",
            r"/model/.*\.java$",
            r"/entity/.*\.java$",
            r"/payload/.*\.java$",
            r"Request\.java$",
            r"Response\.java$",
        ],
        "tags_patterns": [],
        "nodeIds": []
    },
    "testing": {
        "name": "Testing",
        "description": "Unit tests, integration tests, and test utilities",
        "patterns": [
            r"src/test/java/.*\.java$",
            r"Test\.java$",
            r"Tests\.java$",
        ],
        "tags_patterns": [
            r"annotation:Test",
            r"tested",
        ],
        "nodeIds": []
    },
    "config": {
        "name": "Configuration",
        "description": "Spring configuration, beans, and dependency injection",
        "patterns": [
            r"/config/.*\.java$",
            r"application\.yml$",
            r"application\.yaml$",
            r"application\.properties$",
            r"application-.*\.properties$",
            r"\.properties$",
        ],
        "tags_patterns": [
            r"@Configuration",
            r"@Bean",
            r"annotation:Configuration",
        ],
        "nodeIds": []
    },
    "infrastructure": {
        "name": "Infrastructure & DevOps",
        "description": "Docker, CI/CD, deployment configurations",
        "patterns": [
            r"Dockerfile$",
            r"docker-compose\.yml$",
            r"\.github/workflows/",
            r"\.dockerignore$",
            r"\.github/",
            r"build\.gradle$",
            r"settings\.gradle$",
            r"gradlew$",
            r"pom\.xml$",
            r"Makefile$",
        ],
        "tags_patterns": [],
        "nodeIds": []
    },
    "documentation": {
        "name": "Documentation",
        "description": "README, API guides, and architectural documentation",
        "patterns": [
            r"\.md$",
            r"docs/",
        ],
        "tags_patterns": [],
        "nodeIds": []
    },
    "utilities": {
        "name": "Utilities & Helpers",
        "description": "Common utilities, helper classes, and shared code",
        "patterns": [
            r"/util/.*\.java$",
            r"/common/.*\.java$",
            r"/helper/.*\.java$",
            r"/exception/.*\.java$",
            r"/constants/.*\.java$",
        ],
        "tags_patterns": [],
        "nodeIds": []
    },
}

def classify_node(node):
    """Classify a node into a layer based on patterns."""
    node_id = node.get("id", "")
    file_path = node.get("filePath", "")
    tags = node.get("tags", [])
    node_type = node.get("type", "")
    
    # Prioritize by checking each layer in order
    # Check tags first (higher priority as they're more explicit)
    for layer_key, layer_def in LAYER_DEFINITIONS.items():
        for pattern in layer_def["tags_patterns"]:
            if any(re.search(pattern, tag) for tag in tags):
                return layer_key
    
    # Then check file path patterns
    for layer_key, layer_def in LAYER_DEFINITIONS.items():
        for pattern in layer_def["patterns"]:
            if re.search(pattern, file_path):
                return layer_key
    
    # Default classification based on path structure
    if file_path:
        if "src/test" in file_path and file_path.endswith(".java"):
            return "testing"
        elif "src/main/java" in file_path and file_path.endswith(".java"):
            # Fallback to utilities for unclassified Java files
            return "utilities"
        elif file_path.endswith((".md", ".markdown")):
            return "documentation"
        elif any(x in file_path.lower() for x in ["config", "yml", "yaml", "properties"]):
            return "config"
    
    return None

def analyze_graph():
    """Analyze the assembled graph and classify nodes into layers."""
    print(f"Reading graph from {GRAPH_FILE}...")
    
    with open(GRAPH_FILE, 'r') as f:
        graph_data = json.load(f)
    
    nodes = graph_data.get("nodes", [])
    print(f"Total nodes: {len(nodes)}")
    
    # Reset nodeIds for all layers
    for layer_def in LAYER_DEFINITIONS.values():
        layer_def["nodeIds"] = []
    
    uncategorized = []
    categorized_count = 0
    
    # Classify each node
    for node in nodes:
        node_id = node.get("id", "")
        layer_key = classify_node(node)
        
        if layer_key:
            LAYER_DEFINITIONS[layer_key]["nodeIds"].append(node_id)
            categorized_count += 1
        else:
            uncategorized.append({
                "id": node_id,
                "filePath": node.get("filePath", ""),
                "type": node.get("type", ""),
                "tags": node.get("tags", [])
            })
    
    # Print summary
    print("\n=== Layer Classification Summary ===")
    for layer_key, layer_def in LAYER_DEFINITIONS.items():
        count = len(layer_def["nodeIds"])
        if count > 0:
            print(f"{layer_def['name']}: {count} nodes")
    
    print(f"\nTotal categorized: {categorized_count}")
    print(f"Uncategorized nodes: {len(uncategorized)}")
    
    # Analyze uncategorized by type
    uncategorized_by_type = defaultdict(int)
    uncategorized_by_type_samples = defaultdict(list)
    
    for item in uncategorized:
        node_type = item['type']
        uncategorized_by_type[node_type] += 1
        if len(uncategorized_by_type_samples[node_type]) < 3:
            uncategorized_by_type_samples[node_type].append(item['id'])
    
    print("\nUncategorized by type:")
    for node_type in sorted(uncategorized_by_type.keys()):
        count = uncategorized_by_type[node_type]
        samples = uncategorized_by_type_samples[node_type]
        print(f"  {node_type}: {count}")
        for sample in samples[:1]:
            print(f"    Sample: {sample}")
    
    return uncategorized

def generate_layers_json():
    """Generate the layers.json output file."""
    layers = []
    
    for layer_key, layer_def in LAYER_DEFINITIONS.items():
        if layer_def["nodeIds"]:  # Only include layers with nodes
            layers.append({
                "id": f"layer:{layer_key}",
                "name": layer_def["name"],
                "description": layer_def["description"],
                "nodeCount": len(layer_def["nodeIds"]),
                "nodeIds": sorted(layer_def["nodeIds"])
            })
    
    # Sort by nodeCount (descending)
    layers.sort(key=lambda x: x["nodeCount"], reverse=True)
    
    # Remove nodeCount for final output (as per spec)
    for layer in layers:
        del layer["nodeCount"]
    
    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(layers, f, indent=2)
    
    print(f"\n✓ Output written to {OUTPUT_FILE}")
    print(f"Total layers: {len(layers)}")
    
    # Print layer summary
    print("\n=== Final Layers ===")
    for layer in layers:
        print(f"  {layer['name']}: {len(layer['nodeIds'])} nodes")

def main():
    """Main analysis function."""
    print("=" * 70)
    print("Phase 4: Architecture Analysis (Enhanced)")
    print("=" * 70)
    
    uncategorized = analyze_graph()
    generate_layers_json()
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
