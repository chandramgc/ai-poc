# Spec Kit Setup and Reference Guide

Detailed guide and command instructions for **Spec Kit (Spec-Driven Development)**, an executable feature specification and implementation planning workflow.

**GitHub Repository:** [github/spec-kit](https://github.com/github/spec-kit)

---

## Table of Contents

1. [🚀 Step-by-Step Installation](#-step-by-step-installation)
2. [🌱 The SDD Iteration Cycle](#-the-sdd-iteration-cycle)
3. [📋 Optional & Quality Gates Commands](#-optional--quality-gates-commands)
4. [⚠️ Rules & Configuration Restrictions](#-rules--configuration-restrictions)

---

## 🚀 Step-by-Step Installation

### Step 1: Install Specify CLI Tool
Run the following command in your **VS Code Terminal** to install the `specify-cli` command line utility (requires [uv](https://docs.astral.sh/uv/) package manager):

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

### Step 2: Initialize Spec Kit for the Project
Initialize Spec Kit inside your root workspace folder and bind it to GitHub Copilot by running this in the **VS Code Terminal**:

```bash
specify init . --integration copilot --script sh
```
This sets up project configurations, baseline constitution templates, and `/speckit.*` commands in your Copilot workspace context.

---

## 🌱 The SDD Iteration Cycle

To build features using Spec-Driven Development, run the following commands sequentially in **GitHub Copilot Chat**:

### Step 3: Establish Project Principles (Constitution)
Define high-level architecture guidelines, coding rules, and testing standards:

```bash
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

### Step 4: Create the Feature Specification
Detail the requirements and expected outcomes (the *what* and *why*) in plain language:

```bash
/speckit.specify Build a dashboard page that shows code metrics
```

### Step 5: Formulate the Implementation Plan
Introduce technology stack, architecture layout, and file boundaries:

```bash
/speckit.plan Use React with typescript, vanilla CSS, and fetch from API
```

### Step 6: Generate Actionable Task Lists
Construct an ordered TODO list of components and dependency tasks:

```bash
/speckit.tasks
```

### Step 7: Build and Execute Implementation
Command the agent to write the actual code files following the generated task lists:

```bash
/speckit.implement
```

### Step 8: Assess and Converge Project State
Assess code completeness against specifications and plans, and automatically append missing items as trailing tasks:

```bash
/speckit.converge
```

---

## 📋 Optional & Quality Gates Commands

Run these commands in **GitHub Copilot Chat** to improve specification alignment and check consistency:
- **Clarify ambiguous specifications (pre-planning):**
  ```bash
  /speckit.clarify
  ```
- **Cross-artifact consistency and quality check (post-planning, pre-implementation):**
  ```bash
  /speckit.analyze
  ```
- **Generate validation checklists:**
  ```bash
  /speckit.checklist
  ```

---

## ⚠️ Rules & Configuration Restrictions

> [!IMPORTANT]
> **Mandatory Jira validation is active:** A valid Jira issue key/number (e.g. `JIRA-1234`) is strictly required before writing any specifications, starting any plans, or initiating any codebase changes.
> The agent **MUST** prompt the user to provide it and **REFUSE** to proceed or write any files until the Jira key is supplied. The Jira key must be explicitly recorded at the start of the specification document.

> [!IMPORTANT]
> **Date-Scoped Specification Pathing:** Specifications must be organized under chronological subdirectories within the `specs/` folder: `specs/YYYY/Month/` (e.g. `specs/2026/June/`).
