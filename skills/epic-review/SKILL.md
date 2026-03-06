---
name: epic-review
description: Reviews completed epic implementation for quality, architecture, security, and completeness before finishing-branch. Dispatches four specialized reviewer agents (conformance, security, quality, performance) in parallel for unbiased review. Use after all tasks in an epic are completed and before merging, creating a PR, or discarding work.
user_invokable: true
---

# Epic Review

## Overview

Dispatch four specialized reviewer agents to independently audit a completed epic, then synthesize their findings into a gate decision. Reviewers run in fresh context — they haven't seen the implementation process and have no sunk cost bias.

**Core principle:** The implementing context is the worst reviewer of its own work. Delegate review to fresh agents.

**Announce at start:** "I'm using gambit:epic-review to validate this implementation before finishing."

## Rigidity Level

LOW FREEDOM — Dispatch all four reviewers. Synthesize all findings. No approval if any reviewer finds gaps. No skipping reviewers for "simple" epics.

## Quick Reference

| Step | Action | STOP If |
|------|--------|---------|
| **1. Load Context** | Epic + tasks + changed files list | Can't load epic |
| **2. Prepare Brief** | Epic requirements + file list + base branch | Brief incomplete |
| **3. Dispatch Reviewers** | 4 agents in parallel | Any agent fails to run |
| **4. Synthesize** | Merge findings, resolve conflicts | — |
| **5. Gate** | APPROVED or GAPS FOUND | Gaps → fix tasks, STOP |

## When to Use

- All epic subtasks show "completed"
- Before `gambit:finishing-branch`
- Called automatically by `gambit:executing-plans` Step 5

**Don't use when:**
- Tasks still in progress → use `gambit:executing-plans`
- Single task review → use `gambit:verification`
- Mid-implementation quality check → too early

## The Process

### Step 1: Load Context

```
TaskGet → epic (requirements, success criteria, anti-patterns)
TaskList → all subtasks (verify all completed)
```

```bash
git diff main...HEAD --name-only    # Changed files
git diff main...HEAD --stat         # Change summary
```

### Step 2: Prepare Review Brief

Build a brief that each reviewer agent will receive. Include:

1. **Epic requirements** — full text from TaskGet (requirements, success criteria, anti-patterns)
2. **Changed files** — the `--name-only` output
3. **Base branch** — what the diff is against

Do NOT include your opinions, implementation notes, or rationale. The reviewers should form their own conclusions from the code.

### Step 3: Dispatch Four Reviewers

Dispatch all four reviewer agents **in a single message** using their dedicated agent types. Each runs on Sonnet for focused, unbiased review.

```
Agent subagent_type="conformance-reviewer" prompt=[brief]
Agent subagent_type="security-reviewer" prompt=[brief]
Agent subagent_type="quality-reviewer" prompt=[brief]
Agent subagent_type="performance-reviewer" prompt=[brief]
```

The prompt for each agent should contain only the review brief (epic requirements + changed files list). The agent definitions already contain the review instructions and criteria — do not duplicate them in the prompt.

**Critical:** Dispatch in ONE message so they run in parallel. Do not wait for one before dispatching the next.

Each reviewer will:
- Read the changed files independently (they have Read, Bash, Grep, Glob tools)
- Evaluate their dimensions with evidence
- Return findings as APPROVED or GAPS FOUND

### Step 4: Synthesize Findings

Collect all four reviewer reports. Present a unified summary:

```markdown
## Epic Review: [Epic Name]

### Conformance Review
[Reviewer's verdict + key findings]

### Security Review
[Reviewer's verdict + key findings]

### Quality Review
[Reviewer's verdict + key findings]

### Performance Review
[Reviewer's verdict + key findings]

### Overall Verdict: APPROVED / GAPS FOUND
```

**Conflict resolution:** If reviewers disagree (e.g., one flags something another considers fine), err toward the finding. Investigate the specific concern before dismissing it.

### Step 5: Gate Decision

**If APPROVED (all four reviewers approve):**

Announce: "Epic review passed. Proceeding to finishing-branch."

Invoke `gambit:finishing-branch` directly via Skill tool.

**If GAPS FOUND (any reviewer finds gaps):**

```markdown
## Gaps Found — Cannot Proceed

### Issues by Reviewer
[Consolidated list with evidence and locations]

### Recommended Fix Tasks
- [Concrete task description for each gap]
```

Create fix tasks with `TaskCreate` for each gap. Set dependencies. Then STOP — return to `gambit:executing-plans` to implement fixes.

**Do NOT proceed to finishing-branch with gaps. Do NOT override reviewer findings.**

---

## Examples

### Good: Parallel Dispatch

```
# ONE message, four Agent calls:
Agent: "Conformance review of OAuth epic..." (runs in background)
Agent: "Security review of OAuth epic..."    (runs in background)
Agent: "Quality review of OAuth epic..."     (runs in background)
Agent: "Performance review of OAuth epic..." (runs in background)

# All four return findings independently
# Synthesize into unified verdict
```

### Bad: Sequential or Skipped

```
# WRONG: Only dispatching two reviewers
"Security isn't relevant for this config change"

# WRONG: Reviewing in main context instead of dispatching
"Let me just quickly check the architecture myself..."

# WRONG: Overriding a reviewer
"The quality reviewer flagged nolint pragmas but those are fine"
```

## Critical Rules

1. **All four reviewers dispatched** — no skipping for "simple" epics
2. **Parallel dispatch** — one message, four agents
3. **No self-review** — main context prepares brief and synthesizes, does NOT review code
4. **Reviewer findings are authoritative** — don't override without investigation
5. **Any gap blocks** — one reviewer finding gaps = GAPS FOUND overall
6. **Brief is neutral** — don't include opinions or justifications in what you send reviewers

**Common rationalizations:**

| Excuse | Reality |
|--------|---------|
| "I already reviewed during implementation" | You're biased — that's why agents exist |
| "Security isn't relevant here" | Every project has an attack surface |
| "Performance review is overkill" | Dispatch it anyway — it's parallel, costs nothing |
| "The reviewer is being too strict" | Investigate the finding before dismissing |
| "I can review faster myself" | Speed isn't the goal — unbiased review is |

## Verification Checklist

- [ ] Epic loaded, all tasks confirmed completed
- [ ] Review brief prepared (requirements + changed files, no opinions)
- [ ] All four reviewers dispatched in single message
- [ ] All four reviewer reports collected
- [ ] Findings synthesized into unified summary
- [ ] If APPROVED: invoked finishing-branch via Skill tool
- [ ] If GAPS: created fix tasks, STOPPED

## Integration

**Called by:**
- `gambit:executing-plans` (Step 5, replaces direct finishing-branch call)
- User via `/gambit:epic-review`

**Calls:**
- `gambit:finishing-branch` (if approved)

**Dispatches agents (all Sonnet, parallel):**
- `conformance-reviewer` — completeness, architecture, dead code
- `security-reviewer` — OWASP audit, secrets, auth, data exposure
- `quality-reviewer` — language idioms, linter circumvention, test quality
- `performance-reviewer` — scaling, N+1, resource management

**Call chain:**
```
executing-plans (all tasks done) → epic-review → finishing-branch
                                       ↓
                                 (if gaps: STOP → fix → re-review)
```
