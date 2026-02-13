# Code Review Examples and Patterns

Detailed examples for the code-review skill. See [SKILL.md](SKILL.md) for the process.

## Full Dispatch Template

```
Task
  subagent_type: "feature-dev:code-reviewer"
  description: "Review [brief description]"
  prompt: |
    Review the changes in this commit range:

    ## What Was Implemented
    [Brief description of what you built]

    ## Requirements
    [What it should do — from Task or epic]

    ## Commit Range
    Base: {BASE_SHA}
    Head: {HEAD_SHA}

    ## Specific Concerns
    [Areas you're uncertain about]

    ## Review Focus
    - Does implementation match requirements?
    - Are there bugs, edge cases missed?
    - Is error handling sufficient?
    - Are tests meaningful (not tautological)?
    - Is code clear and maintainable?

    Return findings as:
    - Critical: [Must fix before merge]
    - Important: [Should fix before proceeding]
    - Minor: [Note for future]
    - Strengths: [What's done well]
```

**Template placeholders:**

| Placeholder | Description |
|-------------|-------------|
| `{BASE_SHA}` | Starting commit (`git rev-parse HEAD~N` or `origin/main`) |
| `{HEAD_SHA}` | Ending commit (`git rev-parse HEAD`) |

## Bad: Performative Agreement

```
Reviewer: "Remove legacy code"

❌ "You're absolutely right! Let me remove that..."
[Removes code without checking if it's actually unused]
[Build breaks because legacy code was still called]
```

**Why it fails:**
- Agreed without verifying
- Didn't check if code is still referenced
- Performative language substituted for technical evaluation

## Good: Technical Verification

```
Reviewer: "Remove legacy code"

✅ "Checking..."
$ grep -r "legacyFunction" src/
src/handler.go:45: result := legacyFunction(data)

"legacyFunction is still called at handler.go:45. Should I:
A) Update handler to use new function, then remove legacy?
B) Keep legacy for now until handler is migrated?"
```

**Why it works:**
- Verified claim before acting
- Found evidence contradicting assumption
- Presented options with context

## Bad: Blind Implementation

```
Reviewer: "Use async/await pattern here"

[Implements async/await without checking]
[Breaks because caller doesn't handle promises]
[Introduces race condition in tests]
```

**Why it fails:**
- Didn't check callers
- Didn't verify compatibility
- Changed contract without updating consumers

## Good: Verify Then Implement

```
Reviewer: "Use async/await pattern here"

✅ "Checking callers..."
$ grep -r "functionName" src/
3 callers found, all synchronous

"Converting to async would require updating 3 callers:
- handler.go:45
- service.go:78
- batch.go:112

Want me to update all callers, or keep synchronous for now?"
```

## Bad: Implementing Without YAGNI Check

```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"

"Great idea! Let me add all of that..."
[Implements full metrics system]
[Nobody uses it]
[Maintenance burden for unused code]
```

## Good: YAGNI Check

```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"

✅ "Checking usage..."
$ grep -r "metricsEndpoint" src/
[no results]

"Nothing calls metricsEndpoint. Remove it (YAGNI)?
Or is there usage I'm missing?"
```

## Bad: Partial Implementation of Unclear Feedback

```
Reviewer: "Fix items 1-6"

Items 1,2,3,6: Clear
Items 4,5: Unclear what specifically to change

❌ "Fixing 1,2,3,6 now..."
[Implements partial, asks about 4,5 after]
[Item 6 depends on 4, implementation is wrong]
```

**Why it fails:**
- Implemented before understanding all items
- Items may be interdependent
- Later clarification reveals wasted work

## Good: Clarify Everything First

```
Reviewer: "Fix items 1-6"

Items 1,2,3,6: Clear
Items 4,5: Unclear what specifically to change

✅ "I understand items 1,2,3,6. Need clarification on 4 and 5:
- Item 4 mentions 'proper error handling' — which function?
- Item 5 says 'update tests' — add new tests or modify existing?

Will implement all 6 once clarified."
```

## Bad: Authority Deference

```
Reviewer (CTO): "Replace channels with mutex for concurrency"

❌ "The CTO knows best, implementing..."
[Replaces correct producer-consumer pattern with mutex]
[Introduces deadlock potential]
```

## Good: Respectful Technical Pushback

```
Reviewer (CTO): "Replace channels with mutex for concurrency"

✅ "Checking the concurrency pattern..."
$ Read handler.go:40-60
[Code shows producer-consumer pattern with channels]

"The current code uses channels for a producer-consumer pattern —
multiple handlers send to a single processor goroutine. Channels
are the idiomatic choice here because they provide ordering and
backpressure.

A mutex would protect shared state, which is a different pattern.
Is there a specific concurrency bug you've observed, or should we
change the architecture to shared-state?"
```

## Self-Review Quick Commands

Before requesting review, run project-appropriate checks:

```bash
# Find TODOs without issue numbers (adjust grep pattern for your project)
grep -rn "TODO\|FIXME" src/ | grep -v "#[0-9]"

# Find stub implementations (language-dependent)
# Go:     grep -rn "panic\|TODO" src/
# Python: grep -rn "raise NotImplementedError\|pass  #" src/
# Rust:   grep -rn "todo!\|unimplemented!\|unwrap()" src/
# JS/TS:  grep -rn "throw new Error.*not implemented\|TODO" src/
```
