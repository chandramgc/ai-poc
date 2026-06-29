# Project AI Automation Control Center

Consolidated quick-reference index and orchestration roadmap for the main AI agent and automation frameworks configured in this workspace.

---

## Table of Contents

1. [🧭 Setup Roadmap & Summary](#-setup-roadmap--summary)
2. [🧠 1. Understand-Anything (Codebase Visualizer)](#-1-understand-anything-codebase-visualizer)
    - [GitHub Repository Reference](#understand-anything-github-repository-reference)
    - [Step 1: Install Copilot Plugin](#understand-anything-step-1-install-copilot-plugin)
    - [Step 2: Generate Initial Graph](#understand-anything-step-2-generate-initial-graph)
    - [Step 3: Run Web Dashboard](#understand-anything-step-3-run-web-dashboard)
    - [Step 4: Enable Git Hook for Auto-Updates](#understand-anything-step-4-enable-git-hook-for-auto-updates)
    - [Step 5: Makefile Commands](#understand-anything-step-5-makefile-commands)
    - [Detailed Setup Guide](#understand-anything-detailed-setup-guide)
3. [🐴 2. Ponytail (Anti-Overengineering Guard)](#-2-ponytail-anti-overengineering-guard)
    - [GitHub Repository Reference](#ponytail-github-repository-reference)
    - [Step 1: Register Plugin with Marketplace](#ponytail-step-1-register-plugin-with-marketplace)
    - [Step 2: Install Plugin](#ponytail-step-2-install-plugin)
    - [Step 3: Verify Plugin](#ponytail-step-3-verify-plugin)
    - [Step 4: Set Simplicity Level](#ponytail-step-4-set-simplicity-level)
    - [Step 5: Code Review & Audits](#ponytail-step-5-code-review--audits)
    - [Detailed Setup Guide](#ponytail-detailed-setup-guide)
4. [🌱 3. Spec-Driven Development (Spec Kit)](#-3-spec-driven-development-spec-kit)
    - [GitHub Repository Reference](#spec-kit-github-repository-reference)
    - [Step 1: Install Specify CLI](#spec-kit-step-1-install-specify-cli)
    - [Step 2: Initialize Project](#spec-kit-step-2-initialize-project)
    - [Step 3: Establish Principles (Constitution)](#spec-kit-step-3-establish-principles-constitution)
    - [Step 4: Create Feature Specification](#spec-kit-step-4-create-feature-specification)
    - [Step 5: Formulate Implementation Plan](#spec-kit-step-5-formulate-implementation-plan)
    - [Step 6: Generate Tasks](#spec-kit-step-6-generate-tasks)
    - [Step 7: Build & Implement](#spec-kit-step-7-build--implement)
    - [Step 8: Converge Project State](#spec-kit-step-8-converge-project-state)
    - [Detailed Setup Guide](#spec-kit-detailed-setup-guide)

---

## 🧭 Setup Roadmap & Summary

> [!IMPORTANT]
> The workspace rules dictate that **Spec-Driven Development (SDD)** must be followed first. All changes must be planned via specs, and all implementations must be kept minimal and clean using the **Ponytail** rungs.

| Framework | Primary Purpose | Scope | Key Interface |
|:---|:---|:---|:---|
| **Understand-Anything** | Codebase mapping, visualization, & context window optimization | Entire Repository | `/understand-dashboard` |
| **Ponytail** | Enforces the 7-step Simplicity / YAGNI ladder in code proposals | Incremental Changes | `/ponytail-review` |
| **Spec Kit** | Requirement specs, tech planning, tasks, and quality verification | Feature Lifecycle | `/speckit.*` commands |

---

## 🧠 1. Understand-Anything (Codebase Visualizer)

### Understand-Anything GitHub Repository Reference
- **GitHub Repository Link:** [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)

### Understand-Anything Step 1: Install Copilot Plugin
Copy and paste this command into **GitHub Copilot Chat** in VS Code:
```bash
copilot plugin install Egonex-AI/Understand-Anything:understand-anything-plugin
```

> [!TIP]
> If the Marketplace layout is not supported by your client version, open your **VS Code Terminal** and execute:
> ```bash
> curl -sSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash -s -- vscode
> ```

### Understand-Anything Step 2: Generate Initial Graph
Execute the pre-flight checks and scan your codebase by typing this in **GitHub Copilot Chat**:
```bash
/understand
```

### Understand-Anything Step 3: Run Web Dashboard
Launch the force-directed interactive chart client from **GitHub Copilot Chat**:
```bash
/understand-dashboard
```
Open `http://127.0.0.1:5173` in your browser.

### Understand-Anything Step 4: Enable Git Hook for Auto-Updates
Write the update hook script to `.git/hooks/post-commit` and run this in your **VS Code Terminal**:
```bash
chmod +x /Users/girish/MyDrive/Workspace/ai-poc/.git/hooks/post-commit
```

### Understand-Anything Step 5: Makefile Commands
Run these commands in your **VS Code Terminal**:
- Update graph manually: `make graph-update`
- Check graph metadata: `make graph-status`
- Clean trash directories: `make graph-clean`

### Understand-Anything Detailed Setup Guide
For configurations, ignore rules, scan output files, and troubleshooting steps, read [understand_anything_setup.md](understand_anything_setup.md).

---

## 🐴 2. Ponytail (Anti-Overengineering Guard)

### Ponytail GitHub Repository Reference
- **GitHub Repository Link:** [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

### Ponytail Step 1: Register Plugin with Marketplace
Register the ponytail package inside your **VS Code Terminal** or **GitHub Copilot Chat**:
```bash
copilot plugin marketplace add DietrichGebert/ponytail
```

### Ponytail Step 2: Install Plugin
Execute the install instruction inside your **VS Code Terminal** or **GitHub Copilot Chat**:
```bash
copilot plugin install ponytail@ponytail
```

### Ponytail Step 3: Verify Plugin
Confirm successful registration:
```bash
copilot plugin list
```

### Ponytail Step 4: Set Simplicity Level
Configure the agent laziness level in **GitHub Copilot Chat**:
```bash
/ponytail full
```

### Ponytail Step 5: Code Review & Audits
Use these validation commands in **GitHub Copilot Chat**:
- Review diff before staging: `/ponytail-review`
- Audit repo for complexity: `/ponytail-audit`

### Ponytail Detailed Setup Guide
For details on the Laziness Ladder and helper commands, read [ponytail_setup.md](ponytail_setup.md).

---

## 🌱 3. Spec-Driven Development (Spec Kit)

### Spec Kit GitHub Repository Reference
- **GitHub Repository Link:** [github/spec-kit](https://github.com/github/spec-kit)

### Spec Kit Step 1: Install Specify CLI
Install the tool globally using `uv` in your **VS Code Terminal**:
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

### Spec Kit Step 2: Initialize Project
Configure workspace context in your **VS Code Terminal**:
```bash
specify init . --integration copilot --script sh
```

### Spec Kit Step 3: Establish Principles (Constitution)
Define guiding guidelines in **GitHub Copilot Chat**:
```bash
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

> [!CAUTION]
> **Mandatory Jira validation is active:** Spec Kit commands require a valid Jira key (e.g. `JIRA-1234`). If a Jira number is not present, you will be prompted to provide it before any specs, plans, or tasks are written.

### Spec Kit Step 4: Create Feature Specification
Specify requirements in **GitHub Copilot Chat**:
```bash
/speckit.specify Build a dashboard page that shows code metrics
```
*Note: Specs are chronological and written under `specs/YYYY/Month/` folders automatically.*

### Spec Kit Step 5: Formulate Implementation Plan
State tech choices in **GitHub Copilot Chat**:
```bash
/speckit.plan Use React with typescript, vanilla CSS, and fetch from API
```

### Spec Kit Step 6: Generate Tasks
Create structured task lists in **GitHub Copilot Chat**:
```bash
/speckit.tasks
```

### Spec Kit Step 7: Build & Implement
Execute the implementation tasks in **GitHub Copilot Chat**:
```bash
/speckit.implement
```

### Spec Kit Step 8: Converge Project State
Converge state and discover remaining tasks in **GitHub Copilot Chat**:
```bash
/speckit.converge
```

### Spec Kit Detailed Setup Guide
For details on customized templates, presets, and quality checklist runs, read [spec_kit_setup.md](spec_kit_setup.md).
