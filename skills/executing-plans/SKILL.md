---
name: executing-plans
description: Use to execute Tasks one at a time - executes task, reviews learnings, then STOPS for user review before continuing
---

# Executing Plans

## Overview

Execute Tasks one at a time with mandatory human checkpoints. Load epic → Execute ONE task → Review learnings → STOP. User reviews implementation, then runs command again to continue.

**Core principle:** Epic requirements are immutable. Tasks adapt to reality. STOP after each task for human oversight.

**Announce at start:** "I'm using gambit:execute-plan to implement this task."

## Rigidity Level

LOW FREEDOM — Follow exact process: load epic, execute ONE task, review, STOP.

Do not skip checkpoints or verification. Epic requirements never change. Tasks adapt to discoveries.

## Quick Reference

| Step | Tool | Purpose |
|------|------|---------|
| **Check State** | `TaskList` | Find in-progress or ready tasks |
| **Load Epic** | `TaskGet` on epic | Read immutable requirements |
| **Start Task** | `TaskUpdate` status → in_progress | Mark task active |
| **Execute** | Follow steps in task description | TDD cycle, verify each step |
| **Complete Task** | `TaskUpdate` status → completed | After ALL steps done |
| **Review** | Re-read epic, check learnings | Adapt if needed |
| **STOP** | Present summary | User reviews, runs command again |

**Critical:** One task → STOP → User reviews → Next task. No batching. No continuing without checkpoint.

## When to Use

After `gambit:write-plan` creates epic with Tasks.

Symptoms:
- Epic Task exists with subtasks ready to execute
- Need to implement features iteratively
- Requirements clear, implementation adapts to reality

## The Process

### 0. Resumption Check (Every Invocation)

When this skill is invoked, first check state:

```
TaskList
```

**Fresh start:** No in-progress tasks → Step 1

**Resuming:**
- In-progress task exists → Resume at Step 2 (continue executing)
- Ready tasks exist, none in-progress → Step 2 (start next)
- All subtasks completed, epic open → Step 4 (final check)

**Do NOT ask "where did we leave off?"** — Task state tells you exactly where to resume.

### 1. Load Epic Context

Before executing ANY task, load the epic:

```
TaskGet on epic task
```

**Extract and keep in mind:**
- Requirements (IMMUTABLE — never water these down)
- Success criteria (validation checklist)
- Anti-patterns (FORBIDDEN shortcuts)
- Architecture approach

**Why:** Requirements prevent rationalizing shortcuts when blocked.

### 2. Execute Current Ready Task

```
TaskList                           # Find ready task
TaskUpdate taskId status=in_progress  # Start it
TaskGet taskId                     # Read full details
```

**Execute the steps in the task description:**

Task descriptions contain 4-8 bite-sized steps. Execute each:

1. Follow TDD cycle (test → fail → implement → pass → commit)
2. Run verifications exactly as specified
3. Use test-runner agent to avoid context pollution

**Pre-completion verification:**
- All steps in description completed?
- Tests passing?
- Changes committed?

```
TaskUpdate taskId status=completed  # Only when ALL steps done
```

### 2a. When Hitting Obstacles

**CRITICAL: Don't automatically try alternative approaches.**

When blocked:

1. **Re-read epic** — Check requirements and anti-patterns
2. **Check if workaround violates anti-patterns** — If yes, don't do it
3. **Research or ask** — Don't rationalize around blockers

**If solution would violate anti-pattern:**
```markdown
## Obstacle Encountered

**Blocker:** [What's blocking]
**Tempting workaround:** [What you could do]
**Why forbidden:** [Epic anti-pattern it violates]

**Options:**
1. Research proper solution
2. Ask user for guidance

**Recommendation:** [Your suggestion]
```

**Never water down requirements to "make it easier."**

### 3. Review and Adapt

After completing task:

**Review questions:**
1. What did we learn?
2. Discovered existing functionality, blockers, limitations?
3. Moving toward epic success criteria?
4. What's the logical next step?

**Re-read epic:**
```
TaskGet epic-task-id  # Keep requirements fresh
```

**Three cases:**

**A) Next task still valid** → Note for summary, proceed to STOP

**B) Next task now redundant:**
- Discovery makes planned work unnecessary
- Document why in summary
- Task can be marked completed with note, or left for user to decide

**C) Need to adjust approach:**
- Document learnings
- Explain in summary
- Let user decide how to adapt

### 4. STOP Checkpoint (Mandatory)

**Present summary to user:**

```markdown
## Task Complete — Checkpoint

### What Was Done
- [Summary of implementation]
- [Key decisions made]

### Learnings
- [Discoveries during implementation]
- [Anything that affects future tasks]

### Epic Progress
- [X/Y success criteria met]
- [What remains]

### Next Task
- [Title of next ready task]
- [Brief description]

### To Continue
Run `/gambit:execute-plan` to execute the next task.
```

**Why STOP is mandatory:**
- User can review implementation
- User can clear context if needed
- User can adjust next task based on learnings
- Prevents runaway execution without oversight

**Do NOT rationalize skipping:**
- "Good context loaded" → STOP anyway
- "Just one more quick task" → STOP anyway
- "User trusts me" → STOP anyway; one command ≠ blanket permission

### 5. Final Validation

When all subtasks completed and success criteria appear met:

1. **Run full verification** — All tests, all checks
2. **Review against epic** — Every requirement, every criterion
3. **Present completion summary:**

```markdown
## Epic Complete — Final Review

### Requirements Check
- [x] Requirement 1: [How satisfied]
- [x] Requirement 2: [How satisfied]

### Success Criteria
- [x] Criterion 1: [Evidence]
- [x] Criterion 2: [Evidence]

### Anti-patterns Avoided
- [x] Did not [forbidden thing 1]
- [x] Did not [forbidden thing 2]

### Ready for Finish
Use `/gambit:finish` to merge, create PR, or cleanup.
```

## Examples

### Bad: Continuing Without STOP

```
Completed Task 2 (auth middleware).
Task 3 (rate limiting) is ready.

Developer thinks: "Good context, I'll do Task 3 quickly..."
Continues to execute Task 3 without STOP.
```

**Why it fails:**
- User can't review Task 2 before Task 3 starts
- User can't clear context
- No checkpoint = no oversight

### Good: Proper STOP

```
Completed Task 2 (auth middleware).

## Task Complete — Checkpoint

### What Was Done
- Implemented JWT validation middleware
- Added token refresh handling

### Learnings
- Found existing session utils in lib/session.ts
- Can reuse for Task 3

### Epic Progress
- 2/4 success criteria met

### Next Task
- Task 3: Rate limiting
- Add rate limits to auth endpoints

### To Continue
Run `/gambit:execute-plan` to execute the next task.
```

Then STOP. Wait for user.

### Bad: Watering Down Requirements

```
Epic anti-pattern: "FORBIDDEN: Mock database in integration tests"

Developer hits complex DB setup, thinks: "I'll mock just for now..."
Adds mocks with TODO comment.
```

**Why it fails:** Violates explicit anti-pattern. "Later" never comes.

### Good: Handling Blockers

```
## Obstacle Encountered

**Blocker:** Test database setup is complex
**Tempting workaround:** Mock the database
**Why forbidden:** Epic explicitly forbids mocks for integration tests

**Options:**
1. Research existing test DB setup in codebase
2. Ask user about test infrastructure

**Recommendation:** Let me search for existing test DB patterns first.
```

## Anti-patterns

**Don't:**
- Continue past STOP checkpoint
- Execute multiple tasks without stopping
- Water down requirements when blocked
- Close task with steps incomplete
- Rationalize "just one more task"

**Do:**
- STOP after every task
- Re-read epic when blocked
- Complete ALL steps before closing task
- Document learnings in checkpoint
- Let user review before continuing

## Verification Checklist

Before completing each task:
- [ ] All steps in description executed
- [ ] Tests passing
- [ ] Changes committed
- [ ] Task actually done (not "mostly")

After completing each task:
- [ ] Reviewed learnings against epic
- [ ] Presented checkpoint summary
- [ ] STOPPED execution
- [ ] Waiting for user to continue

Before closing epic:
- [ ] ALL success criteria verified
- [ ] ALL anti-patterns avoided
- [ ] Full verification run

## Integration

**This skill is called by:**
- User via `/gambit:execute-plan`
- After `gambit:write-plan` creates tasks

**This skill calls:**
- `gambit:tdd` during implementation
- `gambit:verify` before claiming task complete
- `gambit:finish` after epic complete

**Workflow pattern:**
```
/gambit:execute-plan → Execute task → STOP
[User reviews, clears context if needed]
/gambit:execute-plan → Execute next task → STOP
[Repeat until epic complete]
/gambit:finish → Merge/PR/cleanup
```
