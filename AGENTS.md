# AGENTS.md - AI Agent Configuration

This project uses three major automation frameworks:

## 🌱 Spec Kit (SDD)

Commands available in your AI agent:
- `/speckit.constitution` - Define project principles
- `/speckit.specify` - Write feature specifications
- `/speckit.plan` - Create implementation plans
- `/speckit.tasks` - Generate actionable tasks
- `/speckit.implement` - Execute implementation
- `/speckit.analyze` - Check artifact consistency

Reference: https://github.github.io/spec-kit/reference/overview.html

## 🐴 Ponytail

The laziness ladder before writing code:
1. Does this need to exist? → No: skip it (YAGNI)
2. Already in this codebase? → Reuse it
3. Stdlib does it? → Use it
4. Native platform feature? → Use it
5. Installed dependency? → Use it
6. One line? → One line
7. Only then: the minimum that works

Commands:
- `/ponytail [lite|full|ultra|off]` - Set intensity level
- `/ponytail-review` - Review diff for over-engineering
- `/ponytail-audit` - Audit repo for over-engineering
- `/ponytail-debt` - Harvest deferred shortcuts
- `/ponytail-gain` - Show measured impact
- `/ponytail-help` - Quick reference

Reference: https://github.com/DietrichGebert/ponytail

## 🧠 Graphify

Query your project's knowledge graph:
```
/graphify .                              # Build graph
/graphify --update                       # Update changes only
/graphify query "your question"          # Query graph
/graphify export callflow-html           # Architecture diagrams
```

Reference: https://github.com/safishamsi/graphify

## Development Workflow

1. **Plan** → Use Spec Kit commands to define and plan
2. **Discover** → Use Graphify to understand codebase
3. **Build** → Use Ponytail to build minimal, clean code
4. **Review** → Use Ponytail-review for quality checks
5. **Analyze** → Use Spec Kit analyze for consistency

## Key Files

- `.specify/` - Spec Kit project files
- `.graphifyignore` - Files excluded from knowledge graph
- `automation/` - Helper scripts for all tools
- `Makefile` - Quick automation commands
