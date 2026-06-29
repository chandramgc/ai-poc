# Understand-Anything Setup & Reference Guide

Detailed guide and command instructions for **Understand-Anything**, the codebase visualizer and interactive knowledge graph framework.

**GitHub Repository:** [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)

---

## Table of Contents

1. [🧠 Overview](#-overview)
2. [📋 Prerequisites](#-prerequisites)
3. [🚀 Step-by-Step Installation](#-step-by-step-installation)
4. [🔍 Generate Initial Graph](#-generate-initial-graph)
5. [🖥️ Launch the Web Dashboard](#️-launch-the-web-dashboard)
6. [🔄 Configure Automatic Updates (Git Hook)](#-configure-automatic-updates-git-hook)
7. [⚙️ Makefile Automation Targets](#️-makefile-automation-targets)
8. [🐛 Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 🧠 Overview

**Understand-Anything** parses programming structures (classes, interfaces, functions, dependencies, configuration, and documentation) in your codebase to build an interactive force-directed graph. 

### Current Scan Statistics
- **Total Nodes:** 15,869 elements (files, classes, functions, configs, and docs)
- **Total Edges:** 14,099 relationships (containment hierarchy, imports, function calls, and annotations)
- **Architectural Layers:** 9 key layers detected (Entry Point, HTTP/REST, Service, Data, Config, Testing, Infrastructure, Docs, and Utilities)
- **Learning Tour:** 12-step guided interactive walkthrough of the architecture

---

## 📋 Prerequisites

Before starting, verify that your local environment has the following software installed:
- **Node.js** (v18.0.0 or higher)
- **npm** (v8.0.0 or higher)
- **pnpm** (v8.0.0 or higher)
- **Git**

Run validation commands in your VS Code Terminal:
```bash
node --version
npm --version
pnpm --version
git --version
```

---

## 🚀 Step-by-Step Installation

### Step 1: Install the Copilot Plugin
Copy and paste the command below into your **GitHub Copilot Chat** inside VS Code:

```bash
copilot plugin install Egonex-AI/Understand-Anything:understand-anything-plugin
```

> [!TIP]
> If the extension fails to install because the marketplace format isn't supported, run the following command directly in your **VS Code Terminal**:
> ```bash
> curl -sSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash -s -- vscode
> ```

Once installed, **restart VS Code** to register the new workspace skills.

---

## 🔍 Generate Initial Graph

### Step 2: Initialize Analysis
Copy and paste this command into **GitHub Copilot Chat** to scan the repository, create `.understandignore`, and extract nodes:

```bash
/understand
```

---

## 🖥️ Launch the Web Dashboard

### Step 3: Run Interactive Dashboard
Launch the visualization client by typing this in **GitHub Copilot Chat**:

```bash
/understand-dashboard
```

Once running, navigate to `http://127.0.0.1:5173` in your browser to inspect codebase nodes, track layers, search components, and take the 12-step guided onboarding tour.

---

## 🔄 Configure Automatic Updates (Git Hook)

### Step 4: Enable Git Hook for Auto-Updates
Set up a git post-commit hook so the knowledge graph is updated incrementally in the background whenever you commit changes.

1. Write the following code to `/Users/girish/MyDrive/Workspace/ai-poc/.git/hooks/post-commit`:

```bash
#!/bin/bash
# Auto-update knowledge graph after commits

REPO_ROOT="$(git rev-parse --show-toplevel)"
GRAPH_DIR="$REPO_ROOT/.understand-anything"
GRAPH_FILE="$GRAPH_DIR/knowledge-graph.json"
LOG_FILE="$GRAPH_DIR/.update.log"

# Only run if knowledge graph exists
if [ ! -f "$GRAPH_FILE" ]; then
    exit 0
fi

# Create log directory if needed
mkdir -p "$GRAPH_DIR"

echo "[$(date)] Starting incremental update..." >> "$LOG_FILE"

# Run understand with --update flag in background to avoid blocking git commits
SKILL_DIR="$HOME/.copilot/skills/understand"
if [ -d "$SKILL_DIR" ]; then
    cd "$REPO_ROOT"
    (
        sleep 1  # Delay slightly to let the commit finalize
        node "$SKILL_DIR/update-knowledge-graph.mjs" --repo "$REPO_ROOT" --incremental >> "$LOG_FILE" 2>&1
        echo "[$(date)] Update complete" >> "$LOG_FILE"
    ) &
fi

exit 0
```

2. Make the hook script executable by running this in your **VS Code Terminal**:

```bash
chmod +x /Users/girish/MyDrive/Workspace/ai-poc/.git/hooks/post-commit
```

---

## ⚙️ Makefile Automation Targets

### Step 5: Configure Makefile Shortcuts
Verify that the following targets are present in your workspace [Makefile](file:///Users/girish/MyDrive/Workspace/ai-poc/Makefile) to trigger updates or check logs quickly:

```makefile
# Run this command in VS Code Terminal to update the graph manually
graph-update:
	@echo "🔄 Updating knowledge graph incrementally..."
	@node /Users/girish/.copilot/skills/understand/update-knowledge-graph.mjs --repo . --incremental

# Run this command in VS Code Terminal to verify graph existence and read metadata
graph-status:
	@if [ -f .understand-anything/meta.json ]; then \
		echo "✓ Graph exists"; \
		cat .understand-anything/meta.json | jq '.'; \
	else \
		echo "✗ No knowledge graph found"; \
	fi

# Run this command in VS Code Terminal to clear internal scan cache files
graph-clean:
	@echo "🧹 Cleaning up old update trash..."
	@find .understand-anything -type d -name '.trash-*' -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"
```

---

## 🐛 Troubleshooting & FAQ

### Problem: Git hook not running after commit
> [!WARNING]
> If changes don't show on the graph, check that the hook script is executable.

**Solution:**
1. Check that hook file exists and is executable:
   ```bash
   ls -l .git/hooks/post-commit
   ```
2. If not executable, fix it:
   ```bash
   chmod +x .git/hooks/post-commit
   ```
3. Check update logs:
   ```bash
   tail -20 .understand-anything/.update.log
   ```

### Problem: Dashboard won't start or port 5173 is in use
**Solution:**
1. In browser, force refresh: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows).
2. Kill any conflicting node process:
   ```bash
   lsof -i :5173 | grep node | awk '{print $2}' | xargs kill -9
   ```
3. Restart via Copilot Chat using `/understand-dashboard`.

### FAQ: How often does the graph update?
The graph updates automatically after every Git commit using the background post-commit hook. It processes incrementally (only scanning changed files), which usually completes in 1-2 minutes without blocking your terminal.
