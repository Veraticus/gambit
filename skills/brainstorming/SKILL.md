---
name: brainstorming
description: Use before any creative work - refines rough ideas into epic Tasks with immutable requirements through Socratic questioning
user_invokable: true
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
- Run task refinement before handoff

## Quick Reference

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Ask questions (one at a time) | Understanding of requirements |
| 2 | Research (Explore agent for codebase) | Existing patterns and approaches |
| 3 | Propose 2-3 approaches with trade-offs | Recommended option |
| 4 | Present design in sections (200-300 words) | Validated architecture |
| 5 | Create epic Task with IMMUTABLE requirements | Epic with anti-patterns |
| 6 | Create ONLY first subtask | Ready for executing-plans |
| 7 | Apply task refinement | Corner cases covered |
| 8 | Hand off to executing-plans | Iterative implementation begins |

**Key:** Epic = contract (immutable), Tasks = adaptive (created as you learn)

## When to Use

- User describes new feature to implement
- User has rough idea that needs refinement
- About to write code without clear requirements
- Need to explore approaches before committing
- Requirements exist but architecture unclear

**Don't use for:**
- Executing existing plans (use `gambit:execute-plan`)
- Fixing bugs (use `gambit:debug` when available)
- Refactoring (use `gambit:refactor` when available)
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

**REQUIRED: Use AskUserQuestion tool with scannable format**

**Question Format Guidelines:**

1. **1-5 questions maximum** per round (don't overwhelm)
2. **Multiple choice preferred** with clear options
3. **Include suggested default** marked with "(Recommended)"
4. **Numbered for easy reference**
5. **Separate critical from nice-to-have**

**Question Structure:**
```
Question: [Clear question ending with ?]
Options:
  A. [Option] (Recommended) - [Why this is default]
  B. [Option] - [Trade-off]
  C. [Option] - [Trade-off]
  D. Other (please specify)

Priority: [CRITICAL | IMPORTANT | NICE_TO_HAVE]
```

**Priority Definitions:**
- **CRITICAL**: Must answer before proceeding (security, core functionality)
- **IMPORTANT**: Affects design significantly but has reasonable default
- **NICE_TO_HAVE**: Can defer to implementation phase

**Example using AskUserQuestion:**

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

**Fast-Path Option:**
For IMPORTANT/NICE_TO_HAVE questions with good defaults, offer:
"Reply 'defaults' to accept all recommended options"

**Do NOT just print questions and wait for "yes"** - use the AskUserQuestion tool.

**CAPTURE for Design Discovery:**

As each question is answered, record in "Key Decisions Made" table:
- Question asked
- User's answer
- Implication for requirements/anti-patterns

This preserves the Socratic Q&A for future reference during task creation and obstacle handling.

---

### 2. Exploring Approaches

**Research first:**
- Similar feature exists → Use Explore agent
- New integration → Use WebSearch or WebFetch
- Review findings before proposing

```
Task
  subagent_type: "Explore"
  prompt: "Find how authentication is currently implemented and what patterns are used"
```

**IMPORTANT: Capture research findings for Design Discovery**

As you research, note down:
- Codebase findings: file paths, patterns discovered, relevant code
- External findings: API capabilities, library constraints, doc URLs
- These will populate the "Research Findings" section of the epic

**CAPTURE for Design Discovery:**

- **Research Deep-Dives**: For each major research topic, document:
  - Question explored
  - Sources consulted with key findings
  - Conclusion and how it informed the design
- **Dead-End Paths**: When you abandon an approach during research:
  - Why you explored it (what made it seem viable)
  - What investigation revealed
  - Why abandoned (specific reason linking to requirements/constraints)

Dead-end documentation prevents wasted re-investigation when obstacles arise later.

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

I recommend option 1 because [specific reason, especially codebase consistency].
```

**Lead with recommended option and explain why.**

---

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

When user raises concerns, hesitations, or "what if" questions:
- Record in "Open Concerns Raised" section
- Document how each was addressed or deferred
- Example: "What if Google OAuth is down?" → "Graceful degradation to error message"

These concerns often resurface during implementation - having the resolution documented prevents re-debating.

---

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
    - [ ] Criterion 1 (objective, testable - e.g., 'Integration tests pass')
    - [ ] Criterion 2 (objective, testable - e.g., 'Works with existing User model')
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
    [1-2 sentences: what problem this solves, why status quo insufficient]

    ### Research Findings
    **Codebase:**
    - [file.ts:line] - [what it does, why relevant]
    - [pattern discovered, implications]

    **External:**
    - [API/library] - [key capability, constraint discovered]
    - [doc URL] - [relevant guidance found]

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
    - [decisions deferred to execution phase]

    ## Design Discovery (Reference Context)

    > This section preserves detailed context from brainstorming for task creation.
    > Reference when defining tasks, handling obstacles, or validating decisions.

    ### Key Decisions Made
    | Question | User Answer | Implication |
    |----------|-------------|-------------|
    | [question] | [answer] | [implication] |

    ### Research Deep-Dives
    #### [Topic: e.g., OAuth Library Selection]
    **Question explored:** [What question drove this research?]
    **Sources consulted:**
    - [Source 1] - [key finding]
    **Findings:** [Detailed findings]
    **Conclusion:** [How this informed the design]

    ### Dead-End Paths
    #### [Path: e.g., Custom JWT Implementation]
    **Why explored:** [What made this seem worth investigating]
    **Investigation:** [What was researched/tried]
    **Why abandoned:** [Specific reason - links to requirements/anti-patterns]

    ### Open Concerns Raised
    - [concern] → [resolution]
  activeForm: "Planning [feature name]"
```

**Critical:** Anti-patterns section prevents watering down requirements when blockers occur. Always include reasoning.

**Example anti-patterns:**
- NO localStorage tokens (reason: httpOnly prevents XSS token theft)
- NO new user model (reason: must integrate with existing db/models/user.ts)
- NO mocking OAuth in integration tests (reason: defeats purpose of testing real flow)

---

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

**Link task to epic using metadata or description reference.**

The subtask is part of the epic. Epic stays in_progress while subtasks execute.

**Why only one task?**
- Subsequent tasks created iteratively by executing-plans
- Each task reflects learnings from previous
- Avoids brittle task trees that break when assumptions change

---

### 6. Apply Task Refinement

**REQUIRED: Before handoff, verify first task passes these criteria:**

1. **Is it 2-5 minutes of work?** (If longer, break down)
2. **Can it be executed without asking questions?** (All info present)
3. **Are all file paths explicit?** (No searching required)
4. **Are success criteria specific and testable?** (At least 3 criteria)

**Corner-case analysis checklist:**
- [ ] What happens if the happy path fails?
- [ ] What are the edge cases for inputs?
- [ ] What happens on network/IO failures?
- [ ] What happens on concurrent access?
- [ ] What happens with empty/null/missing data?
- [ ] What are the security implications?
- [ ] What happens at boundaries (max size, timeout)?

If task fails any check, update it with missing details before proceeding.

---

### 7. Documentation (Optional but Recommended)

**Write validated design to docs:**

```bash
# Create design document
# File: docs/plans/YYYY-MM-DD-<topic>-design.md
```

Include:
- Problem statement
- Chosen approach with rationale
- Architecture overview
- Key decisions made
- Anti-patterns to avoid

**Commit the design document** before starting implementation.

---

### 8. Handoff

**After refinement complete, present handoff:**

```
Epic Task created with immutable requirements and success criteria.
First task is ready to execute and has been refined.

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

**Epic example:**
```
TaskCreate
  subject: "Epic: OAuth Authentication"
  description: |
    ## Requirements (IMMUTABLE)
    - Users authenticate via Google OAuth2
    - Tokens stored in httpOnly cookies (NOT localStorage)

    ## Success Criteria (MUST ALL BE TRUE)
    - [ ] Login redirects to Google and back
    - [ ] Tokens in httpOnly cookies
    - [ ] Integration tests pass WITHOUT mocking OAuth
    - [ ] All tests passing
    - [ ] Pre-commit hooks passing

    ## Anti-Patterns (FORBIDDEN)
    - NO localStorage tokens (reason: XSS vulnerability)
    - NO mocking OAuth in integration tests (reason: defeats validation)
  activeForm: "Planning OAuth authentication"
```

**Task example:**
```
TaskCreate
  subject: "Configure Google OAuth provider"
  description: |
    ## Goal
    Set up Google OAuth credentials and basic passport strategy.

    ## Implementation
    1. Study auth/strategies/local.ts:1-30 for strategy pattern
    2. Write test: OAuth callback returns user profile
    3. Add passport-google-oauth20 to package.json
    4. Create auth/strategies/google.ts following local.ts pattern

    ## Success Criteria
    - [ ] passport-google-oauth20 installed
    - [ ] auth/strategies/google.ts exists
    - [ ] OAuth strategy registered in passport config
    - [ ] Tests passing
  activeForm: "Configuring OAuth provider"
```

### TaskUpdate

```
TaskUpdate
  taskId: "the-task-id"
  status: "pending" | "in_progress" | "completed"
  description: "Updated description if needed"
```

### TaskGet

```
TaskGet
  taskId: "the-task-id"
```

Use to read full task details including success criteria.

### TaskList

```
TaskList
```

Returns all tasks with status. Use to verify epic and subtasks.

## Research Agents

### Use Explore agent when:
- Understanding how existing features work
- Finding where specific functionality lives
- Identifying patterns to follow
- Verifying assumptions about structure
- Checking if feature already exists

```
Task
  subagent_type: "Explore"
  prompt: "Find existing authentication patterns in this codebase"
```

### Use WebSearch when:
- Finding current API documentation
- Researching library capabilities
- Comparing technology options
- Understanding community recommendations

### Research protocol:
1. Codebase pattern exists → Use it (unless clearly unwise)
2. No codebase pattern → Research external patterns
3. Research yields nothing → Ask user for direction

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

### Good: Epic With Anti-Patterns and Design Rationale

```
TaskCreate
  subject: "Epic: OAuth Authentication"
  description: |
    ## Requirements (IMMUTABLE)
    - Users authenticate via Google OAuth2
    - Tokens stored in httpOnly cookies (NOT localStorage)
    - Integrates with existing User model at db/models/user.ts

    ## Success Criteria (MUST ALL BE TRUE)
    - [ ] Login redirects to Google and back
    - [ ] Tokens in httpOnly cookies
    - [ ] Token refresh works automatically
    - [ ] Integration tests pass WITHOUT mocking OAuth
    - [ ] All tests passing
    - [ ] Pre-commit hooks passing

    ## Anti-Patterns (FORBIDDEN)
    - NO localStorage tokens (reason: XSS vulnerability)
    - NO new user model (reason: must use existing db/models/user.ts)
    - NO mocking OAuth in integration tests (reason: defeats validation)
    - NO skipping token refresh (reason: explicit user requirement)

    ## Approach
    Extend existing passport.js setup at auth/passport-config.ts with
    Google OAuth2 strategy. Use passport-google-oauth20 library.
    Store tokens in httpOnly cookies via express-session.
    Integrate with existing User model for profile storage.

    ## Architecture
    - auth/strategies/google.ts - New OAuth strategy
    - auth/passport-config.ts - Register strategy (existing)
    - db/models/user.ts - Add googleId field (existing)
    - routes/auth.ts - OAuth callback routes

    ## Design Rationale

    ### Problem
    Users currently have no SSO option - must create accounts manually.
    Manual signup has 40% abandonment rate. Google OAuth reduces friction.

    ### Research Findings
    **Codebase:**
    - auth/passport-config.ts:1-50 - Existing passport setup, uses sessions
    - auth/strategies/local.ts:1-30 - Pattern for adding strategies
    - db/models/user.ts:1-80 - User model, already has email field

    **External:**
    - passport-google-oauth20 - Official Google strategy, 2M weekly downloads
    - Google OAuth2 docs - Requires client ID, callback URL, scopes

    ### Approaches Considered

    #### 1. Extend passport.js with google-oauth20 - CHOSEN
    **What it is:** Add passport-google-oauth20 strategy to existing setup.
    Reuses session-based auth, follows existing pattern in auth/strategies/.

    **Investigation:**
    - Reviewed auth/passport-config.ts - existing passport setup
    - Checked auth/strategies/local.ts - pattern for adding strategies
    - passport-google-oauth20 npm - 2M weekly downloads, maintained

    **Pros:**
    - Matches existing codebase pattern (auth/strategies/)
    - Session handling already works
    - Well-documented, large community

    **Cons:**
    - Adds npm dependency

    **Chosen because:** Consistent with existing pattern, minimal changes

    #### 2. Custom JWT-based OAuth - REJECTED
    **What it is:** Implement OAuth from scratch using JWTs instead of sessions.

    **Why explored:** User mentioned 'maybe we should use JWTs'

    **Investigation:**
    - Counted files using req.session - 15 files would need rewriting
    - Reviewed existing session middleware - deeply integrated

    **Pros:**
    - No new dependencies
    - Stateless (scalability)

    **Cons:**
    - Would require rewriting 15 files
    - Security complexity
    - Breaks existing pattern

    **REJECTED BECAUSE:** Scope creep - OAuth shouldn't require rewriting auth.

    **DO NOT REVISIT UNLESS:** Full auth system rewrite in separate epic.

    ### Scope Boundaries
    **In scope:**
    - Google OAuth login/signup
    - Token storage in httpOnly cookies
    - Profile sync with User model

    **Out of scope:**
    - Other OAuth providers (deferred to future epic)
    - Account linking (deferred)

    ### Open Questions
    - Should failed OAuth create partial user record? (decide during impl)
    - Token refresh: silent vs prompt? (default to silent)

    ## Design Discovery (Reference Context)

    ### Key Decisions Made
    | Question | User Answer | Implication |
    |----------|-------------|-------------|
    | Token storage? | httpOnly cookies | Anti-pattern: NO localStorage |
    | New or existing user model? | Existing | Must add googleId field |
    | Session duration? | 24h inactive | Need refresh token logic |
    | OAuth down fallback? | Error message | No fallback auth needed |

    ### Research Deep-Dives

    #### OAuth Library Selection
    **Question explored:** Which OAuth library to use?
    **Sources consulted:**
    - passport-google-oauth20 npm - 2M weekly downloads
    - google-auth-library npm - official but lower-level

    **Findings:**
    - passport-google-oauth20 matches existing passport setup
    - Built-in session serialization

    **Conclusion:** Use passport-google-oauth20 for consistency

    ### Dead-End Paths

    #### Custom JWT Implementation
    **Why explored:** User mentioned JWTs
    **Investigation:** Counted 15 files using req.session
    **Why abandoned:** Scope creep, breaks existing pattern

    ### Open Concerns Raised
    - 'What if Google OAuth is down?' → Graceful error message
    - 'Should we support account linking?' → Deferred to future epic
  activeForm: "Planning OAuth authentication"
```

**Why it works:**
- Requirements concrete and specific
- Forbidden patterns explicit with reasoning
- Can't rationalize away requirements
- Rejected approaches documented for obstacle handling
- Design Discovery preserves full context

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

## Critical Rules

### Rules That Have No Exceptions

1. **Use AskUserQuestion tool** → Don't just print questions and wait
2. **Research BEFORE proposing** → Use Explore agent to understand context
3. **Propose 2-3 approaches** → Don't jump to single solution
4. **Epic requirements IMMUTABLE** → Tasks adapt, requirements don't
5. **Include anti-patterns section** → Prevents watering down requirements
6. **Create ONLY first task** → Subsequent tasks created iteratively
7. **Apply task refinement** → Before handoff to executing-plans

### Common Excuses

All of these mean: **STOP. Follow the process.**

| Excuse | Reality |
|--------|---------|
| "Requirements obvious, don't need questions" | Questions reveal hidden complexity |
| "I know this pattern, don't need research" | Research might show better way |
| "Can plan all tasks upfront" | Plans become brittle as you learn |
| "Anti-patterns section overkill" | Prevents rationalization under pressure |
| "Epic can evolve" | Requirements contract, tasks evolve |
| "Can just print questions" | Use AskUserQuestion tool - more interactive |
| "Task refinement overkill" | First task sets pattern for entire epic |

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
- [ ] Design Discovery section captures Q&A, research, dead-ends
- [ ] Created ONLY first task (not full tree)
- [ ] First task has detailed implementation checklist
- [ ] Applied task refinement (2-5 min, explicit paths, testable criteria)

## Resources

**When stuck:**
- User gives vague answer → Ask follow-up multiple choice question
- Research yields nothing → Ask user for direction explicitly
- Too many approaches → Narrow to top 2-3, explain why others eliminated
- User changes requirements mid-design → Acknowledge, return to understanding phase

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
