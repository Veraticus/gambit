# Gambit: Structured Development Workflows for Claude Code

## Vision

Gambit combines the polish of [obra/superpowers](https://github.com/obra/superpowers) with the rigor of [withzombies/hyperpowers](https://github.com/withzombies/hyperpowers), replacing external tooling (beads/bd) with **native Claude Code Tasks**.

**Core principles:**
- Native Tasks as the coordination primitive (no external CLI)
- One-task-then-stop discipline for human oversight
- Immutable requirements, adaptive implementation
- Evidence before assertions
- Small steps that stay green

## Architecture

```
gambit/
├── .claude-plugin          # Plugin manifest
├── README.md               # User-facing documentation
├── PLAN.md                 # This file
├── skills/
│   ├── using-gambit/       # Entry point, skill discovery
│   ├── brainstorming/      # Socratic design refinement
│   ├── writing-plans/      # Task creation with dependencies
│   ├── executing-plans/    # One-task-at-a-time execution
│   ├── using-worktrees/    # Git worktree + devenv setup
│   ├── finishing-branch/   # Merge/PR/discard workflow
│   ├── test-driven-dev/    # RED-GREEN-REFACTOR
│   ├── testing-quality/    # Anti-patterns, effectiveness
│   ├── verification/       # Evidence before completion
│   ├── refactoring/        # Safe incremental transforms
│   ├── debugging/          # Systematic root cause analysis
│   ├── code-review/        # Request and receive reviews
│   ├── parallel-agents/    # Concurrent investigation
│   ├── task-refinement/    # SRE-style corner case analysis
│   └── writing-skills/     # Meta: how to create skills
├── hooks/                  # Auto-activation, reminders
├── agents/                 # Specialized subagent definitions
└── docs/                   # Extended guides, examples
```

---

## Skills Specification

### 1. `using-gambit`

**Purpose:** Entry point loaded at session start. Ensures Claude checks for relevant skills before any task.

**Source:** Adapted from superpowers' `using-superpowers`

**Key behaviors:**
- List available skills mentally before responding
- Announce skill usage: "I'm using gambit:skill-name to..."
- Mandatory workflow enforcement (brainstorm → plan → execute → verify)
- Create Tasks for skill checklists, not mental tracking

**Slash command:** `/gambit` (shows available skills)

---

### 2. `brainstorming`

**Purpose:** Socratic design refinement before writing code. Tease out requirements through questions, not assumptions.

**Source:** superpowers' `brainstorming`

**Key behaviors:**
- Ask clarifying questions, don't assume
- Present design in digestible chunks for validation
- Explore alternatives before committing
- Output: Approved design document (markdown or in Task description)

**Slash command:** `/gambit:brainstorm`

**Triggers:** User describes a feature, asks to "add" or "implement" something

---

### 3. `writing-plans`

**Purpose:** Transform approved design into Tasks with dependencies. Each task is bite-sized (completable in one focused session).

**Source:** Hyperpowers' `writing-plans`, adapted for native Tasks

**Key behaviors:**
- Create epic Task with immutable requirements and success criteria
- Create subtasks with explicit dependencies via `addBlockedBy`
- Each task includes: exact file paths, complete code snippets, verification commands
- Assume zero codebase context — spell everything out
- DRY, YAGNI, TDD emphasis

**Slash command:** `/gambit:write-plan`

**Task structure:**
```
Epic Task (parent):
  - subject: "Feature: User Authentication"
  - description: Full requirements, success criteria, anti-patterns
  - status: in_progress (while subtasks execute)

Subtask 1:
  - subject: "Add password hashing utility"
  - description: Exact implementation steps, file paths, code, tests
  - blockedBy: [] (ready to start)

Subtask 2:
  - subject: "Create login endpoint"
  - description: ...
  - blockedBy: [subtask-1-id]
```

---

### 4. `executing-plans`

**Purpose:** Execute Tasks one at a time with mandatory human checkpoints.

**Source:** Hyperpowers' `executing-plans`, using native Tasks instead of bd

**Key behaviors:**
1. **Resumption check:** `TaskList` to find in-progress or ready tasks
2. **Load epic:** Read parent task for immutable requirements
3. **Execute ONE task:**
   - `TaskUpdate` status → in_progress
   - Follow steps exactly
   - Run verifications
   - `TaskUpdate` status → completed
4. **Review learnings:** What did we discover? Does next task need adjustment?
5. **Create/refine next task** if needed (tasks adapt, epic doesn't)
6. **STOP:** Present summary, wait for user to continue

**Slash command:** `/gambit:execute-plan`

**Critical rule:** Epic requirements are immutable. Tasks adapt to reality. Never water down requirements when blocked — stop and discuss.

---

### 5. `using-worktrees`

**Purpose:** Create isolated git worktrees with environment setup (devenv/nix aware).

**Source:** superpowers' `using-git-worktrees`, extended for devenv

**Key behaviors:**
1. **Directory selection:** Check `.worktrees/` → `worktrees/` → CLAUDE.md → ask
2. **Verify gitignored** before creating
3. **Create worktree:** `git worktree add <path> -b <branch>`
4. **Detect environment:**
   - If `devenv.nix`: Prompt for database strategy (share vs. isolate)
   - If `package.json`: `npm install`
   - If `go.mod`: `go mod download`
   - etc.
5. **Devenv-specific:**
   - Shared postgres (same $DATABASE_URL): Just `devenv shell`
   - Isolated postgres: Create new database, provide override instructions
6. **Verify clean baseline:** Run tests before starting work
7. **Report:** Full path, test status, ready message

**Slash command:** `/gambit:worktree`

**New for gambit:** Devenv awareness that superpowers lacks

---

### 6. `finishing-branch`

**Purpose:** Complete workflow when implementation done — verify, present options, cleanup.

**Source:** superpowers/hyperpowers' `finishing-a-development-branch`

**Key behaviors:**
1. **Verify all tasks completed:** `TaskList`, check epic subtasks
2. **Run tests:** Use test-runner agent to avoid context pollution
3. **Present exactly 4 options:**
   - Merge locally
   - Push and create PR
   - Keep as-is (handle later)
   - Discard (requires typed confirmation)
4. **Execute choice**
5. **Cleanup worktree** (except for PR and keep-as-is)

**Slash command:** `/gambit:finish`

---

### 7. `test-driven-dev`

**Purpose:** Enforce RED-GREEN-REFACTOR cycle. Tests fail before code exists.

**Source:** Both have this, hyperpowers is stricter

**Key behaviors:**
1. **RED:** Write failing test first. Watch it fail. Commit.
2. **GREEN:** Write minimal code to pass. Watch it pass. Commit.
3. **REFACTOR:** Clean up while green. Commit.
4. **Delete code written before tests** — no exceptions

**Slash command:** `/gambit:tdd`

**Triggers:** Any implementation task

---

### 8. `testing-quality`

**Purpose:** Prevent tautological tests, coverage gaming, weak assertions.

**Source:** Hyperpowers' `testing-anti-patterns` + `analyzing-test-effectiveness`

**Key behaviors:**
- Identify tests that test mock behavior, not real behavior
- Flag coverage gaming (tests that execute code but don't assert)
- Catch missing corner cases
- Prevent production code pollution with test-only methods

**Anti-patterns to catch:**
- `expect(mock).toHaveBeenCalled()` without verifying *what* was passed
- Tests that pass if you delete the implementation
- Mocking the thing you're testing
- "Happy path only" coverage

**Slash command:** `/gambit:test-quality`

---

### 9. `verification`

**Purpose:** Evidence before claiming completion. Run commands, show output.

**Source:** Both have `verification-before-completion`

**Key behaviors:**
- Before saying "done," "fixed," "passing" — run verification
- Show actual output, not claims
- If verification fails, task isn't complete
- Works with test-runner agent to keep context clean

**Triggers:** Any completion claim

---

### 10. `refactoring`

**Purpose:** Safe incremental transformations. Tests stay green between every change.

**Source:** Hyperpowers' `refactoring-safely`

**Key behaviors:**
1. Verify tests pass BEFORE starting
2. Make ONE small change
3. Run tests
4. Commit if green
5. Repeat

**Never:** Change multiple files then run tests. Big-bang refactoring.

**Slash command:** `/gambit:refactor`

---

### 11. `debugging`

**Purpose:** Systematic root cause analysis. Tools first, fixes second.

**Source:** Superpowers' `systematic-debugging` + hyperpowers' `root-cause-tracing`

**Key behaviors:**
1. **Reproduce:** Confirm the bug exists, get exact steps
2. **Investigate with tools:** Debugger, logs, internet search — before guessing
3. **Trace backward:** Find original trigger, not just symptom
4. **Hypothesize and test:** Form theory, verify with evidence
5. **Fix:** Only after root cause identified
6. **Regression test:** Write test that would have caught this

**Slash command:** `/gambit:debug`

---

### 12. `code-review`

**Purpose:** Request and receive code reviews systematically.

**Source:** Superpowers' `requesting-code-review` + `receiving-code-review`

**Key behaviors:**

**Requesting:**
- Self-review checklist before asking for review
- Provide context: what changed, why, how to test
- Flag areas of uncertainty

**Receiving:**
- Address all feedback (don't cherry-pick)
- Explain if disagreeing (don't silently ignore)
- Verify fixes don't break other things

**Slash command:** `/gambit:review`

---

### 13. `parallel-agents`

**Purpose:** Dispatch multiple subagents for independent investigations.

**Source:** Both have `dispatching-parallel-agents`

**Key behaviors:**
1. **Verify independence:** Problems must not share state
2. **Create Tasks** for each investigation
3. **Dispatch in single message** (parallel, not sequential)
4. **Monitor and collect** results
5. **Synthesize:** Combine findings, check for conflicts

**When to use:** 3+ independent failures, parallel test suites, multi-file investigation

**Slash command:** `/gambit:parallel`

---

### 14. `task-refinement`

**Purpose:** SRE-style corner case analysis before implementation.

**Source:** Hyperpowers' `sre-task-refinement`

**Key behaviors:**
- For each task, enumerate corner cases
- Consider: empty inputs, boundaries, concurrency, failures, permissions
- Update task description with handling for each
- Use stronger model (Opus) for analysis if available

**Slash command:** `/gambit:refine`

---

### 15. `writing-skills`

**Purpose:** Meta-skill for creating new gambit skills.

**Source:** Both have this

**Key behaviors:**
- TDD for documentation: test skill with subagent before finalizing
- Standard structure: overview, when to use, the process, examples, anti-patterns
- Rigidity level declaration (how strictly to follow)
- Integration notes (what calls this, what this calls)

**Slash command:** `/gambit:new-skill`

---

## Hooks

### `session-start`

Loads `using-gambit` skill automatically.

### `user-prompt-submit`

Analyzes prompt, suggests relevant skills before Claude responds.

### `post-tool-use`

Tracks file edits for context (TDD reminders, commit reminders).

### `stop`

Gentle reminders after response:
- TDD reminder when editing source without tests
- Verification reminder when claiming completion
- Commit reminder after multiple edits

---

## Agents

### `test-runner`

Runs tests/hooks/commits in isolated context, returns only summary + failures.
Uses Haiku for speed.

### `code-reviewer`

Reviews implementation against plan and standards.
Returns prioritized issues by severity.

### `codebase-investigator`

Explores codebase to answer questions about patterns, architecture, file locations.

### `internet-researcher`

Searches web for API docs, library usage, current best practices.

---

## Implementation Order

**Phase 1: Foundation**
1. `.claude-plugin` manifest
2. `using-gambit` (entry point)
3. `writing-plans` (Task creation)
4. `executing-plans` (Task execution)

**Phase 2: Quality**
5. `test-driven-dev`
6. `verification`
7. `testing-quality`

**Phase 3: Workflow**
8. `brainstorming`
9. `using-worktrees` (with devenv)
10. `finishing-branch`

**Phase 4: Advanced**
11. `debugging`
12. `refactoring`
13. `code-review`
14. `parallel-agents`
15. `task-refinement`

**Phase 5: Meta**
16. `writing-skills`
17. Hooks
18. Agents

---

## Design Guidelines for Skill Authors

### Structure

```markdown
---
name: skill-name
description: One-line description for skill discovery
---

# Skill Name

## Overview
What this skill does and core principle.

## When to Use
Triggers and symptoms that indicate this skill applies.

## The Process
Step-by-step, numbered, explicit.

## Examples
Good and bad examples with explanations.

## Anti-patterns
What NOT to do and why.

## Integration
- Called by: which skills invoke this
- Calls: which skills this invokes
```

### Rigidity Levels

- **LOW FREEDOM:** Follow exact process, no deviation
- **MEDIUM FREEDOM:** Follow structure, adapt details
- **HIGH FREEDOM:** Apply principles, adapt to situation

### Task Integration

- Use `TaskCreate` for multi-step work
- Use `TaskUpdate` to track progress
- Use `TaskList` to find next work
- Dependencies via `addBlockedBy` parameter
- Never track work mentally — Tasks are source of truth

---

## Success Criteria for Gambit

1. **No external tooling:** Everything works with native Claude Code
2. **Human oversight:** Clear checkpoints, no runaway execution
3. **Devenv-aware:** Worktrees work with nix/devenv projects
4. **Discoverable:** `/gambit` shows all skills, descriptions are clear
5. **Documented:** Every skill has examples and anti-patterns
6. **Tested:** Skills are tested with subagents before release
