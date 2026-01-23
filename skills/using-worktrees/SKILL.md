---
name: using-worktrees
description: Use when starting feature work that needs isolation - creates git worktrees with smart directory selection, safety verification, and devenv awareness
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Systematic directory selection + safety verification + environment setup = reliable isolation.

**Announce at start:** "I'm using gambit:worktree to set up an isolated workspace."

## Rigidity Level

MEDIUM FREEDOM - Follow directory selection priority exactly. Adapt environment setup to project type.

## Quick Reference

| Step | Action | If Blocked |
|------|--------|------------|
| 1 | Check existing directories | Use found directory |
| 2 | Check CLAUDE.md preference | Use specified location |
| 3 | Ask user for preference | Wait for answer |
| 4 | Verify directory is gitignored | Add to .gitignore if not |
| 5 | Create worktree | Report full path |
| 6 | Detect and run environment setup | Auto-detect from project files |
| 7 | Verify clean baseline (tests pass) | Report failures, ask to proceed |

## When to Use

- Starting feature work that needs isolation from main workspace
- Before executing implementation plans
- Working on multiple features simultaneously
- Experimenting without affecting main workspace

**Don't use for:**
- Quick fixes that don't need isolation
- Single-file changes
- When user explicitly wants to work in current directory

## The Process

### Step 1: Directory Selection

Follow this priority order:

**1a. Check Existing Directories**

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**If found:** Use that directory. If both exist, `.worktrees` wins.

**1b. Check CLAUDE.md**

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**If preference specified:** Use it without asking.

**1c. Ask User**

If no directory exists and no CLAUDE.md preference:

```
AskUserQuestion
  questions:
    - question: "No worktree directory found. Where should I create worktrees?"
      header: "Location"
      options:
        - label: ".worktrees/ (Recommended)"
          description: "Project-local, hidden directory"
        - label: "worktrees/"
          description: "Project-local, visible directory"
        - label: "~/.worktrees/<project>/"
          description: "Global location outside project"
      multiSelect: false
```

### Step 2: Safety Verification

**For project-local directories (.worktrees or worktrees):**

**MUST verify directory is ignored before creating worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:**

1. Add appropriate line to .gitignore
2. Commit the change
3. Proceed with worktree creation

```bash
echo ".worktrees/" >> .gitignore
git add .gitignore
git commit -m "chore: add .worktrees to gitignore"
```

**Why critical:** Prevents accidentally committing worktree contents to repository.

**For global directory (~/.worktrees/):**

No .gitignore verification needed - outside project entirely.

### Step 3: Create Worktree

```bash
# Detect project name
project=$(basename "$(git rev-parse --show-toplevel)")

# Determine full path based on location choice
# For .worktrees:
path=".worktrees/$BRANCH_NAME"

# For global:
path="$HOME/.worktrees/$project/$BRANCH_NAME"

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
```

### Step 4: Environment Setup

**Auto-detect and run appropriate setup based on project files:**

#### Standard Projects

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

#### Devenv/Nix Projects (Gambit-specific)

**If `devenv.nix` or `flake.nix` exists:**

```bash
# Check for devenv
if [ -f devenv.nix ] || [ -f .envrc ]; then
    # Devenv detected
fi
```

**Database Strategy:**

Present options to user:

```
AskUserQuestion
  questions:
    - question: "This project uses devenv with a database. How should the worktree handle it?"
      header: "Database"
      options:
        - label: "Share database (Recommended)"
          description: "Use same $DATABASE_URL as main. Faster setup, shared data."
        - label: "Isolated database"
          description: "Create new database. Clean slate, but requires migration."
      multiSelect: false
```

**For shared database:**
```bash
# Just enter devenv shell - uses same postgres
cd "$path"
direnv allow  # If using direnv
# Or: devenv shell
```

**For isolated database:**
```bash
# Create new database
createdb "${project}_${BRANCH_NAME}"

# Provide override instructions
echo "To use isolated database:"
echo "export DATABASE_URL=postgres://localhost/${project}_${BRANCH_NAME}"

# Run migrations
# (project-specific command)
```

### Step 5: Verify Clean Baseline

**Run tests to ensure worktree starts clean:**

```bash
# Use test-runner agent for clean output
Task
  subagent_type: "hyperpowers:test-runner"
  prompt: "Run: npm test"  # or appropriate test command
```

**If tests fail:**
```
Tests failing (N failures) in fresh worktree.

[Show failures]

These failures exist in the base branch. Options:
1. Proceed anyway (failures are known/expected)
2. Investigate before proceeding
3. Cancel worktree creation

Which option?
```

**If tests pass:** Continue to report.

### Step 6: Report Ready

```
Worktree ready at <full-path>
Branch: <branch-name>
Tests: <N> passing, 0 failures
Environment: <devenv/npm/cargo/etc.>

Ready to implement <feature-name>
```

## Quick Reference Table

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md → Ask user |
| Directory not ignored | Add to .gitignore + commit |
| Tests fail during baseline | Report failures + ask |
| No package.json/Cargo.toml | Skip dependency install |
| devenv.nix exists | Ask about database strategy |

## Examples

### Good: Complete Workflow

```
You: "I'm using gambit:worktree to set up an isolated workspace."

[Check .worktrees/ - exists]
[Verify ignored - git check-ignore confirms]
[Create worktree: git worktree add .worktrees/auth -b feature/auth]
[Detect devenv.nix - ask about database]
User selects: Share database
[Run direnv allow]
[Run tests via test-runner agent - 47 passing]

Worktree ready at /Users/dev/myproject/.worktrees/auth
Branch: feature/auth
Tests: 47 passing, 0 failures
Environment: devenv (shared database)

Ready to implement auth feature
```

### Bad: Skip Ignore Verification

```
[Check .worktrees/ - doesn't exist]
[Create .worktrees/feature directly without checking ignore]

# Later...
git status
# Shows all worktree files as untracked!
# Pollutes git status, risk of accidental commit
```

**Why it fails:**
- Worktree contents get tracked
- Pollutes git status
- Risk of committing worktree to repo

### Bad: Proceed with Failing Tests

```
[Create worktree]
[Run tests - 3 failures]
[Proceed without asking]

# Later...
# New test failures appear
# Can't tell if they're from your changes or pre-existing
```

**Why it fails:**
- Can't distinguish new bugs from pre-existing
- Wastes time debugging inherited failures
- Uncertain baseline

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Skip ignore verification | Worktree contents tracked | Always `git check-ignore` first |
| Assume directory location | Inconsistency, violates conventions | Follow priority: existing > CLAUDE.md > ask |
| Proceed with failing tests | Can't distinguish new vs old failures | Report failures, get permission |
| Hardcode setup commands | Breaks on different project types | Auto-detect from project files |
| Skip devenv detection | Missing environment, broken builds | Check for devenv.nix/flake.nix |

## Anti-patterns

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Skip CLAUDE.md check
- Assume database strategy for devenv projects

**Always:**
- Follow directory priority: existing > CLAUDE.md > ask
- Verify directory is ignored for project-local
- Auto-detect and run project setup
- Ask about database strategy for devenv projects
- Verify clean test baseline
- Report full path and test status

## Verification Checklist

Before reporting ready:

- [ ] Checked existing directories (.worktrees, worktrees)
- [ ] Checked CLAUDE.md for preference
- [ ] Asked user if no existing preference
- [ ] Verified directory is gitignored (project-local only)
- [ ] Added to .gitignore if needed
- [ ] Created worktree with branch
- [ ] Detected environment type (devenv/npm/cargo/etc.)
- [ ] Asked about database strategy (devenv only)
- [ ] Ran environment setup
- [ ] Verified tests pass (or got permission to proceed)
- [ ] Reported full path, branch, test status

## Integration

**This skill is called by:**
- `gambit:brainstorm` (after design approved)
- Any skill needing isolated workspace

**This skill pairs with:**
- `gambit:finish` - REQUIRED for cleanup after work complete
- `gambit:execute-plan` - Work happens in this worktree

**Workflow:**
```
gambit:brainstorm
    → Design approved
gambit:worktree
    → Create isolated workspace
    → Environment setup
gambit:execute-plan
    → Implement in worktree
gambit:finish
    → Merge/PR/cleanup worktree
```
