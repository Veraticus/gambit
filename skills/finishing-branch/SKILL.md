---
name: finishing-branch
description: Use when implementation complete and tests pass - verifies all tasks done, presents integration options (merge/PR/keep/discard), executes choice
---

# Finishing a Development Branch

## Overview

Guide completion of development work by verifying tasks, running tests, presenting clear options, and handling chosen workflow.

**Core principle:** Verify tasks → Verify tests → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using gambit:finish to complete this work."

## Rigidity Level

LOW FREEDOM - Follow the 6-step process exactly. Present exactly 4 options. Never skip test verification. Must confirm before discarding.

## Quick Reference

| Step | Action | If Blocked |
|------|--------|------------|
| 1 | Verify all tasks complete | Tasks still open → STOP |
| 2 | Verify tests pass (test-runner agent) | Tests fail → STOP |
| 3 | Determine base branch | Ask if unclear |
| 4 | Present exactly 4 options | Wait for choice |
| 5 | Execute choice | Follow option workflow |
| 6 | Cleanup worktree (options 1,2,4 only) | Option 3 keeps worktree |

**Options:** 1=Merge locally, 2=PR, 3=Keep as-is, 4=Discard (requires confirmation)

## When to Use

- Implementation complete and reviewed
- All tasks for epic are done
- Ready to integrate work back to main branch

**Don't use for:**
- Work still in progress
- Tests failing
- Epic has open tasks
- Mid-implementation (use `gambit:execute-plan`)

## The Process

### Step 1: Verify All Tasks Complete

**Check task status:**

```
TaskList
```

**Look for the epic and its subtasks. All must show status="completed".**

**If any tasks still open:**

```
Cannot finish: N tasks still open:
- [task-id]: Task Name (status: in_progress)
- [task-id]: Task Name (status: pending)

Complete all tasks before finishing.
```

**STOP. Do not proceed.**

**If all tasks complete:**

```
TaskGet
  taskId: "epic-task-id"
```

Verify all success criteria are met.

### Step 2: Verify Tests Pass

**IMPORTANT:** Use test-runner agent to avoid context pollution.

```
Task
  subagent_type: "hyperpowers:test-runner"
  prompt: "Run: go test ./..."
```

Agent returns summary + failures only.

**If tests fail:**

```
Tests failing (N failures). Must fix before completing:

[Show failures]

Cannot proceed until tests pass.
```

**STOP. Do not proceed.**

**If tests pass:** Continue to Step 3.

### Step 3: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main - is that correct?"

### Step 4: Present Options

**Present exactly these 4 options:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

Or use AskUserQuestion:

```
AskUserQuestion
  questions:
    - question: "Implementation complete. What would you like to do?"
      header: "Integration"
      options:
        - label: "Merge locally"
          description: "Merge to <base-branch>, delete feature branch"
        - label: "Create Pull Request"
          description: "Push and create PR for review"
        - label: "Keep as-is"
          description: "Leave branch, handle later"
        - label: "Discard"
          description: "Delete all work (requires confirmation)"
      multiSelect: false
```

**Don't add explanation.** Keep concise.

### Step 5: Execute Choice

#### Option 1: Merge Locally

```bash
# Switch to base branch
git checkout <base-branch>

# Pull latest
git pull

# Merge feature branch
git merge <feature-branch>
```

**Verify tests on merged result:**

```
Task
  subagent_type: "hyperpowers:test-runner"
  prompt: "Run: go test ./..."
```

**If tests pass:**

```bash
git branch -d <feature-branch>
```

Then: Step 6 (cleanup worktree)

**If tests fail after merge:**

```
Merge introduced test failures. Options:
1. Fix failures before completing
2. Abort merge (git merge --abort)

Which option?
```

#### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>
```

**Create PR with epic context:**

```
TaskGet
  taskId: "epic-task-id"
```

Use epic info for PR description:

```bash
gh pr create --title "feat: <epic-name>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets from epic requirements>

## Tasks Completed
- Task 1: <description>
- Task 2: <description>

## Test Plan
- [ ] All tests passing
- [ ] <verification steps from epic success criteria>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**Report PR URL.**

Then: Step 6 (cleanup worktree) — **BUT keep worktree for PR option**

Actually, for Option 2, DON'T cleanup worktree. User may need it for PR feedback.

```
Pull request created: <PR-URL>

Keeping worktree at <path> for PR updates.
```

#### Option 3: Keep As-Is

```
Keeping branch <name>. Worktree preserved at <path>.
```

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**

```
This will permanently delete:
- Branch <name>
- All commits:
  * <commit-hash> <commit-message>
  * <commit-hash> <commit-message>
  * ... (N more commits)
- Worktree at <path>

Type 'discard' to confirm.
```

**Wait for exact "discard" confirmation.**

**If confirmed:**

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: Step 6 (cleanup worktree)

### Step 6: Cleanup Worktree

**For Options 1 and 4 only:**

```bash
# Check if in worktree
git worktree list | grep <feature-branch>

# If yes
git worktree remove <worktree-path>
```

**For Options 2 and 3:** Keep worktree.

## Option Matrix

| Option | Merge | Push | Keep Worktree | Cleanup Branch | Cleanup Worktree |
|--------|-------|------|---------------|----------------|------------------|
| 1. Merge locally | Yes | - | - | Yes | Yes |
| 2. Create PR | - | Yes | Yes | - | - |
| 3. Keep as-is | - | - | Yes | - | - |
| 4. Discard | - | - | - | Yes (force) | Yes |

## Task Tool Reference

### TaskList

```
TaskList
```

Returns all tasks with status. Look for epic and subtasks all showing "completed".

### TaskGet

```
TaskGet
  taskId: "epic-task-id"
```

Read success criteria to include in PR description.

### TaskUpdate

```
TaskUpdate
  taskId: "epic-task-id"
  status: "completed"
```

Mark epic complete after successful merge/PR.

## Examples

### Bad: Skip Test Verification

```
# Tasks all complete ✓
TaskList shows all completed

# SKIP test verification
# Jump to presenting options

"Implementation complete. What would you like to do?..."

User selects Option 1

git checkout main
git merge feature-branch
# Tests fail! Broken code on main
```

**Why it fails:**
- Merged broken code to main
- Other developers pull broken main
- CI/CD fails, blocks deployment

### Good: Verify Tests Before Options

```
# Tasks all complete ✓
TaskList shows all completed

# Verify tests
Task subagent_type: "hyperpowers:test-runner"
      prompt: "Run: go test ./..."

Agent reports: "127 tests passed, 0 failures"

# NOW present options
"Implementation complete. What would you like to do?..."
```

### Bad: Cleanup Worktree for PR

```
User selects Option 2
git push -u origin feature-auth
gh pr create ...

# Immediately cleanup worktree
git worktree remove ../feature-auth-worktree

# PR gets feedback: "Please add rate limiting"
# Worktree is gone! Have to recreate
```

**Why it fails:**
- PR likely needs updates
- Have to recreate worktree
- Lost local state

### Good: Keep Worktree for PR

```
User selects Option 2
git push -u origin feature-auth
gh pr create ...

"Pull request created: https://github.com/user/repo/pull/42

Keeping worktree at ../feature-auth-worktree for PR updates."

# User can address feedback in same worktree
```

### Bad: Discard Without Confirmation

```
User: "Discard this work"

# Immediately execute
git checkout main
git branch -D feature-experimental
git worktree remove ../worktree

# 50 commits deleted
# User: "Wait, I meant the LAST commit!"
```

**Why it fails:**
- No confirmation before destructive action
- Misunderstood user intent
- Permanent data loss

### Good: Require Confirmation

```
User: "Discard this work"

"This will permanently delete:
- Branch feature-experimental
- All commits:
  * a1b2c3d Add OAuth integration
  * d4e5f6g Add rate limiting
  ... (48 more commits)
- Worktree at ../worktree

Type 'discard' to confirm."

User types: "discard"

# NOW execute
git checkout main
git branch -D feature-experimental
git worktree remove ../worktree

"Branch deleted."
```

## Anti-patterns

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without typed confirmation
- Force-push without explicit request
- Skip task verification
- Cleanup worktree for Option 2 (PR)

**Always:**
- Verify all tasks complete before proceeding
- Verify tests before offering options
- Present exactly 4 options (not open-ended)
- Get typed "discard" confirmation for Option 4
- Keep worktree for Options 2 & 3

## Verification Checklist

Before completing:

- [ ] All tasks show status="completed" (TaskList)
- [ ] Tests verified passing (via test-runner agent)
- [ ] Presented exactly 4 options
- [ ] Waited for user choice
- [ ] If Option 1: Verified tests on merged result
- [ ] If Option 4: Got typed "discard" confirmation
- [ ] Worktree cleaned for Options 1, 4 only
- [ ] Worktree kept for Options 2, 3
- [ ] Reported completion status

## Integration

**This skill is called by:**
- User after implementation complete
- After `gambit:execute-plan` completes all tasks

**This skill calls:**
- test-runner agent (for test verification)
- gh commands (PR creation)

**This skill pairs with:**
- `gambit:worktree` - Cleans up worktree created by that skill

**Workflow:**
```
gambit:execute-plan
    → All tasks complete
gambit:finish
    → Verify tasks + tests
    → Present options
    → Execute choice
    → Cleanup
```
