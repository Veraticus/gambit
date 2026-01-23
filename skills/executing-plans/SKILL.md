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
| **Load Epic** | `TaskGet taskId` on epic | Read immutable requirements |
| **Start Task** | `TaskUpdate taskId status="in_progress"` | Mark task active |
| **Execute** | Follow steps in task description | TDD cycle, verify each step |
| **Complete Task** | `TaskUpdate taskId status="completed"` | After ALL steps done |
| **Review** | `TaskGet` on epic | Check learnings against requirements |
| **STOP** | Present summary | User reviews, runs command again |

**Critical:** One task → STOP → User reviews → Next task. No batching. No continuing without checkpoint.

## Task Tool Reference

### TaskList

Lists all tasks with status, owner, and blockers. Use to find ready tasks.

```
TaskList
```

Returns tasks showing:
- `id` — Task identifier
- `subject` — Task title
- `status` — "pending", "in_progress", or "completed"
- `blockedBy` — List of task IDs that must complete first

**Ready task:** status="pending" AND blockedBy is empty

### TaskGet

Retrieves full task details including description.

```
TaskGet
  taskId: "the-task-id"
```

### TaskUpdate

Updates task status or dependencies.

```
TaskUpdate
  taskId: "the-task-id"
  status: "in_progress"  # or "completed"
```

### TaskCreate

Creates a new task (used if discoveries require new work).

```
TaskCreate
  subject: "Handle edge case discovered during implementation"
  description: "Full description..."
  activeForm: "Handling edge case"
```

Then set dependency:
```
TaskUpdate
  taskId: "new-task-id"
  addBlockedBy: ["current-task-id"]
```

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

**Analyze the output:**

- **Fresh start:** All tasks "pending", none "in_progress" → Proceed to Step 1
- **Resume in-progress:** Found task with status="in_progress" → Resume at Step 2
- **Start next:** All previous completed, next is "pending" with empty blockedBy → Step 2
- **All done:** All subtasks "completed" → Step 4 (final check)

**Do NOT ask "where did we leave off?"** — Task state tells you exactly where to resume.

### 1. Load Epic Context

Before executing ANY task, load the epic:

```
TaskGet
  taskId: "epic-task-id"
```

**Extract and keep in mind:**
- Requirements (IMMUTABLE — never water these down)
- Success criteria (validation checklist)
- Anti-patterns (FORBIDDEN shortcuts)
- Architecture approach

**Why:** Requirements prevent rationalizing shortcuts when blocked.

### 2. Execute Current Ready Task

**Find and start the task:**

```
TaskList
```

Identify ready task (status="pending", blockedBy=[]).

```
TaskUpdate
  taskId: "ready-task-id"
  status: "in_progress"
```

**Load full details:**

```
TaskGet
  taskId: "ready-task-id"
```

**Execute the steps in the task description:**

Task descriptions contain 4-8 bite-sized steps. Execute each:

1. Follow TDD cycle (test → fail → implement → pass → commit)
2. Run verifications exactly as specified
3. Use test-runner agent to avoid context pollution:

```
Task
  subagent_type: "hyperpowers:test-runner"
  prompt: "Run: npm test -- tests/models/user.test.ts"
```

**Pre-completion verification:**
- All steps in description completed?
- Tests passing?
- Changes committed?

**Mark complete:**

```
TaskUpdate
  taskId: "ready-task-id"
  status: "completed"
```

### 2a. When Hitting Obstacles

**CRITICAL: Don't automatically try alternative approaches.**

When blocked:

1. **Re-read epic:**
```
TaskGet
  taskId: "epic-task-id"
```

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

### 2b. When Discoveries Require New Work

If implementation reveals unexpected work needed:

```
TaskCreate
  subject: "Handle discovered edge case: empty email validation"
  description: |
    **Discovered during:** Task "Add login endpoint"
    **Issue:** Login crashes on empty email input

    **Step 1: Write failing test**
    ```typescript
    it('returns 400 for empty email', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({ email: '', password: 'test' });
      expect(response.status).toBe(400);
    });
    ```

    **Step 2-5:** [Full implementation steps...]
  activeForm: "Handling empty email validation"
```

**Set dependency on current task:**

```
TaskUpdate
  taskId: "new-edge-case-task"
  addBlockedBy: ["current-task-id"]
```

Document in checkpoint summary that new task was created.

### 3. Review and Adapt

After completing task:

**Review questions:**
1. What did we learn?
2. Discovered existing functionality, blockers, limitations?
3. Moving toward epic success criteria?
4. What's the logical next step?

**Re-read epic:**

```
TaskGet
  taskId: "epic-task-id"
```

**Check remaining tasks:**

```
TaskList
```

**Three cases:**

**A) Next task still valid** → Note for summary, proceed to STOP

**B) Next task now redundant:**
- Discovery makes planned work unnecessary
- Document why in summary
- Can mark completed with note:
```
TaskUpdate
  taskId: "redundant-task-id"
  status: "completed"
  description: "SKIPPED: Discovered existing implementation in lib/auth.ts"
```

**C) Need to adjust approach:**
- Document learnings in summary
- Let user decide how to adapt

### 4. STOP Checkpoint (Mandatory)

**Present summary to user:**

```markdown
## Task Complete — Checkpoint

### What Was Done
- [Summary of implementation]
- [Key decisions made]

### Task Status
```
TaskList output showing current state
```

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

When all subtasks completed:

```
TaskList
```

Verify all subtasks show status="completed".

**Check epic success criteria:**

```
TaskGet
  taskId: "epic-task-id"
```

Review each success criterion. Run full verification.

**Present completion summary:**

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

### Task Summary
```
TaskList showing all completed
```

### Ready for Finish
Use `/gambit:finish` to merge, create PR, or cleanup.
```

**Mark epic complete:**

```
TaskUpdate
  taskId: "epic-task-id"
  status: "completed"
```

## Examples

### Bad: Continuing Without STOP

```
Completed Task 2 (auth middleware).

TaskList shows Task 3 (rate limiting) is ready.

Developer thinks: "Good context, I'll do Task 3 quickly..."

TaskUpdate
  taskId: "task-3"
  status: "in_progress"

Continues to execute Task 3 without STOP.
```

**Why it fails:**
- User can't review Task 2 before Task 3 starts
- User can't clear context
- No checkpoint = no oversight

### Good: Proper STOP

```
TaskUpdate
  taskId: "task-2"
  status: "completed"

## Task Complete — Checkpoint

### What Was Done
- Implemented JWT validation middleware
- Added token refresh handling

### Task Status
TaskList shows:
- Task 1: completed
- Task 2: completed ← just finished
- Task 3: pending, blockedBy: [] ← ready

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

Developer hits complex DB setup.

TaskGet on epic shows the anti-pattern clearly.

Developer thinks: "I'll mock just for now..."
Adds mocks with TODO comment.
```

**Why it fails:** Violates explicit anti-pattern. "Later" never comes.

### Good: Handling Blockers

```
TaskGet
  taskId: "epic-id"

Reads anti-pattern: "FORBIDDEN: Mock database in integration tests"

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
- Complete ALL steps before `TaskUpdate status="completed"`
- Document learnings in checkpoint
- Let user review before continuing

## Verification Checklist

Before completing each task:
- [ ] All steps in description executed
- [ ] Tests passing (verified with test-runner agent)
- [ ] Changes committed
- [ ] `TaskUpdate status="completed"` only after truly done

After completing each task:
- [ ] Reviewed learnings against epic (`TaskGet` on epic)
- [ ] Checked `TaskList` for next ready task
- [ ] Presented checkpoint summary
- [ ] STOPPED execution
- [ ] Waiting for user to run `/gambit:execute-plan` again

Before closing epic:
- [ ] ALL subtasks show status="completed" in `TaskList`
- [ ] ALL success criteria verified against epic
- [ ] ALL anti-patterns avoided
- [ ] `TaskUpdate status="completed"` on epic task

## Integration

**This skill is called by:**
- User via `/gambit:execute-plan`
- After `gambit:write-plan` creates tasks

**This skill calls:**
- `gambit:tdd` during implementation
- `gambit:verify` before claiming task complete
- test-runner agent for running tests
- `gambit:finish` after epic complete

**Task tools used:**
- `TaskList` — Find ready tasks, check progress
- `TaskGet` — Load epic requirements, read task details
- `TaskUpdate` — Mark in_progress, mark completed
- `TaskCreate` — Add tasks for discovered work

**Workflow pattern:**
```
/gambit:execute-plan
  → TaskList (find ready task)
  → TaskUpdate status="in_progress"
  → Execute steps
  → TaskUpdate status="completed"
  → Present checkpoint
  → STOP

[User reviews, clears context if needed]

/gambit:execute-plan
  → TaskList (find next ready task)
  → ... repeat ...

[Until all tasks complete]

/gambit:finish
  → Merge/PR/cleanup
```
