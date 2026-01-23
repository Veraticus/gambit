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

**CRITICAL: Check Design Discovery before switching approaches.**

When you hit a blocker, do NOT automatically try alternatives. First check if the alternative was already considered and rejected.

**Step 1: Re-read epic for "Approaches Considered"**

```
TaskGet
  taskId: "epic-task-id"
```

Look for:
- **Approaches Considered** section
- **"⚠️ REJECTED BECAUSE"** notes
- **"🚫 DO NOT REVISIT UNLESS"** conditions
- **Anti-patterns (FORBIDDEN)** section

**Step 2: Check if your alternative was already rejected**

If the epic shows the approach you're considering was rejected:

```markdown
## Obstacle Encountered

**Current approach:** [Chosen Approach from epic]
**Obstacle:** [What blocker was hit]

**Considering:** [Rejected Approach from epic]

**Original rejection reason:** [Copy from epic]
**DO NOT REVISIT UNLESS:** [Copy from epic]

**Why reconsidering:**
- [ ] Rejection reason no longer applies because: [specific reason]
- [ ] DO NOT REVISIT condition is now met: [specific evidence]

**Recommendation:** [Stay course / Switch with user approval]
```

**Step 3: Get user approval before switching**

Before switching to a previously rejected approach, you MUST:
- Document why the rejection reason no longer applies
- OR explain why this obstacle changes the calculus
- Get explicit user confirmation

**Why this matters:**

Rejected approaches were rejected for good reasons. Those reasons often still apply when obstacles arise.

Example:
- Chose passport.js, hit session complexity
- Considered switching to custom JWT
- But custom JWT was rejected because it requires rewriting 15 files
- The obstacle doesn't change that — switching makes the problem worse

**Step 4: If no prior rejection, check anti-patterns**

If the workaround wasn't previously considered but might violate anti-patterns:

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

If implementation reveals unexpected work needed, new tasks require the same rigor as initial planning.

**Step 1: Create the new task with full detail**

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

    **Step 2: Run test (expect fail)**
    ```bash
    npm test -- tests/routes/auth.test.ts -t "empty email"
    ```
    Expected: FAIL (currently crashes or returns 500)

    **Step 3: Add validation**
    ```typescript
    // src/routes/auth.ts - add at start of login handler
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }
    ```

    **Step 4: Run test (expect pass)**
    ```bash
    npm test -- tests/routes/auth.test.ts -t "empty email"
    ```
    Expected: PASS

    **Step 5: Commit**
    ```bash
    git add src/routes/auth.ts tests/routes/auth.test.ts
    git commit -m "fix(auth): validate email and password presence"
    ```

    ## Success Criteria
    - [ ] Returns 400 for empty email
    - [ ] Returns 400 for empty password
    - [ ] Returns 400 for missing fields
    - [ ] Tests pass
  activeForm: "Handling empty email validation"
```

**Step 2: Set dependency on current task**

```
TaskUpdate
  taskId: "new-edge-case-task"
  addBlockedBy: ["current-task-id"]
```

**Step 3: Apply SRE-style refinement**

Before considering the new task ready, review it with scrutiny:

**Granularity check:**
- Is it 2-5 minutes of work? If longer, break it down.

**Implementability check:**
- Can it be executed without asking questions?
- Are all file paths explicit?
- Is all code complete (no placeholders)?

**Edge cases check:**
- Empty string vs null vs undefined?
- Unicode/special characters?
- Boundary conditions?

**Success criteria check:**
- Are criteria specific and testable?
- At least 3 criteria?

If the task fails any check, update it:

```
TaskUpdate
  taskId: "new-edge-case-task"
  description: "[Updated description with missing details]"
```

**Step 4: Document in checkpoint**

Note in your STOP checkpoint that a new task was created and why.

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

### Good: Handling Blockers (Anti-pattern Check)

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

### Good: Checking Approaches Considered Before Switching

```
Hit obstacle: passport.js session handling is complex.

TaskGet
  taskId: "epic-id"

Epic shows:
## Approaches Considered
1. **passport.js** ✅ CHOSEN
2. **Custom JWT** ⚠️ REJECTED BECAUSE: Requires rewriting 15 files
   🚫 DO NOT REVISIT UNLESS: We're doing a full auth rewrite

## Obstacle Encountered

**Current approach:** passport.js (chosen)
**Obstacle:** Session handling is complex, taking longer than expected

**Considering:** Custom JWT (rejected)

**Original rejection reason:** Requires rewriting 15 files
**DO NOT REVISIT UNLESS:** We're doing a full auth rewrite

**Why reconsidering:**
- [ ] Rejection reason no longer applies because: [can't claim this - still 15 files]
- [ ] DO NOT REVISIT condition is now met: [no - not doing full rewrite]

**Recommendation:** Stay course. The obstacle (complexity) doesn't change the
rejection reason (15 file rewrite). Switching would make things worse.
Research passport.js session patterns instead.
```

### Bad: Switching to Rejected Approach Without Checking

```
Hit obstacle: passport.js session handling is complex.

Developer thinks: "Custom JWT would be simpler..."

TaskUpdate
  taskId: "current-task"
  description: "Switching to custom JWT approach"

[Starts implementing custom JWT without checking epic]
```

**Why it fails:**
- Didn't check if custom JWT was already rejected
- The rejection reason (15 file rewrite) still applies
- Made the problem worse, not better
- Hours wasted on approach that was rejected for good reason

## Anti-patterns

**Don't:**
- Continue past STOP checkpoint
- Execute multiple tasks without stopping
- Water down requirements when blocked
- Close task with steps incomplete
- Rationalize "just one more task"
- Switch to rejected approaches without checking epic
- Create new tasks without SRE-style refinement
- Skip checking "Approaches Considered" when hitting obstacles

**Do:**
- STOP after every task
- Re-read epic when blocked
- Check "Approaches Considered" before switching approaches
- Apply SRE refinement to newly created tasks
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
