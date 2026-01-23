---
name: brainstorming
description: Use before any creative work - refines rough ideas into epic Tasks with immutable requirements through Socratic questioning
---

# Brainstorming Ideas Into Designs

## Overview

Turn rough ideas into validated designs stored as epic Tasks with immutable requirements. Tasks are created iteratively as you learn, not upfront.

**Core principle:** Ask questions to understand, research before proposing, document decisions for future reference.

**Announce at start:** "I'm using gambit:brainstorming to refine your idea into a design."

## Rigidity Level

HIGH FREEDOM - Adapt Socratic questioning to context. But always:
- Create immutable epic before code
- Create only first task (not full tree)
- Use AskUserQuestion tool for questions

## Quick Reference

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Ask questions (one at a time) | Understanding of requirements |
| 2 | Research (Explore agent for codebase) | Existing patterns and approaches |
| 3 | Propose 2-3 approaches with trade-offs | Recommended option |
| 4 | Present design in sections (200-300 words) | Validated architecture |
| 5 | Create epic Task with IMMUTABLE requirements | Epic with anti-patterns |
| 6 | Create ONLY first subtask | Ready for executing-plans |
| 7 | Hand off to executing-plans | Iterative implementation begins |

**Key:** Epic = contract (immutable), Tasks = adaptive (created as you learn)

## When to Use

- User describes new feature to implement
- User has rough idea that needs refinement
- About to write code without clear requirements
- Need to explore approaches before committing
- Requirements exist but architecture unclear

**Don't use for:**
- Executing existing plans (use `gambit:execute-plan`)
- Fixing bugs (use `gambit:debug`)
- Refactoring (use `gambit:refactor`)
- Requirements already crystal clear and epic exists

## The Process

### 1. Understanding the Idea

**Check current state:**
- Recent commits, existing docs, codebase structure
- Use Explore agent for existing patterns

```
Task
  subagent_type: "Explore"
  prompt: "Find existing auth implementation patterns in this codebase"
```

**REQUIRED: Use AskUserQuestion tool**

One question at a time. Multiple choice preferred.

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
        - label: "localStorage"
          description: "Persists across sessions, XSS vulnerable"
      multiSelect: false
```

**Question priorities:**
- **CRITICAL**: Must answer before proceeding (security, core functionality)
- **IMPORTANT**: Affects design significantly but has reasonable default
- **NICE_TO_HAVE**: Can defer to implementation phase

**Fast-path:** For IMPORTANT/NICE_TO_HAVE questions with good defaults, offer:
"Reply 'defaults' to accept all recommended options"

**CAPTURE for Design Discovery:**

As each question is answered, record in "Key Decisions Made":
- Question asked
- User's answer
- Implication for requirements/anti-patterns

This preserves context for task creation and obstacle handling.

### 2. Exploring Approaches

**Research first:**
- Similar feature exists → Explore agent
- New integration → WebSearch for docs
- Review findings before proposing

**CAPTURE for Design Discovery:**

Document:
- **Research Findings**: File paths, patterns, relevant code
- **Dead-End Paths**: Approaches explored and abandoned with reasons

Dead-end documentation prevents wasted re-investigation when obstacles arise.

**Propose 2-3 approaches with trade-offs:**

```
Based on [research findings], I recommend:

1. **[Approach A]** (recommended)
   - Pros: [benefits, especially "matches existing pattern"]
   - Cons: [drawbacks]

2. **[Approach B]**
   - Pros: [benefits]
   - Cons: [drawbacks]

3. **[Approach C]**
   - Pros: [benefits]
   - Cons: [drawbacks]

I recommend option 1 because [specific reason].
```

**Lead with recommended option and explain why.**

### 3. Presenting the Design

**Once approach is chosen, present design in sections:**
- Break into 200-300 word chunks
- Ask after each: "Does this look right so far?"
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify

**Show research findings:**
- "Based on codebase investigation: auth/ uses passport.js..."
- "API docs show OAuth flow requires..."
- Demonstrate how design builds on existing code

**CAPTURE for Design Discovery:**

When user raises concerns or "what if" questions:
- Record in "Open Concerns Raised" section
- Document how each was addressed or deferred

### 4. Creating the Epic Task

**After design validated, create epic as immutable contract:**

```
TaskCreate
  subject: "Epic: [Feature Name]"
  description: |
    ## Requirements (IMMUTABLE)
    [What MUST be true when complete - specific, testable]
    - Requirement 1: [concrete requirement]
    - Requirement 2: [concrete requirement]
    - Requirement 3: [concrete requirement]

    ## Success Criteria (MUST ALL BE TRUE)
    - [ ] Criterion 1 (objective, testable)
    - [ ] Criterion 2 (objective, testable)
    - [ ] All tests passing
    - [ ] Pre-commit hooks passing

    ## Anti-Patterns (FORBIDDEN)
    - NO [Pattern 1] (reason: [why forbidden])
    - NO [Pattern 2] (reason: [why forbidden])

    ## Approach
    [2-3 paragraph summary of chosen approach]

    ## Architecture
    [Key components, data flow, integration points]

    ## Design Rationale

    ### Problem
    [1-2 sentences: what problem this solves]

    ### Research Findings
    **Codebase:**
    - [file.ts:line] - [what it does, why relevant]
    - [pattern discovered, implications]

    **External:**
    - [API/library] - [key capability, constraint]

    ### Approaches Considered

    #### 1. [Chosen Approach] - CHOSEN
    **What it is:** [2-3 sentence description]
    **Investigation:** [What was researched]
    **Pros:** [benefits]
    **Cons:** [drawbacks]
    **Chosen because:** [specific reasoning]

    #### 2. [Rejected Approach] - REJECTED
    **What it is:** [2-3 sentence description]
    **Why explored:** [What made it seem viable]
    **Investigation:** [What was researched]
    **Pros:** [benefits]
    **Cons:** [fatal flaw]
    **REJECTED BECAUSE:** [specific reason]
    **DO NOT REVISIT UNLESS:** [condition that would change decision]

    ### Scope Boundaries
    **In scope:**
    - [explicit inclusions]

    **Out of scope:**
    - [explicit exclusions with reasoning]

    ### Open Questions
    - [uncertainties to resolve during implementation]

    ## Design Discovery (Reference Context)

    ### Key Decisions Made
    | Question | User Answer | Implication |
    |----------|-------------|-------------|
    | [question] | [answer] | [implication] |

    ### Research Deep-Dives
    [Detailed research findings for reference]

    ### Dead-End Paths
    [Approaches abandoned and why]

    ### Open Concerns Raised
    - [concern] → [resolution]
  activeForm: "Planning [feature name]"
```

**Critical:** Anti-patterns section prevents watering down requirements when blockers occur. Always include reasoning.

### 5. Creating ONLY First Task

**Create one task, not full tree:**

```
TaskCreate
  subject: "Add [specific deliverable]"
  description: |
    ## Goal
    [What this task delivers - one clear outcome]

    ## Implementation

    1. Study existing code
       [Point to 2-3 similar implementations: file.ts:line]

    2. Write tests first (TDD)
       [Specific test cases for this task]

    3. Implementation checklist
       - [ ] file.ts:line - function_name() - [what it does]
       - [ ] test.ts:line - test_name() - [what it tests]

    ## Success Criteria
    - [ ] [Specific, measurable outcome]
    - [ ] Tests passing
    - [ ] Pre-commit hooks passing
  activeForm: "Adding [deliverable]"
```

**Set dependency on epic:**

```
TaskUpdate
  taskId: "first-task-id"
  addBlockedBy: ["epic-task-id"]
```

Wait—actually subtasks should block the epic completion, not be blocked by it. Let me reconsider...

Actually, the dependency should show the task is part of the epic. Use metadata or just the description to link them. The epic stays in_progress while subtasks execute.

**Why only one task?**
- Subsequent tasks created iteratively by executing-plans
- Each task reflects learnings from previous
- Avoids brittle task trees that break when assumptions change

### 6. Apply Task Refinement

Before handoff, verify first task passes SRE criteria:
- Is it 2-5 minutes of work? (If longer, break down)
- Can it be executed without asking questions?
- Are all file paths explicit?
- Are success criteria specific and testable (at least 3)?

If task fails any check, update it with missing details.

### 7. Handoff

**Present handoff:**

```
Epic Task created with immutable requirements and success criteria.
First task is ready to execute.

Ready to start implementation? I'll use gambit:execute-plan to work through this iteratively.

The executing-plans skill will:
1. Execute the current task
2. Review what was learned against epic requirements
3. Create next task based on current reality
4. Repeat until all epic success criteria met

This approach avoids brittle upfront planning - each task adapts to what we learn.
```

## Task Tool Reference

### TaskCreate

```
TaskCreate
  subject: "Brief imperative title"
  description: "Full markdown with requirements, steps, code"
  activeForm: "Present participle for spinner"
```

### TaskUpdate

```
TaskUpdate
  taskId: "the-task-id"
  status: "pending" | "in_progress" | "completed"
  addBlockedBy: ["blocking-task-id"]
```

### TaskGet

```
TaskGet
  taskId: "the-task-id"
```

### TaskList

```
TaskList
```

## Key Principles

- **One question at a time** - Don't overwhelm
- **Multiple choice preferred** - Easier to answer when possible
- **Research before proposing** - Use Explore agent to understand context
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Epic is contract** - Requirements immutable, tasks adapt
- **Anti-patterns prevent shortcuts** - Explicit forbidden patterns stop rationalization
- **One task only** - Subsequent tasks created iteratively (not upfront)

## Examples

### Bad: Creating Full Task Tree Upfront

```
TaskCreate subject: "Epic: Add OAuth"
TaskCreate subject: "Task 1: Configure OAuth"
TaskCreate subject: "Task 2: Implement token exchange"
TaskCreate subject: "Task 3: Add refresh logic"
TaskCreate subject: "Task 4: Create middleware"
TaskCreate subject: "Task 5: Add UI components"
TaskCreate subject: "Task 6: Write tests"

# Starts Task 1
# Discovers library handles refresh automatically
# Now Task 3 is wrong
# Discovers middleware exists
# Now Task 4 is wrong
# Task tree brittle to reality
```

**Why it fails:**
- Assumptions prove wrong as you learn
- Task tree becomes incorrect
- Wastes time updating/deleting wrong tasks

### Good: Iterative Task Creation

```
TaskCreate subject: "Epic: Add OAuth" [with immutable requirements]
TaskCreate subject: "Task 1: Configure OAuth provider"

# Execute Task 1
# Learn: library handles refresh, middleware exists

TaskCreate subject: "Task 2: Integrate with existing middleware"
# Created AFTER learning from Task 1

# Execute Task 2
# Learn: UI needs OAuth button

TaskCreate subject: "Task 3: Add OAuth button to login"
# Created AFTER learning from Task 2
```

**Why it works:**
- Tasks reflect current reality
- No wasted time fixing wrong plans
- Epic requirements stay immutable

### Bad: Epic Without Anti-Patterns

```
TaskCreate
  subject: "Epic: OAuth Authentication"
  description: |
    ## Requirements
    - Users authenticate via Google OAuth2
    - Tokens stored securely

    ## Success Criteria
    - [ ] Login flow works
    - [ ] Tokens secured
```

**Why it fails:**
- No explicit forbidden patterns
- Agent rationalizes shortcuts when blocked
- "Tokens stored securely" too vague
- Mocking defeats the purpose of integration tests

### Good: Epic With Anti-Patterns

```
TaskCreate
  subject: "Epic: OAuth Authentication"
  description: |
    ## Requirements (IMMUTABLE)
    - Users authenticate via Google OAuth2
    - Tokens stored in httpOnly cookies (NOT localStorage)

    ## Success Criteria
    - [ ] Login redirects to Google and back
    - [ ] Tokens in httpOnly cookies
    - [ ] Integration tests pass WITHOUT mocking OAuth

    ## Anti-Patterns (FORBIDDEN)
    - NO localStorage tokens (reason: XSS vulnerability)
    - NO mocking OAuth in integration tests (reason: defeats validation)
    - NO new user model (reason: must use existing db/models/user.ts)

    ## Approaches Considered

    #### Custom JWT - REJECTED
    **REJECTED BECAUSE:** Would require rewriting 15 files
    **DO NOT REVISIT UNLESS:** Full auth system rewrite
```

**Why it works:**
- Requirements concrete and specific
- Forbidden patterns explicit with reasoning
- Can't rationalize away requirements
- Rejected approaches documented for obstacle handling

## Anti-patterns

**Don't:**
- Skip research, propose approach without checking codebase
- Create full task tree upfront
- Create epic without anti-patterns section
- Use open-ended questions when multiple choice works
- Print questions instead of using AskUserQuestion tool

**Do:**
- Research codebase first (Explore agent)
- Create only first task, iterate from there
- Include anti-patterns with reasoning
- Use AskUserQuestion tool for all clarifying questions
- Document rejected approaches with DO NOT REVISIT conditions

## Verification Checklist

Before handing off to executing-plans:

- [ ] Used AskUserQuestion tool for clarifying questions
- [ ] Researched codebase patterns (Explore agent)
- [ ] Proposed 2-3 approaches with trade-offs
- [ ] Presented design in sections, validated each
- [ ] Created epic Task with all sections
- [ ] Requirements are IMMUTABLE and specific
- [ ] Anti-patterns include reasoning
- [ ] Approaches Considered shows rejected options with DO NOT REVISIT
- [ ] Created ONLY first task (not full tree)
- [ ] First task has detailed implementation checklist
- [ ] Applied task refinement (2-5 min, explicit paths, testable criteria)

## Integration

**This skill is called by:**
- User requests for new features
- Beginning of greenfield development

**This skill calls:**
- Explore agent (understand existing code)
- `gambit:execute-plan` (handoff after design approved)

**Workflow:**
```
gambit:brainstorm
    → Create epic with immutable requirements
    → Create first task
    → Apply task refinement
gambit:execute-plan
    → Execute first task
    → Create next task based on learnings
    → Repeat until epic complete
```
