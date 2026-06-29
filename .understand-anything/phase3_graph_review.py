#!/usr/bin/env python3
"""Phase 3: Assembled Graph Reviewer

Validates the assembled knowledge graph for:
- Orphan nodes (no edges)
- Dangling edge references
- Schema violations
- Naming consistency
- Quality metrics
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_graph(graph_path):
    """Load and parse assembled graph."""
    print(f"Loading graph from {graph_path}...")
    with open(graph_path, 'r') as f:
        graph = json.load(f)
    return graph

def build_indexes(graph):
    """Build node and edge indexes."""
    print("Building indexes...")
    node_ids = set()
    node_types = defaultdict(int)
    edge_types = defaultdict(int)
    node_edges = defaultdict(list)  # node_id -> list of edge indices
    
    # Index all nodes
    nodes = graph.get('nodes', [])
    for i, node in enumerate(nodes):
        node_id = node.get('id')
        if node_id:
            node_ids.add(node_id)
            node_type = node.get('type', 'unknown')
            node_types[node_type] += 1
    
    # Index all edges and track node references
    edges = graph.get('edges', [])
    for i, edge in enumerate(edges):
        source = edge.get('source')
        target = edge.get('target')
        edge_type = edge.get('type', 'unknown')
        edge_types[edge_type] += 1
        
        if source:
            node_edges[source].append(i)
        if target:
            node_edges[target].append(i)
    
    return {
        'node_ids': node_ids,
        'node_types': node_types,
        'edge_types': edge_types,
        'node_edges': node_edges,
        'nodes': nodes,
        'edges': edges
    }

def check_orphan_nodes(nodes, node_edges):
    """Find nodes with no edges."""
    print("Checking for orphan nodes...")
    orphans = []
    for node in nodes:
        node_id = node.get('id')
        if node_id and len(node_edges.get(node_id, [])) == 0:
            orphans.append(node_id)
    return orphans

def check_dangling_edges(edges, node_ids):
    """Find edges with missing source or target nodes."""
    print("Checking for dangling edges...")
    dangling = []
    for i, edge in enumerate(edges):
        source = edge.get('source')
        target = edge.get('target')
        
        if not source or source not in node_ids:
            dangling.append({
                'edge_index': i,
                'issue': f"Missing or invalid source: {source}",
                'edge': edge
            })
        elif not target or target not in node_ids:
            dangling.append({
                'edge_index': i,
                'issue': f"Missing or invalid target: {target}",
                'edge': edge
            })
    
    return dangling

def check_schema_violations(nodes, edges):
    """Check for schema consistency."""
    print("Checking schema violations...")
    violations = []
    
    # Check node schema
    for i, node in enumerate(nodes):
        if 'id' not in node:
            violations.append({
                'type': 'node',
                'issue': 'Missing id',
                'index': i
            })
        if 'type' not in node:
            violations.append({
                'type': 'node',
                'issue': 'Missing type',
                'index': i,
                'node_id': node.get('id')
            })
    
    # Check edge schema
    for i, edge in enumerate(edges):
        missing_fields = []
        if 'source' not in edge:
            missing_fields.append('source')
        if 'target' not in edge:
            missing_fields.append('target')
        if 'type' not in edge:
            missing_fields.append('type')
        
        if missing_fields:
            violations.append({
                'type': 'edge',
                'issue': f"Missing fields: {', '.join(missing_fields)}",
                'index': i
            })
    
    return violations

def check_naming_consistency(nodes):
    """Check for naming issues."""
    print("Checking naming consistency...")
    issues = []
    naming_stats = {
        'missing_names': 0,
        'empty_names': 0,
        'unusual_patterns': []
    }
    
    for node in nodes:
        node_id = node.get('id')
        name = node.get('name')
        
        if not name:
            naming_stats['missing_names'] += 1
            if naming_stats['missing_names'] <= 5:
                issues.append({
                    'node_id': node_id,
                    'issue': 'Missing name field'
                })
        elif name.strip() == '':
            naming_stats['empty_names'] += 1
    
    return issues, naming_stats

def check_duplicate_ids(nodes):
    """Check for duplicate node IDs."""
    print("Checking for duplicate IDs...")
    seen_ids = {}
    duplicates = []
    
    for i, node in enumerate(nodes):
        node_id = node.get('id')
        if node_id:
            if node_id in seen_ids:
                duplicates.append({
                    'id': node_id,
                    'indices': [seen_ids[node_id], i]
                })
            else:
                seen_ids[node_id] = i
    
    return duplicates

def check_complexity(nodes, node_edges):
    """Check for nodes with excessive edges."""
    print("Checking node complexity...")
    high_complexity = []
    complexity_threshold = 100
    
    for node in nodes:
        node_id = node.get('id')
        if node_id:
            edge_count = len(node_edges.get(node_id, []))
            if edge_count > complexity_threshold:
                high_complexity.append({
                    'node_id': node_id,
                    'edge_count': edge_count
                })
    
    return high_complexity

def compute_quality_metrics(nodes, edges, node_edges, orphans):
    """Compute quality metrics."""
    print("Computing quality metrics...")
    
    total_nodes = len(nodes)
    total_edges = len(edges)
    
    # Graph density
    if total_nodes > 0:
        max_edges = total_nodes * (total_nodes - 1)
        graph_density = total_edges / max_edges if max_edges > 0 else 0
    else:
        graph_density = 0
    
    # Average edges per node
    avg_edges_per_node = total_edges / total_nodes if total_nodes > 0 else 0
    
    # Connected components (approximation: count components with >1 node)
    visited = set()
    component_count = 0
    
    def dfs(node_id, visited_set):
        visited_set.add(node_id)
        for edge_idx in node_edges.get(node_id, []):
            edge = edges[edge_idx]
            next_node = edge.get('source') if edge.get('target') == node_id else edge.get('target')
            if next_node and next_node not in visited_set:
                dfs(next_node, visited_set)
    
    for node in nodes:
        node_id = node.get('id')
        if node_id and node_id not in visited:
            dfs(node_id, visited)
            component_count += 1
    
    return {
        'graphDensity': round(graph_density, 5),
        'avgEdgesPerNode': round(avg_edges_per_node, 2),
        'connectedComponentCount': component_count,
        'orphanNodeCount': len(orphans)
    }

def generate_review(graph_path, output_path):
    """Generate comprehensive review."""
    try:
        # Load and index
        graph = load_graph(graph_path)
        indexes = build_indexes(graph)
        
        nodes = indexes['nodes']
        edges = indexes['edges']
        node_ids = indexes['node_ids']
        node_edges = indexes['node_edges']
        
        print(f"Graph loaded: {len(nodes)} nodes, {len(edges)} edges")
        
        # Run all checks
        orphans = check_orphan_nodes(nodes, node_edges)
        dangling = check_dangling_edges(edges, node_ids)
        schema_issues = check_schema_violations(nodes, edges)
        naming_issues, naming_stats = check_naming_consistency(nodes)
        duplicates = check_duplicate_ids(nodes)
        high_complexity = check_complexity(nodes, node_edges)
        metrics = compute_quality_metrics(nodes, edges, node_edges, orphans)
        
        # Determine validation status
        critical_issues = len(dangling) + len(duplicates) + len([i for i in schema_issues if i.get('issue', '').startswith('Missing')])
        validation_status = 'fail' if critical_issues > 0 else ('warning' if len(orphans) > 0 or len(high_complexity) > 0 else 'pass')
        
        # Build review
        review = {
            'validationStatus': validation_status,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'summary': {
                'totalNodes': len(nodes),
                'totalEdges': len(edges),
                'nodeTypeDistribution': dict(indexes['node_types']),
                'edgeTypeDistribution': dict(indexes['edge_types'])
            },
            'issues': []
        }
        
        # Add issues
        if orphans:
            review['issues'].append({
                'severity': 'warning',
                'category': 'orphan_nodes',
                'count': len(orphans),
                'examples': orphans[:10],
                'recommendation': 'Orphan nodes with no edges may indicate incomplete extraction or isolated components. Review and consider removing if not intentional.'
            })
        
        if dangling:
            dangling_examples = [d['issue'] for d in dangling[:5]]
            review['issues'].append({
                'severity': 'critical',
                'category': 'dangling_refs',
                'count': len(dangling),
                'examples': dangling_examples,
                'recommendation': 'Dangling edge references break graph integrity. Rebuild the graph or remove invalid edges.'
            })
        
        critical_schema = [i for i in schema_issues if 'Missing' in i.get('issue', '')]
        if critical_schema:
            review['issues'].append({
                'severity': 'critical',
                'category': 'schema_violation',
                'count': len(critical_schema),
                'examples': [s['issue'] for s in critical_schema[:5]],
                'recommendation': 'Schema violations must be fixed. Add missing required fields.'
            })
        
        if duplicates:
            review['issues'].append({
                'severity': 'critical',
                'category': 'duplicate_ids',
                'count': len(duplicates),
                'examples': [d['id'] for d in duplicates[:5]],
                'recommendation': 'Duplicate node IDs violate graph uniqueness. Merge duplicates or rename conflicting nodes.'
            })
        
        if naming_stats['missing_names'] > 0:
            review['issues'].append({
                'severity': 'warning',
                'category': 'naming_inconsistency',
                'count': naming_stats['missing_names'],
                'examples': [i['node_id'] for i in naming_issues[:5]],
                'recommendation': 'Nodes without names reduce graph readability. Add name fields from node ID or source.'
            })
        
        if high_complexity:
            review['issues'].append({
                'severity': 'info',
                'category': 'high_complexity_nodes',
                'count': len(high_complexity),
                'examples': [(h['node_id'], h['edge_count']) for h in high_complexity[:5]],
                'recommendation': 'Highly connected nodes may represent important hub components. Review for potential factoring or role specialization.'
            })
        
        review['qualityMetrics'] = metrics
        review['notes'] = f"""
Graph Review Summary:
- Total nodes: {len(nodes)}
- Total edges: {len(edges)}
- Orphan nodes: {len(orphans)} ({100*len(orphans)/len(nodes):.1f}% of nodes)
- Dangling edges: {len(dangling)}
- Schema violations: {len(schema_issues)}
- Duplicate IDs: {len(duplicates)}
- Nodes with high complexity (>100 edges): {len(high_complexity)}
- Node types: {len(indexes['node_types'])} distinct types
- Edge types: {len(indexes['edge_types'])} distinct types
- Graph connectivity: {metrics['connectedComponentCount']} components
- Average edges per node: {metrics['avgEdgesPerNode']:.2f}

Validation Status: {validation_status.upper()}
"""
        
        # Write review
        print(f"Writing review to {output_path}...")
        with open(output_path, 'w') as f:
            json.dump(review, f, indent=2)
        
        print(f"✓ Review complete: {validation_status}")
        print(f"  - Critical issues: {critical_issues}")
        print(f"  - Warnings: {len(orphans) + len(high_complexity)}")
        print(f"  - Info: {len(review['issues']) - (critical_issues + len(orphans) + len(high_complexity))}")
        
        return review
        
    except Exception as e:
        print(f"Error during review: {e}", file=sys.stderr)
        raise

if __name__ == '__main__':
    graph_path = Path('/Users/girish/MyDrive/Workspace/ai-poc/.understand-anything/intermediate/assembled-graph.json')
    output_path = Path('/Users/girish/MyDrive/Workspace/ai-poc/.understand-anything/intermediate/assemble-review.json')
    
    review = generate_review(str(graph_path), str(output_path))
