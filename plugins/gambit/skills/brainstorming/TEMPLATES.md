# Epic Contract and Worker Brief Templates

Full templates for drafting the epic contract and first-wave worker briefs before user review, then presenting the approved records in the root transcript. SKILL.md has condensed versions. Only concise wave summaries belong in the native plan.

## Epic Template

```
Draft for user review as "Epic: [Feature Name]":
    ## Requirements (IMMUTABLE)
    [Outcomes and guarantees, not incidental mechanisms. Include each requirement's basis:
    explicit user request, existing obligation, or necessary guarantee with failure/consequence.]
    - Requirement 1: [concrete requirement — basis]
    - Requirement 2: [concrete requirement — basis]
    - Requirement 3: [concrete requirement — basis]

    ## Success Criteria (MUST ALL BE TRUE)
    - [ ] Criterion 1 (objective, testable — e.g., 'Integration tests pass')
    - [ ] Criterion 2 (objective, testable — e.g., 'Works with existing User model')
    - [ ] All tests passing
    - [ ] Pre-commit hooks passing

    ## Anti-Patterns (FORBIDDEN)
    - NO [Pattern 1] (reason: [why forbidden])
    - NO [Pattern 2] (reason: [why forbidden])
    - NO [Pattern 3] (reason: [why forbidden])

    ## Quality Bar
    Failing, low-quality, or bad code is unacceptable, but failure to meet a mythic platonic
    ideal of code or cover literally every imaginable edge case is NOT itself a defect. This
    bar is FIXED for every epic; write it verbatim — never elicit it, strengthen it, or make it a
    per-project preference. A defect is exactly one of: a Requirement or Success Criterion not
    met; an Anti-Pattern present; a change outside the task's owned files; a violation of the
    worker contract's mechanical floor (a suppressed check, a weakened or tautological test,
    dead code, an unhandled error); or a security or data-loss failure with a reachable
    precondition. Everything else the orchestrator or a reviewer notices is an observation — it
    may be recorded, it never becomes work without the user. The craftsmanship asked of the
    worker is one line: simple, foundational, secure; match the surrounding code.

    ## Approach
    [Chosen implementation, revisable while preserving Requirements and explicit constraints.
    Approval of this approach does not independently promote its mechanisms into Requirements.]

    ## Architecture
    [Key components, data flow, integration points]

    ## Approaches Considered

    ### 1. [Chosen Approach] — CHOSEN
    **What:** [2-3 sentence description]
    **Investigation:** [What was researched]
    **Pros:** [benefits]
    **Cons:** [drawbacks]
    **Chosen because:** [specific reasoning]

    ### 2. [Rejected Approach] — REJECTED
    **What:** [2-3 sentence description]
    **Why explored:** [What made it seem viable]
    **Investigation:** [What was researched]
    **Pros:** [benefits]
    **Cons:** [fatal flaw]
    **REJECTED BECAUSE:** [specific reason]
    **DO NOT REVISIT UNLESS:** [condition that would change decision]

    ## Scope Boundaries
    **In scope:**
    - [explicit inclusions]

    **Out of scope:**
    - [explicit exclusions with reasoning]

    ## Delivery Constraints
    - Convergence circuit breaker: STOP autonomous continuation when two consecutive checkpoints
      retire no success criterion or named blocker, or when remaining work grows at both
      checkpoints. Report the evidence and require explicit user approval before changing scope,
      architecture, or the delivery budget.
    - Repair limit: one implementation, then at most one informed repair on the `escalation`
      rung. A task still NOT DONE after that repair is preserved uncommitted, marked
      `awaiting_user`, and checkpointed with its diff and one question; no worker, higher rung,
      judge, or renamed task continues it until the user answers. `repairs_used` and
      `awaiting_user` travel with the task through splits, renames, and Goal resumes.
    - Scope growth: every newly discovered worker must map to an immutable requirement, an
      admitted review-ledger finding, or a failing declared validation gate. A true observation
      alone does not authorize work. Optional improvements are not convergence milestones.
    - First deliverable: [smallest runnable path exercising required behavior through its real
      consumer; if prerequisites prevent that first, name the concrete dependency and next
      integration point, not a collection of hypothetical reusable foundations.]

    ## Validation Strategy
    - Focused worker command: [fast exact command each worker runs for its owned behavior]
    - Wave/component gate: [exact command run once on the integrated wave]
    - Release acceptance: [exact expensive end-to-end/system command, including freshness setup]
    - Acceptance budget: [normally one fresh run after implementation and architecture/scope
      preflight; name any additional allowed diagnostic run and what question it answers]

    ## Open Questions
    - [uncertainties to resolve during implementation]
    - [decisions deferred to execution phase]
```

### Anti-Pattern Examples

```
- NO localStorage tokens (reason: httpOnly prevents XSS token theft)
- NO new user model (reason: must integrate with existing db/models/user.ts)
- NO mocking OAuth in integration tests (reason: defeats purpose of testing real flow)
- NO Socket.IO (reason: user confirmed mobile clients use raw WebSocket)
- NO separate WebSocket port (reason: deployment complexity, firewall rules)
```

## First-Wave Worker Brief Template

```
Draft for user review as "Worker Brief: Add [specific deliverable]":
    ## Goal
    [What this task delivers — one clear outcome]

    ## Files owned
    [Exact repository-relative path allowlist. List every tracked or untracked text or binary
    artifact, deletion, symlink, and executable-mode change this worker may deliver. No globs or
    directories.]
    - exact/path/to/source.ext
    - exact/path/to/test.ext

    ## Hidden shared surfaces
    [Name implicit collision surfaces checked while forming the wave: lockfiles/manifests,
    generated code or indexes, migration sequences, registries/barrels, route tables, snapshot
    directories. Write `None` only after checking. Any surface this task will edit must also appear
    in Files owned; overlapping ownership moves the task to another wave.]

    ## Neighbors
    [For a parallel wave, give every concurrent worker's subject and exact Files owned allowlist;
    all are off-limits. For a single-task wave, write `None (single-task wave)`.]
    - [neighbor subject] — exact allowlist: [path/a, path/b] (off-limits)

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

    Test command: [exact focused worker command for this task]
```

For a fresh epic, obtain explicit user approval of the complete draft contract and every complete first-wave worker brief. Only after approval, present the full approved contract and every complete first-wave brief in the root transcript, then initialize the complete ordered wave list. A parallel first wave is one step regardless of its worker count:

```
SessionPlanWrite
  plan:
    - step: "Wave 1: Add [concise deliverable summary]"
      status: pending
```
