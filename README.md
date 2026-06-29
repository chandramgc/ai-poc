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
├── docs/
│   └── decisions/          # Architecture Decision Records (ADRs)
├── tests/                  # Test suites
├── automation/
│   ├── sdd/               # Spec Kit helpers
│   ├── ponytail/          # Ponytail setup
│   └── graphify/          # Graphify automation
├── .specify/              # Spec Kit config
├── .graphifyignore        # Graphify ignore rules
└── AGENTS.md              # Agent instructions
```

---

## 🔄 Development Workflow

1. **Write Specifications** - Use `/speckit.specify` to define what you want to build
   - Specs are auto-organized: `specs/YYYY/MonthName/`
2. **Clarify Gaps** - Use `/speckit.clarify` to identify missing details or ambiguities
3. **Review Spec** - Human review gate to ensure alignment
4. **Create Plan** - Use `/speckit.plan` for technical implementation design
5. **Review Plan** - Human review gate for architectural approval
6. **Quality Checklist** - Use `/speckit.checklist` to generate verification items
7. **Generate Tasks** - Use `/speckit.tasks` for actionable implementation steps
8. **Review Tasks** - Human review gate before beginning implementation
9. **Analyze Consistency** - Use `/speckit.analyze` to verify artifact consistency
10. **Implement** - Use `/speckit.implement` with ponytail lazy principles
11. **Query Graph** - Use `graphify query` to understand your codebase
12. **Review** - Use `/ponytail-review` for code quality feedback

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
- **SonarQube**: Self-hosted for quality gate validation
- **OpenTelemetry**: For observability instrumentation

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
2. Follow Conventional Commits format (`feat|fix|refactor|chore|docs|test(scope): description`)
3. Document architectural decisions as ADRs in `docs/decisions/`
4. Run Ponytail review: `/ponytail-review`
5. Update knowledge graph: `./automation/graphify/run-graphify.sh update`
6. Keep README and specs synchronized

---

## 📞 Support

For issues with specific tools:
- **Spec Kit**: https://github.com/github/spec-kit/issues
- **Ponytail**: https://github.com/DietrichGebert/ponytail/issues
- **Graphify**: https://github.com/safishamsi/graphify/issues

---

**Generated**: 2026-06-29 07:22:00
**Script Version**: 2.0
