---
name: brainstorming
description: Refines rough ideas into validated designs stored as epic Tasks with immutable requirements through Socratic questioning. Use when planning new features, exploring approaches before coding, or turning vague ideas into actionable tasks.
user_invokable: true
---

# Brainstorming Ideas Into Designs

## Overview

Turn rough ideas into validated designs stored as epic Tasks with immutable requirements. Tasks are created iteratively as you learn, not upfront.

**Core principle:** Ask questions to understand, research before proposing, document decisions for future reference.

**Announce at start:** "I'm using gambit:brainstorming to refine your idea into a design."

## Rigidity Level

HIGH FREEDOM - Adapt questioning to context. But always:
- Create immutable epic before code
- Create only first task (not full tree)
- Use AskUserQuestion tool for questions
- Apply task refinement before handoff

## Quick Reference

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Ask clarifying questions | Understanding of requirements |
| 2 | Research codebase and patterns | Existing approaches |
| 3 | Propose 2-3 approaches | Recommended option |
| 4 | Present design in sections | Validated architecture |
| 5 | Create epic Task | Immutable requirements + anti-patterns |
| 6 | Create ONLY first subtask | Ready for executing-plans |
| 7 | Apply task refinement | Corner cases covered |
| 8 | Hand off to executing-plans | Iterative execution begins |

**Key:** Epic = contract (immutable), Tasks = adaptive (created as you learn)

## When to Use

- User describes a new feature to implement
- User has a rough idea that needs refinement
- About to write code without clear requirements
- Need to explore approaches before committing

**Don't use for:**
- Executing existing plans (use `gambit:executing-plans`)
- Fixing bugs (use `gambit:debugging`)
- Refactoring (use `gambit:refactoring`)
- Requirements already crystal clear and epic exists

## The Process

### 1. Understand the Idea

**Research existing context first:**

```
Task
  subagent_type: "Explore"
  prompt: "Find existing [relevant] implementation patterns in this codebase"
```

**Then ask clarifying questions using AskUserQuestion tool.**

Aim for 2-4 questions per round, 2-4 rounds total. Use multiple choice with recommended defaults. Stop when you understand scope, constraints, existing patterns, and scale.

```
AskUserQuestion
  questions:
    - question: "Where should OAuth tokens be stored?"
      header: "Token storage"
      options:
        - label: "httpOnly cookies (Recommended)"
          description: "Prevents XSS token theft, industry standard"
        - label: "sessionStorage"
          description: "Cleared on tab close, less persistent"
      multiSelect: false
```

**Do NOT print questions as text and wait** — always use the AskUserQuestion tool.

---

### 2. Explore Approaches

**Research before proposing:**
- Existing pattern in codebase → Explore agent
- New integration → WebSearch or WebFetch
- No results → Ask user for direction

**Propose 2-3 approaches:**
- Lead with your recommendation and why
- Include pros/cons for each
- Reference codebase consistency as a factor

```
Based on [research findings], I recommend:

1. **[Approach A]** (recommended)
   - Pros: [benefits, especially "matches existing pattern"]
   - Cons: [drawbacks]

2. **[Approach B]**
   - Pros: [benefits]
   - Cons: [drawbacks]

I recommend option 1 because [specific reason].
```

---

### 3. Present the Design

Once approach is chosen, present in digestible sections. Ask "Does this look right?" after each. Cover: architecture, components, data flow, error handling, testing.

---

### 4. Create the Epic Task

After design is validated, create epic as immutable contract. See [TEMPLATES.md](TEMPLATES.md) for the full template with all sections.

**Required epic sections:**

| Section | Purpose |
|---------|---------|
| Requirements (IMMUTABLE) | Specific, testable conditions that must be true |
| Success Criteria | Objective, checkable items including "all tests passing" |
| Anti-Patterns (FORBIDDEN) | Explicitly forbidden patterns with reasoning |
| Approach | 2-3 paragraph summary of chosen approach |
| Approaches Considered | Rejected alternatives with DO NOT REVISIT conditions |

```
TaskCreate
  subject: "Epic: [Feature Name]"
  description: |
    ## Requirements (IMMUTABLE)
    - Requirement 1: [concrete, testable]

    ## Success Criteria (MUST ALL BE TRUE)
    - [ ] [objective criterion]
    - [ ] All tests passing

    ## Anti-Patterns (FORBIDDEN)
    - NO [pattern] (reason: [why])

    ## Approach
    [2-3 paragraph summary]

    ## Approaches Considered
    ### [Rejected Approach] - REJECTED
    REJECTED BECAUSE: [reason]
    DO NOT REVISIT UNLESS: [condition]
  activeForm: "Planning [feature name]"
```

**Anti-patterns prevent requirement erosion.** When implementation gets hard, there's pressure to water down requirements. Explicit forbidden patterns with reasoning prevent this.

---

### 5. Create ONLY First Task

One task, not a full tree. Subsequent tasks are created by executing-plans as you learn.

```
TaskCreate
  subject: "Add [specific deliverable]"
  description: |
    ## Goal
    [One clear outcome]

    ## Implementation
    1. Study existing code: [file.ts:line]
    2. Write tests first (TDD)
    3. Implementation:
       - [ ] file.ts - function() - [what it does]

    ## Success Criteria
    - [ ] [specific measurable outcome]
    - [ ] Tests passing
    - [ ] Pre-commit hooks passing
  activeForm: "Adding [deliverable]"
```

**Why only one?** Each subsequent task reflects learnings from the previous one. Upfront task trees become brittle when assumptions change.

---

### 6. Apply Task Refinement

Before handoff, verify the first task passes these checks:

1. **Scoped:** 2-5 minutes of work (if longer, break down)
2. **Self-contained:** Can execute without asking questions
3. **Explicit:** All file paths specified
4. **Testable:** At least 3 success criteria

**Corner cases to check:**
- What if the happy path fails?
- Edge case inputs? Empty/null/missing data?
- Network/IO failures? Concurrent access?
- Security implications? Boundary conditions?

Update the task with any missing details before proceeding.

---

### 7. Handoff

```
Epic created with immutable requirements.
First task ready and refined.

Ready to start? I'll use gambit:executing-plans to work through this iteratively.
Each task adapts to what we learn — no brittle upfront planning.
```

## Examples

### Bad: Full Task Tree Upfront

```
TaskCreate "Epic: Add OAuth"
TaskCreate "Task 1: Configure OAuth"
TaskCreate "Task 2: Implement token exchange"
TaskCreate "Task 3: Add refresh logic"
# Execute Task 1 → discover library handles refresh
# Task 3 is now wrong. Task tree is brittle.
```

### Good: Iterative Task Creation

```
TaskCreate "Epic: Add OAuth" [immutable requirements + anti-patterns]
TaskCreate "Task 1: Configure OAuth provider"
# Execute → learn library handles refresh automatically
TaskCreate "Task 2: Integrate with existing middleware"
# Created AFTER learning from Task 1 — reflects reality
```

### Bad: Epic Without Anti-Patterns

```
TaskCreate subject: "Epic: OAuth"
  ## Requirements
  - Users authenticate via Google OAuth2
  - Tokens stored securely
# "Tokens stored securely" is vague
# No forbidden patterns → agent rationalizes localStorage when blocked
```

### Good: Epic With Anti-Patterns

```
TaskCreate subject: "Epic: OAuth"
  ## Requirements (IMMUTABLE)
  - Tokens stored in httpOnly cookies with Secure flag
  ## Anti-Patterns (FORBIDDEN)
  - NO localStorage tokens (reason: XSS vulnerability)
  - NO mocking OAuth in integration tests (reason: defeats purpose)
# Explicit reasoning prevents watering down under pressure
```

## Critical Rules

1. **Use AskUserQuestion tool** — don't print questions as text
2. **Research BEFORE proposing** — use Explore agent for codebase context
3. **Propose 2-3 approaches** — don't jump to a single solution
4. **Epic requirements IMMUTABLE** — tasks adapt, requirements don't
5. **Include anti-patterns** — prevents watering down under pressure
6. **Create ONLY first task** — subsequent tasks created iteratively
7. **Apply task refinement** — before handoff to executing-plans

**Common rationalizations (all mean STOP, follow the process):**
- "Requirements obvious" → Questions reveal hidden complexity
- "I know this pattern" → Research might show a better way
- "Can plan all tasks upfront" → Plans become brittle as you learn

## Verification Checklist

- [ ] Used AskUserQuestion tool (not printed text)
- [ ] Researched codebase patterns (Explore agent)
- [ ] Proposed 2-3 approaches with trade-offs
- [ ] Created epic with all required sections
- [ ] Anti-patterns include reasoning
- [ ] Rejected approaches have DO NOT REVISIT UNLESS
- [ ] Created ONLY first task (not full tree)
- [ ] Task refined: scoped, self-contained, explicit, testable

## Integration

**Calls:** Explore agent → hands off to `gambit:executing-plans`
