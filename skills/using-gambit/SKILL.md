---
name: using-gambit
description: Establishes structured development workflows at session start. Routes tasks to the correct skill based on context. Use at the beginning of any session or when starting implementation, debugging, refactoring, testing, or planning work.
---

# Using Gambit

## Overview

Gambit provides structured development workflows using native Claude Code Tasks. This skill loads at session start and routes work to the correct skill.

**Core principle:** If a skill exists for your task, use it. Skills are mandatory, not optional.

**Announce at start:** "I'm using gambit to guide this session."

## Rigidity Level

MEDIUM FREEDOM - Always check for relevant skills before acting. Adapt skill selection to context, but never skip the check.

## Quick Reference

| Task Type | Skill | Slash Command |
|-----------|-------|---------------|
| New feature idea | brainstorming | `/gambit:brainstorming` |
| Create task plan | writing-plans | `/gambit:writing-plans` |
| Execute tasks | executing-plans | `/gambit:executing-plans` |
| Fix a bug | debugging | `/gambit:debugging` |
| Implement with TDD | test-driven-development | `/gambit:test-driven-development` |
| Improve code structure | refactoring | `/gambit:refactoring` |
| Review code | code-review | `/gambit:code-review` |
| Audit test quality | testing-quality | `/gambit:testing-quality` |
| Refine task details | task-refinement | `/gambit:task-refinement` |
| Verify completion | verification | `/gambit:verification` |
| Parallel investigations | parallel-agents | `/gambit:parallel-agents` |
| Create/modify skills | writing-skills | `/gambit:writing-skills` |
| Start feature branch | using-worktrees | `/gambit:using-worktrees` |
| Finish feature branch | finishing-branch | `/gambit:finishing-branch` |

## The Process

### Before Any Task

1. Read the user's request
2. Match to a skill using the Quick Reference table above
3. If a skill matches → load and follow it
4. Announce: "I'm using gambit:[skill-name] to handle this."

### Skill Selection Guide

**User describes a new idea or feature:**
1. `gambit:brainstorming` — refine into epic Task with immutable requirements
2. `gambit:writing-plans` — create Tasks with dependencies
3. `gambit:executing-plans` — work through Tasks one at a time

**User wants to fix a bug:**
1. `gambit:debugging` — systematic root cause analysis, tools first
2. `gambit:test-driven-development` — write failing test, then fix

**User wants to improve existing code:**
1. `gambit:refactoring` — test-preserving transforms in small steps
2. `gambit:code-review` — dispatch reviewer agent

**User wants to verify or audit:**
1. `gambit:verification` — evidence before completion claims
2. `gambit:testing-quality` — audit test effectiveness

**Multiple independent failures:**
1. `gambit:parallel-agents` — dispatch concurrent investigators

**Feature work lifecycle:**
1. `gambit:using-worktrees` — create isolated worktree
2. `gambit:finishing-branch` — merge, PR, or discard

### Core Principles

These apply across ALL gambit skills:

1. **One task then stop** — Execute one Task, present checkpoint, STOP for human review
2. **Tasks are source of truth** — Use `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`. Never track work mentally
3. **Evidence over assertions** — Run verification commands and show output before claiming done
4. **Small steps that stay green** — Tests pass between every change
5. **Immutable requirements** — Epic requirements don't change; Tasks adapt to reality

## Anti-patterns

**Don't:**
- Skip checking for skills ("This is simple, I'll just do it")
- Track work mentally instead of in Tasks
- Claim completion without running verification
- Write code before writing a failing test
- Execute multiple tasks without stopping for review
- Use shortened/wrong skill names (e.g., `gambit:brainstorm` instead of `gambit:brainstorming`)

**Do:**
- Check the Quick Reference table before every task
- Create Tasks for multi-step work
- Run verification commands and show output
- Follow the matched skill's process exactly
- Stop after each task for human review

## Common Excuses

| Excuse | Reality |
|--------|---------|
| "This doesn't need a skill" | Check the table. If it matches, use it |
| "I know the pattern" | Load the skill. Memory drifts, skills don't |
| "This is almost done" | Run verification first, then claim done |
| "Let me just fix this quickly" | Create a Task, follow the process |
| "Too simple for Tasks" | Simple tasks finish fast. Track them anyway |

## Integration

**Loaded by:** Session start hook (automatic)

**Calls:** All other gambit skills based on task context

**Task tools used:**
- `TaskCreate` — Create tasks with subject, description, activeForm
- `TaskUpdate` — Set status (in_progress/completed), add blockers via `addBlockedBy`
- `TaskList` — Find ready tasks (status=pending, blockedBy=[])
- `TaskGet` — Read full task details and success criteria
