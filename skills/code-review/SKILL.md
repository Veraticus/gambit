---
name: code-review
description: Use for requesting and receiving code reviews - dispatch reviewer agent for self-review, verify feedback before implementing, no performative agreement
---

# Code Review

## Overview

Code review requires technical evaluation, not emotional performance. Verify before implementing. Push back with evidence.

**Core principle:** Every piece of feedback must be verified against the codebase before implementation. Actions over words.

**Announce at start:** "I'm using gambit:code-review to [request/receive] review."

## Rigidity Level

MEDIUM FREEDOM — Follow the self-review checklist strictly before requesting. Verify ALL feedback before implementing ANY. Adapt review scope to context. No performative agreement.

## Quick Reference

### Requesting Review

| Step | Action | STOP If |
|------|--------|---------|
| 1 | Run self-review checklist | Critical issues found |
| 2 | Dispatch code-reviewer agent | - |
| 3 | Act on feedback by severity | Critical unfixed |

### Receiving Review

| Step | Action | STOP If |
|------|--------|---------|
| 1 | Read complete feedback | - |
| 2 | Verify EACH item against codebase | Can't verify without more info |
| 3 | Clarify ALL unclear items | Any item unclear |
| 4 | Implement one item at a time | Tests fail |

## The Iron Law

```
NO IMPLEMENTING FEEDBACK WITHOUT VERIFYING IT FIRST
```

Verification means running commands — reading code, grepping for usage, running tests. Not thinking about it. Not assuming.

- Reviewer says "remove X" → `grep -r "X"` to check if it's used
- Reviewer says "change pattern" → read the code, understand WHY current pattern exists
- Reviewer says "fix edge case" → write a test proving the edge case fails

**Forbidden responses:** "You're absolutely right!", "Great point!", "Thanks for catching that!", "Let me implement that now" (before verification)

---

## Part 1: Requesting Review

### When to Request

**Mandatory:**
- After completing Task from epic
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

### Step 1: Self-Review Checklist

**BEFORE dispatching reviewer, verify:**

```
Task
  subagent_type: "general-purpose"
  description: "Run automated checks"
  prompt: "Run: [project test command] && [project lint command]. Report pass/fail counts and any failures."
```

**Automated checks:**
- [ ] All tests pass
- [ ] No linter warnings
- [ ] No TODOs without issue numbers
- [ ] No stub implementations (search for `unimplemented`, `todo!`, `panic("not implemented")`, `raise NotImplementedError`, etc. as appropriate for the language)

**Code quality self-check:**
- [ ] Error handling proper (not panicking/crashing on bad input)
- [ ] Edge cases handled (empty, nil, boundaries)
- [ ] Names clear (would junior understand in 6 months?)
- [ ] No "while I'm here" changes mixed in
- [ ] Tests meaningful (not tautological)

**If any critical issues found:** Fix before requesting review.

### Step 2: Dispatch Code-Reviewer Agent

Get the commit range, then dispatch. See [REFERENCE.md](REFERENCE.md) for the full dispatch template.

```bash
BASE_SHA=$(git rev-parse HEAD~N)  # or origin/main for full branch diff
HEAD_SHA=$(git rev-parse HEAD)
```

```
Task
  subagent_type: "feature-dev:code-reviewer"
  description: "Review [brief description]"
  prompt: |
    Review the changes between {BASE_SHA} and {HEAD_SHA}.

    ## What Was Implemented
    [Brief description of what you built]

    ## Requirements
    [What it should do — from Task or epic]

    ## Specific Concerns
    [Areas you're uncertain about]

    Return findings as:
    - Critical: [Must fix before merge]
    - Important: [Should fix before proceeding]
    - Minor: [Note for future]
    - Strengths: [What's done well]
```

### Step 3: Act on Feedback

**By severity:**

| Severity | Action |
|----------|--------|
| **Critical** | Fix immediately. Do not proceed until fixed. |
| **Important** | Fix before proceeding to next Task. |
| **Minor** | Note for later. OK to defer. |

**If reviewer is wrong:** Push back with technical reasoning. Show code/tests that prove it works.

---

## Part 2: Receiving Review

### The Response Pattern

```
WHEN receiving feedback:

1. READ: Complete feedback without reacting
2. VERIFY: Check EACH item against the actual codebase
3. CLARIFY: Ask about ALL unclear items before implementing ANY
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

### Step 1: Read Without Reacting

Read all feedback items. Do NOT:
- Start implementing the first item before reading the rest
- React emotionally (items may be related or contradictory)
- Use performative language

### Step 2: Verify Against Codebase

**BEFORE implementing ANYTHING, verify EACH item:**

For each piece of feedback, run verification:

```bash
# "Remove this function" → Check if it's used
grep -r "functionName" src/

# "Change this pattern" → Understand why current pattern exists
# Read the code, read the git history

# "Fix this edge case" → Verify the edge case actually fails
# Write a quick test or run the scenario
```

**Ask for each item:**
1. Technically correct for THIS codebase?
2. Would it break existing functionality?
3. Is there a reason for the current implementation?
4. Does reviewer understand full context?

### Step 3: Clarify Unclear Items

**IF any item is unclear: STOP. Do not implement anything yet.**

```
❌ WRONG: Implement items 1,2,3 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3. Need clarification on 4 and 5 before proceeding."
```

**Why:** Items may be related. Partial understanding = wrong implementation.

### Step 4: Evaluate and Respond

**For each verified item:**

| Verdict | Response |
|---------|----------|
| Correct | Just fix it. Or: "Fixed. [Brief description]" |
| Wrong | Push back with evidence: code, tests, grep results |
| Partially right | "Agree with X, but Y would break Z. How about W?" |
| Need more info | "Can't verify without [X]. Should I investigate?" |

**YAGNI check:** If reviewer suggests adding features, check if the code is actually used:

```bash
grep -r "functionName" src/
# If unused: "Nothing calls this. Remove it (YAGNI)?"
```

### Step 5: Implement One at a Time

**FOR multi-item feedback:**

1. Clarify anything unclear FIRST
2. Then implement in this order:
   - Blocking issues (breaks, security)
   - Simple fixes (typos, imports)
   - Complex fixes (refactoring, logic)
3. Test each fix individually
4. Verify no regressions after each

### When to Push Back

**Push back when:**
- Suggestion breaks existing functionality → show failing test
- Reviewer lacks full context → provide missing context
- Violates YAGNI (unused feature) → show grep proving unused
- Technically incorrect for this stack → explain constraint
- Conflicts with architectural decisions → stop and discuss

**How to push back:**
- Technical reasoning, not defensiveness
- Reference working tests/code
- Ask specific questions
- Escalate if architectural

### Acknowledging Correct Feedback

```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch — [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
```

Actions speak. Just fix it. The code itself shows you heard.

### Correcting Your Pushback

**If you pushed back and were wrong:**

```
✅ "You were right — I checked [X] and it does [Y]. Implementing now."
❌ Long apology or defending why you pushed back
```

State the correction factually and move on.

---

## Critical Rules

### Rules That Have No Exceptions

1. **Run self-review checklist before requesting** → Don't waste reviewer time on obvious issues
2. **Verify ALL feedback before implementing ANY** → Check against codebase with tools, not assumptions
3. **No performative agreement** → Technical acknowledgment or pushback only
4. **Clarify ALL unclear items FIRST** → Don't implement partial understanding
5. **Test each fix individually** → One at a time, verify no regressions
6. **Push back with technical evidence** → Not defensiveness, not blind acceptance

### Common Excuses

All mean: **STOP. Return to the verification step.**

| Excuse | Reality |
|--------|---------|
| "Reviewer is senior, they must be right" | Seniority ≠ infallibility. Verify. |
| "It's a simple change, just do it" | Simple changes break things too. Verify. |
| "No time for back-and-forth" | Wrong implementation wastes MORE time. Verify. |
| "I'll verify after implementing" | Then you'll rationalize it works. Verify FIRST. |
| "Feedback looks reasonable" | Looking reasonable ≠ being correct. Verify. |
| "Just this once, skip verification" | "Just this once" is how bugs ship |
| "Thank you for the thorough review!" | Performative. Just verify and act. |

---

## Verification Checklist

### Before Requesting Review
- [ ] All tests pass (verified with actual command)
- [ ] No linter warnings
- [ ] No TODOs without issue numbers
- [ ] No stub implementations
- [ ] Error handling proper
- [ ] Edge cases handled
- [ ] Names clear
- [ ] Tests meaningful (not tautological)

### After Receiving Review
- [ ] Read complete feedback without reacting
- [ ] Verified EACH item against codebase (with tools)
- [ ] Asked for clarification on ALL unclear items
- [ ] Pushed back on incorrect suggestions (with evidence)
- [ ] Implemented one item at a time
- [ ] Tested after each fix
- [ ] Verified no regressions

**Can't check all boxes?** Return to process.

---

## Examples

See [REFERENCE.md](REFERENCE.md) for detailed good/bad examples including:
- Performative agreement vs technical verification
- Blind implementation vs verify-then-implement
- YAGNI check on suggested features
- Handling unclear multi-item feedback
- Full dispatch template with all placeholders

---

## Integration

**This skill calls:**
- `gambit:verification` (for self-review verification)
- feature-dev:code-reviewer agent (`subagent_type: "feature-dev:code-reviewer"`) for requesting review
- general-purpose agent (`subagent_type: "general-purpose"`) for running automated checks

**Called by:**
- `gambit:executing-plans` (after each Task)
- Before merging to main
- When stuck and need fresh perspective

**Workflow:**
```
Complete Task
    ↓
Self-review checklist (pass automated checks)
    ↓
Dispatch code-reviewer agent
    ↓
Receive feedback
    ↓
Read → Verify each item → Clarify unclear → Implement one-at-a-time → Test each
    ↓
Ready for next Task
```
