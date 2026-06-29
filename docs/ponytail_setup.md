# Ponytail Setup and Reference Guide

Detailed guide and command instructions for **Ponytail**, an anti-overengineering and simplicity guard plugin.

**GitHub Repository:** [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

---

## Table of Contents

1. [🚀 Step-by-Step Installation](#-step-by-step-installation)
2. [⚙️ Configure Intensity Levels](#️-configure-intensity-levels)
3. [🛡️ Simplicity Validation & Commands](#️-simplicity-validation--commands)
4. [🐴 Core Philosophy (The Laziness Ladder)](#-core-philosophy-the-laziness-ladder)

---

## 🚀 Step-by-Step Installation

### Step 1: Register Ponytail with Copilot Marketplace
Copy and paste this command into either your **VS Code Terminal** or **GitHub Copilot Chat**:

```bash
copilot plugin marketplace add DietrichGebert/ponytail
```

### Step 2: Install Ponytail Plugin
Copy and paste this command to complete the installation:

```bash
copilot plugin install ponytail@ponytail
```

### Step 3: Verify the Plugin Installation
Confirm the installation succeeded and inspect the active skills list by executing:

```bash
copilot plugin list
```
*(Verify that `ponytail@ponytail (v4.8.x)` is shown as registered).*

---

## ⚙️ Configure Intensity Levels

### Step 4: Set the Simplicity Intensity Level
Configure the agent's laziness enforcement level by running the command in **GitHub Copilot Chat**:

```bash
/ponytail full
```
*(Options include: `lite` | `full` | `ultra` | `off`. The recommended level is `full`).*

---

## 🛡️ Simplicity Validation & Commands

### Step 5: Run Code Review and Repo Audits
Use the simplicity agent's validation commands in **GitHub Copilot Chat**:

- **Review recent diffs for over-engineering before staging:**
  ```bash
  /ponytail-review
  ```
- **Audit your entire repository for overly complex components:**
  ```bash
  /ponytail-audit
  ```
- **Harvest deferred shortcuts / debt:**
  ```bash
  /ponytail-debt
  ```
- **Show measured impact of ponytail simplification:**
  ```bash
  /ponytail-gain
  ```
- **Quick reference guide:**
  ```bash
  /ponytail-help
  ```

---

## 🐴 Core Philosophy: The Laziness Ladder

> [!IMPORTANT]
> The ladder runs *after* the agent understands the problem, not instead of it: it reads the code the change touches and traces the real flow before picking a rung. Lazy about the solution, never about reading.

Before proposing or writing any code block, the agent evaluates changes top-down using this ladder:

```
1. Does this need to exist?   → no: skip it (YAGNI)
2. Already in this codebase?  → reuse it, don't rewrite
3. Stdlib does it?            → use native standard library structures
4. Native platform feature?   → use native browser/host APIs (e.g. <input type="date">)
5. Installed dependency?      → reuse existing packages
6. One line?                  → keep it simple and small
7. Only then:                 → write the absolute minimum viable code that works
```
