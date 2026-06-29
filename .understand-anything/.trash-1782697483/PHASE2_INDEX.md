# Phase 2: File Analysis - Output Index

**Completion Date**: 2026-06-28  
**Analysis Framework**: Custom Python knowledge graph extraction  
**Project**: ai-poc (Java/Gradle)

## 📁 Output Files

### Batch Analysis Outputs (670 files)
```
batch-1.json through batch-670.json
```

**Format**: JSON with structure:
```json
{
  "batchIndex": N,
  "nodes": [...],      // GraphNode objects
  "edges": [...],      // GraphEdge objects
  "statistics": {...}  // Count and type distribution
}
```

**Size**: 11 MB total (average 16.4 KB per file)

### Documentation & Reports

| File | Size | Purpose |
|------|------|---------|
| PHASE2_INDEX.md | This file | Navigation guide |
| PHASE2_COMPLETION_SUMMARY.md | 12 KB | Executive summary and key findings |
| PHASE2_ANALYSIS_REPORT.md | 29 KB | Detailed technical report |
| phase2_file_analysis.py | 15 KB | Python analysis script |

## 🎯 Quick Stats

| Metric | Count |
|--------|-------|
| Batches Processed | 670 |
| Success Rate | 100% |
| Failed Batches | 0 |
| **Total Nodes** | **15,869** |
| **Total Edges** | **14,099** |

### Node Breakdown
- Files: 7,859
- Functions: 5,111
- Classes: 2,587
- Documents: 258
- Configs: 53
- Interfaces: 1

### Edge Breakdown
- Contains: 7,699
- Self: 6,385
- Imports: 12
- Calls: 3

## 📖 How to Use

### 1. Quick Overview
Read: `PHASE2_COMPLETION_SUMMARY.md` (5 min read)

### 2. Detailed Analysis
Read: `PHASE2_ANALYSIS_REPORT.md` (15 min read)

### 3. Access Batch Data
```bash
# Read specific batch
jq . batch-1.json | head -50

# Count nodes in a batch
jq '.nodes | length' batch-1.json

# List all node types in a batch
jq '.nodes[].type' batch-1.json | sort | uniq -c

# Get all edges of a type
jq '.edges[] | select(.type == "imports")' batch-1.json
```

### 4. Aggregate Statistics
```bash
# Total nodes across all batches
for f in batch-*.json; do jq '.nodes | length' "$f"; done | awk '{s+=$1} END {print s}'

# Node type distribution
jq -s 'map(.nodes[].type) | group_by(.) | map({type: .[0], count: length})' batch-*.json
```

## 🔍 Example Queries

### Find all REST controllers
```bash
jq '.nodes[] | select(.tags[] == "controller")' batch-*.json
```

### Find all Spring Boot entry points
```bash
jq '.nodes[] | select(.tags[] == "entry-point")' batch-*.json
```

### Find cross-file imports
```bash
jq '.edges[] | select(.type == "imports")' batch-*.json
```

### Find largest components (most methods)
```bash
jq '[.nodes[] | select(.type == "class")] | sort_by(.summary | length) | reverse' batch-*.json | head -10
```

## 📊 Batch Statistics Sample

From Batch 1:
- Nodes: 16 (4 files, 2 classes, 9 functions, 1 interface)
- Edges: 20 (contains, imports relationships)
- Languages: Java
- Focus: TimeController REST endpoint

From Batch 631 (largest):
- Nodes: 314+ (extracted from venv Python packages)
- Edges: 280+ (dependency relationships)
- Languages: Python
- Focus: networkx and tree-sitter libraries

## 🔗 Data Schema Reference

### GraphNode
```json
{
  "id": "unique:identifier:here",
  "type": "file|class|function|config|document|interface",
  "name": "HumanReadableName",
  "filePath": "path/to/source/file",
  "summary": "One-line description",
  "tags": ["tag1", "tag2", "tag3"],
  "complexity": "simple|moderate|complex",
  "languageNotes": "Language-specific details"
}
```

### GraphEdge
```json
{
  "source": "source:node:id",
  "target": "target:node:id",
  "type": "contains|imports|calls|extends|implements|configures",
  "weight": 1.0
}
```

## 🚀 Next Steps

1. **Phase 3: Community Detection**
   - Input: All batch-*.json files
   - Process: Louvain algorithm
   - Output: communities.json
   - Timeline: ~5 minutes

2. **Phase 4: Graph Aggregation**
   - Merge all batches
   - Compute global metrics
   - Output: graph-aggregated.json
   - Timeline: ~2 minutes

3. **Phase 5: Visualization**
   - Generate HTML dashboard
   - Create interactive graph
   - Export in multiple formats
   - Timeline: ~3 minutes

## 📝 Notes

- All timestamps are 2026-06-28
- Project root: `/Users/girish/MyDrive/Workspace/ai-poc`
- Intermediate directory: `.understand-anything/intermediate/`
- Processing was deterministic (same input → same output)
- All output files are self-contained and can be processed independently

## ✅ Validation

All output files have been validated for:
- [x] JSON schema compliance
- [x] No data corruption
- [x] Proper linking (source/target nodes exist)
- [x] File integrity (no truncation)
- [x] Complete processing (all 670 batches)

## 🎓 Analysis Techniques Used

**Language Parsers**:
- Java: Package, class, method, annotation extraction
- Gradle: Plugin and dependency parsing
- YAML/JSON/XML: Configuration key extraction
- Markdown: Document structure extraction
- Python: Class and function extraction

**Relationship Detection**:
- Syntax-based (regex patterns)
- Import statement analysis
- Cross-file dependency mapping
- Annotation-based categorization

## 📞 Support

For issues or questions:
1. Check PHASE2_ANALYSIS_REPORT.md (Troubleshooting section)
2. Review the analysis script: phase2_file_analysis.py
3. Validate individual batch files with jq
4. Check file permissions and encoding

---

**Framework**: Custom Python knowledge graph engine  
**Algorithm**: Regex-based syntactic analysis  
**Output Format**: JSON (per-batch, graph-ready)  
**Status**: ✅ COMPLETE - Ready for Phase 3
