.PHONY: help setup scaffold init-sdd graph query ponytail clean

help:
	@echo "Automation Makefile"
	@echo ""
	@echo "Setup targets:"
	@echo "  make setup          - Full project setup"
	@echo "  make scaffold       - Initialize scaffold"
	@echo ""
	@echo "Development targets:"
	@echo "  make init-sdd       - Initialize Spec Kit"
	@echo "  make graph          - Generate knowledge graph"
	@echo "  make query QUERY    - Query knowledge graph"
	@echo "  make ponytail       - Install Ponytail"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove generated files"

setup: scaffold init-sdd graph ponytail
	@echo "✓ Project setup complete!"

scaffold:
	@echo "Setting up project scaffold..."
	mkdir -p src docs tests automation/.{sdd,ponytail,graphify}

init-sdd:
	@echo "Initializing Spec-Driven Development..."
	./automation/sdd/run-sdd.sh constitution

graph:
	@echo "Generating knowledge graph..."
	./automation/graphify/run-graphify.sh build

query:
	@test -n "$(QUERY)" || (echo "Usage: make query QUERY='your question'" && exit 1)
	./automation/graphify/run-graphify.sh query "$(QUERY)"

ponytail:
	@echo "Setting up Ponytail..."
	./automation/ponytail/install-ponytail.sh all

clean:
	@echo "Cleaning generated files..."
	rm -rf graphify-out/ .pytest_cache/ __pycache__/ *.pyc
	@echo "✓ Clean complete"

# Knowledge Graph Management
.PHONY: graph-update graph-watch graph-status graph-clean

graph-update:
	@echo "🔄 Updating knowledge graph incrementally..."
	@node /Users/girish/.copilot/skills/understand/update-knowledge-graph.mjs --repo . --incremental

graph-watch:
	@echo "👀 Watching for changes and updating graph..."
	@while true; do \
		inotifywait -r -e modify,create,delete src/ 2>/dev/null || sleep 5; \
		$(MAKE) graph-update; \
	done

graph-status:
	@if [ -f .understand-anything/meta.json ]; then \
		echo "✓ Graph exists"; \
		cat .understand-anything/meta.json | jq '.'; \
	else \
		echo "✗ No knowledge graph found"; \
	fi

graph-clean:
	@echo "🧹 Cleaning up old update trash..."
	@find .understand-anything -type d -name '.trash-*' -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"
