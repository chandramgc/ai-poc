# Project with Automation

This project uses three powerful automation tools for enhanced development:

## 🌱 Spec Kit (Spec-Driven Development)

Spec-Driven Development (SDD) flips the script - specifications become executable,
directly generating working implementations rather than just guiding them.

**Setup:**
```bash
cd automation/sdd
./run-sdd.sh constitution  # Create project principles
./run-sdd.sh specify       # Define what to build
./run-sdd.sh plan          # Create technical plan
./run-sdd.sh tasks         # Generate task list
./run-sdd.sh implement     # Execute tasks
```

### Spec Kit Resources
- 📖 [Spec Kit Documentation](https://github.github.io/spec-kit/)
- 🎥 [Video Overview](https://www.youtube.com/watch?v=a9eR1xsfvHg)
- 📚 [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)

---

## 🐴 Ponytail

Makes your AI agent think like the laziest (best) senior developer. The best code
is the code you never wrote. ~54% less code, ~20% cheaper, ~27% faster.

**Laziness Ladder:**
```
1. Does this need to exist?   → No: skip it (YAGNI)
2. Already in this codebase?  → Reuse it
3. Stdlib does it?            → Use it
4. Native platform feature?   → Use it
5. Installed dependency?      → Use it
6. One line?                  → One line
7. Only then: the minimum that works
```

**Setup:**
```bash
cd automation/ponytail
./install-ponytail.sh all
```

### Ponytail Resources
- 🔧 [Ponytail Repository](https://github.com/DietrichGebert/ponytail)
- 📊 [Benchmark Results](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-18-agentic.md)
- 📝 [AGENTS.md Integration](./AGENTS.md)

---

## 🧠 Graphify

Maps your entire project—code, docs, PDFs, images, videos—into a queryable knowledge graph.
Let your AI assistant access the graph immediately instead of reading files one-by-one.

**Usage:**
```bash
cd automation/graphify
./run-graphify.sh build      # Generate knowledge graph
./run-graphify.sh update     # Update changed files only
./run-graphify.sh query "What connects auth to the database?"
./run-graphify.sh callflow   # Generate architecture diagrams
./run-graphify.sh hook       # Auto-rebuild on git commits
```

### Graphify Resources
- 📖 [Graphify Documentation](https://github.com/safishamsi/graphify)
- 🔍 [Full Command Reference](https://github.com/safishamsi/graphify#full-command-reference)
- 🏗️ [Architecture](https://github.com/safishamsi/graphify/blob/v8/docs/how-it-works.md)

---

## 🚀 Quick Start

### 1. Initialize the project
```bash
./automation/sdd/run-sdd.sh constitution
```

### 2. Generate knowledge graph
```bash
./automation/graphify/run-graphify.sh build
```

### 3. Set up AI agent integration
```bash
./automation/ponytail/install-ponytail.sh all
```

### 4. Start development with specs
```bash
./automation/sdd/run-sdd.sh specify
./automation/sdd/run-sdd.sh plan
./automation/sdd/run-sdd.sh tasks
./automation/sdd/run-sdd.sh implement
```

---

## 📁 Project Structure

```
.
├── src/                    # Source code
├── docs/                   # Documentation
├── tests/                  # Test suites
├── automation/
│   ├── sdd/               # Spec Kit helpers
│   ├── ponytail/          # Ponytail setup
│   └── graphify/          # Graphify automation
├── .specify/              # Spec Kit config
├── .graphifyignore        # Graphify ignore rules
├── .agents/               # AI agent configs
└── AGENTS.md              # Agent instructions
```

---

## 🔄 Development Workflow

1. **Write Specifications** - Use `/speckit.specify` to define what you want to build
   - Specs are auto-organized: `specs/YYYY/MonthName/`
2. **Create Plan** - Use `/speckit.plan` for technical implementation
3. **Generate Tasks** - Use `/speckit.tasks` for actionable steps
4. **Query Graph** - Use `graphify query` to understand your codebase
5. **Implement** - Use `/speckit.implement` with ponytail lazy principles
6. **Review** - Use `/ponytail-review` for code quality feedback

### Spec Organization

Feature specifications are automatically organized by year and month:
```
specs/
├── 2026/
│   ├── June/
│   │   ├── user-authentication.md
│   │   ├── payment-gateway.md
│   │   └── ...
│   └── July/
│       └── ...
└── 2027/
    └── ...
```

This structure enables:
- Easy historical tracking of specifications
- Quick filtering by date
- Archive management by year/month
- Clear audit trail of when features were defined

---

## 📚 Documentation

- [Spec Kit Official Docs](https://github.github.io/spec-kit/)
- [Spec-Driven Development Methodology](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Ponytail Benchmarks](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks)
- [Graphify Installation Guide](https://github.com/safishamsi/graphify#install)

---

## 🔧 System Requirements

- **OS**: macOS, Linux, or Windows
- **Python**: 3.10+ (3.12+ recommended)
- **Package Manager**: `uv` (recommended) or `pip`
- **Git**: For version control and hooks

### Install uv (recommended)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 📝 License

This project structure is provided as-is. Individual tools maintain their own licenses:
- Spec Kit: MIT
- Ponytail: MIT
- Graphify: MIT

---

## 🤝 Contributing

When contributing to this project:
1. Follow Spec-Driven Development principles
2. Run Ponytail review: `/ponytail-review`
3. Update knowledge graph: `./automation/graphify/run-graphify.sh update`
4. Keep README and specs synchronized

---

## 📞 Support

For issues with specific tools:
- **Spec Kit**: https://github.com/github/spec-kit/issues
- **Ponytail**: https://github.com/DietrichGebert/ponytail/issues
- **Graphify**: https://github.com/safishamsi/graphify/issues

---

**Generated**: [TIMESTAMP]
**Script Version**: 1.0
