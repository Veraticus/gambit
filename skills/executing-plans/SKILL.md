---
name: executing-plans
description: Executes an approved epic one wave at a time, dispatching a worker per task and stopping at a checkpoint after each wave.
when_to_use: Use when an epic Task exists and subtasks are ready to implement, when resuming work after a previous checkpoint, when iteratively building a feature, or when implementation has revealed unexpected work that needs a new task. User phrases like "continue the plan", "next task", "resume where we left off", "pick up the epic".
user_invokable: true
---

# Executing Plans

**Freedom: LOW** — load epic, execute one wave, checkpoint, STOP.

## Overview

Execute an epic in cycles with mandatory checkpoints. Load epic → run one wave (one task, or several independent tasks in parallel) → Present checkpoint → STOP. User reviews, then invokes again to continue.

**Core principle:** Epic requirements are immutable. Tasks adapt to reality. STOP after each wave for human oversight — no exceptions. A wave of independent parallel tasks is one cycle with one checkpoint; running a *second* wave without stopping is the batching that's forbidden.

**Announce at start:** "I'm using gambit:executing-plans to implement this task."

## Execution and continuation

Each invocation runs **one cycle** — execute the ready work, verify, run the checkpoint gate, commit, present the checkpoint — then **STOPs (ends the turn)**. The skill never loops across cycles within a single turn.

STOP does not mean the epic halts; it means this turn ends and the next cycle begins on the next invocation. Two things can trigger that next invocation:
- **A human** re-running `/gambit:executing-plans` — the default.
- **A goal Stop-hook** that re-invokes the skill automatically — the ONLY sanctioned way to run cycle-after-cycle without a human pause.

Continuous, no-human-pause execution is therefore **authorized only by a goal Stop-hook — never self-granted.** An in-session "just keep going, don't stop for me" does NOT authorize it: if the user wants unattended execution they set a goal; surface that in the checkpoint rather than batching cycles yourself. Every safeguard — checkpoint gate, repair limit, commit, checkpoint summary, and this re-invocation — runs on every cycle regardless; the goal changes only who triggers the next one, never what happens inside a cycle. A task marked `awaiting_user` stays that way across goal-driven cycles: continuation re-invokes the skill, it never answers the question.

## Quick Reference

| Step | Action | Critical Rule |
|------|--------|---------------|
| **0. Check State** | `TaskList` | Task state tells you where to resume — never ask |
| **1. Load Epic + Enter Worktree** | `TaskGet` on epic; enter/re-enter the epic worktree | Requirements are IMMUTABLE; never execute on main |
| **2. Execute the Wave** | Mark in_progress → dispatch worker(s) → verify → integrate → mark completed | Explicit worker rung, TDD cycle, worktree-isolate a ≥2 wave |
| **3. Create Next Wave** | `TaskCreate` every pluckable task based on learnings | As wide as pluckability allows; disjoint file sets; reflect reality |
| **4. Commit & Checkpoint** | Commit to current branch, present summary | STOP — no exceptions |

**Iron Law:** One wave → Checkpoint → STOP → Next cycle. No batching (no second wave this cycle). No "just one more." The STOP always happens; whether a human or a goal Stop-hook triggers the next cycle is the only thing that varies (see **Execution and continuation**).

## When to Use

- Epic Task exists with subtasks ready to execute
- Resuming implementation after a previous checkpoint
- Need to implement features iteratively with human oversight
- After `gambit:brainstorming` creates the epic and first task

**Don't use when:**
- No epic exists → use `gambit:brainstorming`
- Debugging a bug → use `gambit:debugging`
- Single quick fix → just do it

## The Process

### 0. Resumption Check (Every Invocation)

Run `TaskList` and analyze:

- **Fresh start:** All tasks "pending", none "in_progress" → Step 1
- **Resume in-progress:** Found task with status="in_progress" → Step 2
- **Start next:** Previous completed, next "pending" with empty blockedBy → Step 1 then 2
- **All done:** All subtasks "completed" → Step 5 (final validation)

**Do NOT ask "where did we leave off?"** — Task state tells you exactly where to resume. Before choosing work on resume, read each in-progress task's `repairs_used` and `awaiting_user` fields. A task marked `awaiting_user` is not work: leave its `parked/<task-slug>` branch untouched, restate its question in this cycle's checkpoint, and take other ready tasks whose files are disjoint from it; if nothing else is ready, STOP with the question. Nothing re-dispatches, splits, renames, or escalates a parked task — only the user's answer does. A `pending` task with no repair fields is fresh and gets them when claimed (Step 2); an `in_progress` task with no repair fields cannot be told apart from one that lost them, and is treated as `awaiting_user`.

**If the task store is empty or wiped** (e.g. an MCP reconnect drops the session's tasks mid-epic), recreate the epic and the in-flight tasks from your own context, carrying each task's `repairs_used` and `awaiting_user` forward. A task whose repair state you cannot recover is recreated as `awaiting_user`; a wipe never grants a fresh repair.

---

### 1. Load Epic Context and Enter the Worktree

Before executing ANY task, read the epic with `TaskGet`.

**Extract and keep in mind:**
- Requirements (IMMUTABLE — never water these down)
- Success criteria (validation checklist)
- Anti-patterns (FORBIDDEN shortcuts)
- Approaches Considered (what was already REJECTED and why)
- Delivery Constraints (the convergence circuit breaker and the one-repair limit)
- Validation Strategy (focused worker command, wave/component gate, release acceptance, freshness, and declared acceptance budget)

**Why:** Requirements prevent rationalizing shortcuts when implementation gets hard.

For a legacy epic that lacks Delivery Constraints or Validation Strategy, do not guess silently. Before implementation, propose the conservative defaults from this skill — the two-checkpoint convergence circuit breaker, the one-repair limit, focused and wave/component commands from repository policy, and one fresh release acceptance run after architecture/scope preflight — then obtain explicit user approval. Agent-generated legacy retry boilerplate is replaced by this bounded policy even when the epic already has Delivery Constraints; it never preserves extra automatic retries. An explicit conflicting user-selected continuation policy requires clarification rather than silent override. This records delivery policy without changing immutable product requirements.

**Enter the epic worktree.** All epic work happens in a worktree — never directly on main. Working on main risks orphaned commits and a corrupted mainline while waves land.

On a **fresh start** (Step 0 found all tasks pending):

1. **Repo convention first.** If the repo provides its own worktree setup (an existing `.worktrees/` or `worktrees/` directory, a CLAUDE.md worktree preference, or project tooling like a `just worktree` target), follow it: `git worktree add <dir>/<epic-slug> -b <branch>` and work there.
2. **Otherwise use the native facility:** `EnterWorktree name: "<epic-slug>"` — creates the worktree under `.claude/worktrees/` on a new branch and switches the session into it. The base ref follows the `worktree.baseRef` setting (`fresh` = origin default branch; `head` = current HEAD).

Then prepare it: run the project's dependency setup (match the tooling — `npm install`, `cargo build`, `direnv allow`/devenv, etc.), and run the declared wave/component gate once to pin the baseline. Report baseline failures before dispatching any wave — you can't distinguish new breakage from inherited breakage without this. Do not spend release acceptance merely to establish a baseline unless the approved Validation Strategy explicitly budgets that run.

On **resume**: if the session is already in the epic's worktree, continue. In a fresh session, re-enter it — `EnterWorktree path: "<worktree path>"` for a native one (it must appear in `git worktree list`), or switch to a repo-managed one directly. Never dispatch a wave from main.

The transient per-worker worktrees of a ≥2 wave (`references/wave-dispatch.md`) fork off THIS worktree's HEAD — they are orchestrator-managed and separate from the epic workspace.

---

### 2. Execute the Wave

**Find and claim the wave:**
1. `TaskList` → identify the ready tasks (status="pending", blockedBy=[]). The wave is those whose file sets are pairwise disjoint with no cross-dependency — usually one, sometimes several. Overlapping or dependent tasks wait for a later wave. A parked task (`awaiting_user`) is never ready, and its `parked/<task-slug>` branch stays untouched.
2. `TaskUpdate` → mark each wave task in_progress; for a task claimed for the first time, set its metadata `repairs_used: 0` and `awaiting_user: false` in the same update — these two fields are the task's whole repair state, and they live nowhere else
3. `TaskGet` → load each task's full details

**Investigate first if needed — reach for a scout.** Before constructing the worker brief, if you need to locate code, confirm an interface, or gather cross-task context, dispatch the read-only **scout class** — don't read around inline or spawn a bare generic agent. This is optional per task; skip it when the brief is already clear.

Glob `**/contracts/scout.md`. Resolve the `scout` role through `contracts/models.md` to its
rung. On a model rung, dispatch `subagent_type: "Explore"` with `model:` set to the rung's alias;
an agent rung uses the rung's `readonly_agent` and passes no `model:` at all. Either way,
prompt it to Read `contracts/scout.md` first, then ask the bounded question with the task's
repository/worktree root.

The scout returns `file:line` evidence or `NOT FOUND` — never a guess.

**Settle architecture before dispatching.** A worker implements; it does not decide cross-file design. If a task carries an unresolved architectural question, resolve it first — scout it, record the decision in the brief, or decompose the task — then dispatch. A design question tangled into an implementation task is what produces same-pass-TDD drift.

**Apply the declared validation ladder.** The focused worker command proves the worker-owned behavior during TDD. The wave/component gate proves the integrated wave once. Release acceptance proves the final system claim on fresh artifacts within the approved budget. Release acceptance is not a per-worker or per-wave default; run it early only when the contract budgets a diagnostic run that answers a named system-level question.

**Answer the user before you dispatch.** When the user asks a direct question mid-epic, answer it in prose before or alongside your next action. A dispatch, a task update, or a checkpoint summary is never a substitute for the answer. Deferring a question to "keep the loop moving" is the drift, not the discipline; if you can't answer, say so plainly rather than fabricating (e.g. per-worker token cost isn't surfaced to you — point the user at the session telemetry, don't guess a number).

**Dispatch the wave to workers:**

The ready work is a **wave** — one or more ready tasks whose file sets are **pairwise disjoint** and that have **no semantic dependency** on each other (a task needing another's output belongs in a later wave). One cycle dispatches one wave. The orchestrator does not write implementation code in the main context and stays a coordinator: it plans, verifies, integrates, and checkpoints while a fresh worker on the resolved `worker` rung does the mechanical work. Every worker is governed by the shared **`contracts/worker.md`** — blast-radius confinement, TDD with RED/GREEN evidence, fail-fast Stop Triggers, and a 4-state return.

- **Single-task wave** → dispatch one worker; it works directly in the epic's working tree.
- **Wave of ≥2** → run each worker in its OWN isolated worktree so their tests, lints, and builds cannot interfere; give every brief exact `## Files owned`, `## Hidden shared surfaces`, and `## Neighbors` allowlists; then use `scripts/integrate_wave.py` for commit-based atomic integration and one combined wave/component gate. Never let two workers edit the same working tree. Full mechanics: **`references/wave-dispatch.md`** — read it whenever a wave has ≥2 tasks.

**Resolve the contract path once.** Glob `**/contracts/worker.md` at the start of the epic to get its absolute path and pass that path to the worker — **do NOT Read `worker.md` into your own context**, and **do NOT hardcode or reuse a stale absolute path from an earlier session** (plugin store paths change; re-Glob). The worker reads it in its fresh context (exactly as the `review` skill passes `reviewers/*.md` by path); reading it yourself loads ~1.4k tokens into the long-lived orchestrator context on every epic, for nothing. The worker re-reads it on every dispatch, including retries — keep `worker.md` lean.

1. **Resolve the worker rung.** Resolve the `worker` role through `contracts/models.md` before the initial dispatch. Use the role's entry rung, or a higher rung on its ladder when the task brief states difficulty that warrants it — never a rung below the entry, and never a rung the worker picks for itself. On a model rung, **always set `model:` explicitly to the rung's alias — never omit it, never pass `inherit`** (that silently inherits the expensive session model). On an agent rung, dispatch the rung's `agent` and pass **no `model:` at all** — a foreign model id in `model:` is silently substituted rather than rejected. **Never write a concrete model ID into this skill.**

2. **Dispatch the wave** — emit every worker together in one message so a ≥2 wave runs concurrently.

   The prompt starts with the absolute worker-contract directive, then contains the complete constructed brief and its exact `## Files owned`, `## Hidden shared surfaces`, `## Context`, and `## Neighbors`; the focused command, exact worktree and branch, and correct wave base; never session history:
   ```
   Agent subagent_type="general-purpose" model="<worker rung alias — contracts/models.md>" description="Implement: <task subject>"
     prompt="Read <abs>/contracts/worker.md first and follow it exactly. <complete constructed brief and dispatch fields described above>"
   ```

   On an agent rung the same dispatch becomes `Agent subagent_type="<worker rung agent>"` with the `model=` field removed entirely; the prompt is unchanged. Worktree isolation and `integrate_wave.py` are unchanged either way.

   Pass the contract by path and the task as **constructed text** — never paste your session history into the worker prompt. **Optional project briefs:** gambit ships no per-language briefs. If a project provides a `contracts/<lang>.md` for the task's language, add a line telling the worker to read it too — optional, never required; dispatch is fully functional with `worker.md` alone.

3. **Route on the worker's returned status** (the contract defines four). The repair limit is fixed: one implementation, then at most one informed repair on the `escalation` rung, then the user. Before any corrective dispatch, read the task's `repairs_used`; if it is already `1`, or the task is `awaiting_user`, there is no dispatch to make — preserve the work and go to the checkpoint with the question:
   - **DONE** → single-task wave: verify with FRESH evidence by running its focused worker command. Wave of ≥2: confirm the worker's isolated RED/GREEN evidence and rerun only a missing worker-scoped check; the declared wave/component gate belongs to the combined manifest and runs exactly once. Then run the **Checkpoint gate** (below) on that worker's complete change set before proceeding. Copy the worker's `## Notes` into the checkpoint's Notes; they are for the user and create no task.
   - **DONE_WITH_CONCERNS** → read the concern. A doubt about a behavior the brief names, or about the floor in the worker's own diff, is a NOT DONE item for the checkpoint gate: it routes as the one informed repair, never to a reviewer. Anything the worker put under `## Notes` is verified as DONE and recorded, not acted on. **A "bigger behavior change than the brief implied" flag usually means the brief was wrong, not the worker** — re-read the requirement the worker cites and fix the brief, don't wave the flag through because the worker followed instructions literally. A worker's scope-surprise is often your spec catching itself.
   - **NEEDS_CONTEXT** → supply the missing values/decisions and re-dispatch on the same rung with them added; this is still the first implementation, not a repair. A second NEEDS_CONTEXT on the same task means the brief cannot be written from what you know: mark it `awaiting_user` and checkpoint with the exact missing decision.
   - **BLOCKED** → act by cause: missing context → add it + re-dispatch, as for NEEDS_CONTEXT; needs more reasoning → that is the one informed repair on the `escalation` rung; task too large → decompose ONCE into new tasks (`TaskCreate`) that start at `repairs_used: 0`, and mark the parent SKIPPED in favor of them — a task that was itself produced by decomposition is never decomposed again, and if it returns BLOCKED it is `awaiting_user`; the plan/brief itself is wrong → STOP and escalate to the user. Do NOT water down requirements.

     **The one informed repair.** Resolve the `escalation` role through `contracts/models.md` and dispatch a fresh agent on that rung, reusing the same absolute worker contract path and complete brief plus the exact NOT DONE list — for each item its baseline clause, the changed-code cause, and the evidence (failing output, `file:line`). Record `repairs_used: 1` on the task's metadata with `TaskUpdate` BEFORE dispatching. There is no second repair, no climb beyond this rung, and no renamed or split descendant that starts fresh; if the repair returns anything but DONE, the task is `awaiting_user` and its work is parked.

     **Parking.** A task that becomes `awaiting_user` keeps its work on its own branch, never in the epic's working tree, so the epic tree stays clean for the wave gate and for other tasks. In the tree that holds the diff (the epic worktree for a single-task wave, the worker's own worktree for a wave of ≥2): `git switch -c parked/<task-slug>` (the uncommitted changes come along), stage exactly the task's `Files owned` including untracked artifacts, commit with subject `parked: <task subject> — awaiting user`, then `git switch` back to the epic branch, which leaves the tree clean at the epic HEAD. Set `awaiting_user: true` and record the branch name in the same `TaskUpdate`. The parked commit is not on the epic branch and is never integrated until the user answers; the answer decides whether a repair worker starts from that commit, the work is accepted as is, or the branch is dropped:
     ```
     Agent subagent_type="general-purpose" model="<escalation rung alias — contracts/models.md>" description="Repair: <task subject>"
       prompt="<same absolute worker contract path directive, complete worker brief, and the NOT DONE list>"
     ```
     On an agent rung, drop the `model=` field and set `subagent_type="<escalation rung agent>"` instead.

**One of the four statuses is the ONLY signal that advances a task — silence is not one of them.** A worker that has not returned DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED is still working, even when it looks otherwise. A worker spends a long opening stretch reading, grepping, and reasoning before it writes a single byte — so a **flat `git status`, an unchanged diff across several checks, and an unanswered status ping are indistinguishable from a dead worker but are not one.** Worker↔orchestrator messaging also lags: a worker deep in work often does not read its inbox for a while, and its replies can arrive minutes after you'd expect (sometimes crossing your own next message). **Do not presume a silent worker is dead, and above all do not spawn a replacement on silence alone** — re-dispatching a still-live worker onto its own task and tree manufactures a file collision (two workers editing the same files), the single most expensive and recurrent orchestration mistake. If you genuinely must probe, send **one** status ping framed as informational ("not a stand-down — where are you?") and wait a full cycle; only a returned BLOCKED/failure, or a process you have confirmed dead by other means, justifies re-dispatch. When a collision does happen anyway, workers detect it (`## Neighbors` / blast-radius) and stand down cleanly — so before integrating a tree two workers may have touched, confirm it has been **stable across a couple of checks** (no files changing under you) and rerun its worker-scoped verification. Invoke the manifest's combined wave/component gate only after every tree is stable and accepted. Patience here is not idleness; it is the cheapest thing you will do all epic.

4. **Integrate the wave atomically — you are the sole committer.** Workers edit; you judge each complete diff before integration. Single-task wave → gate the diff, run its focused worker command, then run the declared wave/component gate once on the integrated epic HEAD and commit at the checkpoint (Step 4a). Wave of ≥2 → after every per-worker checkpoint gate returns DONE, create the ordered JSON manifest and run `scripts/integrate_wave.py` as specified in `references/wave-dispatch.md`, using the declared wave/component gate as its combined gate. Workers never commit. While a wave runs, scout and brief the next wave rather than idling.

    The ≥2-wave transaction is ordered and indivisible:

    1. **Validate inputs.** Reject overlapping exact allowlists, verify the epic and all workers at the shared base, and build each complete worker tree through a temporary index without changing the worker's real staged or unstaged state.
    2. **Combine ordered commits.** Create one distinct commit object per worker, then cherry-pick them in manifest order on the detached integration worktree.
    3. **Run one combined gate.** Run the declared wave/component gate exactly once on the combined detached HEAD and require its worktree to remain fully clean.
    4. **Fast-forward the exact tested head.** Revalidate the epic and every worker after the gate, then fast-forward the epic only to that exact passing combined HEAD.
    5. **Clean up only after success.** Remove transient worker and integration worktrees only after the exact-head fast-forward succeeds. Validation, conflict, gate, revalidation, or fast-forward failure leaves epic HEAD unmoved and retains every worktree and artifact for inspection.

**What you do yourself vs dispatch.** Two kinds of task the orchestrator executes directly; everything else is dispatched to a worker:
- **Non-code tasks** (pure docs, task bookkeeping) — there's no implementation to delegate.
- **Aesthetic-judgment tasks** (visual design, layout, typography, art direction — success is *does it look right*, not a functional spec) — the ONE code exception to dispatch, because visual taste is the orchestrator's strength and a worker's weakness. Exact-spec mechanical markup is NOT this exception — dispatch that normally.

Everything else is worker work — including **operational work**: live-run debugging, timeout/retry tuning, incident chasing, and log-driven fixes are code changes; dispatch them (a reproducing test first — the worker's TDD loop, or `gambit:debugging`), never absorb them into your own context because "you're already in the logs." Read-only investigation (tailing logs, a scout, forming a hypothesis) is fine; the moment you edit source to fix it, that's a worker's job.

**Verify visual work by looking.** However the code was produced — self-implemented or dispatched — an aesthetic or visual task is not done until you have seen it rendered: build → screenshot at desktop + mobile widths (+ reduced-motion where it matters) → judge the pixels against the brief. Reading the diff cannot tell you whether it looks right. Full loop: `references/visual-verification.md`.

**Execute the steps in the task description:**

For a delegated task the worker runs this loop in its own context under `contracts/worker.md`; for a non-code task you run it directly. Commits happen only at the checkpoint (Step 4a) — the worker never commits. For each step:
1. Follow the TDD cycle: write test → watch it FAIL → write minimal code → watch it PASS → refactor
   - **Iron law: no production code without a failing test first.** Wrote code before the test? Delete it. Start over. Don't keep it as "reference."
   - If test passes immediately, STOP — test doesn't catch the new behavior. Fix the test.
   - GREEN means minimal: no features the test doesn't exercise, no error handling it doesn't check.
2. Run verifications exactly as specified

**Pre-completion verification (FRESH evidence required):**
- All steps in description completed?
- Tests passing? Run each worker's complete focused command. Then run the declared wave/component gate exactly once on the integrated wave; for a wave of ≥2 that is the manifest gate, never a per-worker rerun.
- Read complete output, check pass/fail counts and exit code
- Changes committed?
- State claim WITH evidence: "Tests pass. [Ran: X, Output: Y/Y passed, exit 0]"

#### Checkpoint gate (judge the diff against the baseline, not just the tests)

A green test is necessary but NOT sufficient. Before marking the task complete, read the worker's complete change set — NUL-safe `git status`, staged and unstaged diffs, and every untracked/binary artifact named in `Files owned` — and judge it. Ordinary `git diff` alone is incomplete. The integrator later exposes a staged `--binary --full-index` diff for the durable record. The orchestrator does this ITSELF, always — there is no per-task reviewer dispatch. It judges a *worker's* code, not its own, against the epic's baseline and nothing else: the Requirements, Success Criteria, Anti-Patterns, and Scope Boundaries, the task's `Files owned`, and the worker contract's mechanical floor. The epic's Quality Bar is the definition of defect you apply here; it is not a second standard.

The verdict is binary and itemized. Emit this record, with every line cited (`file:line` or command output):

```
Baseline:      <epic subject> / <task subject>
C1 <criterion or requirement this task owns>   DONE | NOT DONE   <evidence>
C2 ...
Anti-patterns: none present | present at file:line
Scope:         within Files owned | outside at path  (mechanical fallout of a correct change that breaks the shared gate — regenerated fixtures, a cross-package test that must update — is in scope once the worker reports it and you authorize it)
Floor:         clean | suppression / weakened or tautological test / dead code / unhandled error / security or data-loss path with a reachable precondition, at file:line
Minimal:       nothing beyond what the brief names and the floor handling the change itself requires | extra guard, fallback, retry, abstraction, or behavior at file:line (the repair removes it)
Evidence:      RED/GREEN genuinely exercises the change (fails without it, for the right reason) | vacuous at file:line
Wiring:        every new field, event, or behavior reaches its read/consumption path | orphan at file:line
Verdict:       DONE | NOT DONE [C-ids and lines]
```

Each NOT DONE names its baseline clause, the changed-code cause, and the evidence — that triple is exactly what the repair worker receives. Anything you notice that is none of the lines above — an edge case the brief does not name, a refactor you would prefer, a guard against a failure no requirement describes, a hypothetical future need — is an observation: write it under the checkpoint's Notes and move on. It is not a NOT DONE and it is not a task. **Never a silent "looks fine"**: a DONE verdict carries its per-line evidence.

Route on the verdict:
- **DONE** → proceed to mark complete and checkpoint.
- **NOT DONE** → if the task's `repairs_used` is `0`, route the itemized NOT DONE list as the one informed repair (Step 2.3); otherwise the task is `awaiting_user` — park the work on its `parked/<task-slug>` branch (Step 2.3) and checkpoint with the diff summary and one question. **Never edit the diff yourself — you judge and route; workers implement.**

There is no per-task reviewer. The end-of-epic `gambit:review` (Step 5) is the one independent review of this epic, and it is bounded there; a defect this gate misses surfaces once, at review, and costs one bounded repair there instead of an open-ended loop mid-wave. Do NOT dispatch a finder, verifier, or judge from this gate, and do NOT run the four-dimension review per task.

For a single task, mark complete with `TaskUpdate` only after all steps are verified with fresh evidence and the checkpoint gate returned DONE. For a ≥2 wave, keep every task in progress until every per-worker checkpoint gate returns DONE and `integrate_wave.py` completes the atomic fast-forward after its one combined wave/component gate; then mark the wave's tasks complete together.

#### When Hitting Obstacles

**CRITICAL: Check epic BEFORE switching approaches.**

1. Re-read epic with `TaskGet` — check "Approaches Considered" and "Anti-patterns"
2. If alternative was already REJECTED, note original rejection reason
3. Only switch if rejection reason no longer applies AND user approves

**Never water down requirements to "make it easier."**

#### When Discoveries Require New Work

If implementation reveals unexpected work:

1. Create new task with `TaskCreate` — full detail, no placeholders
2. Set dependency with `TaskUpdate addBlockedBy` (only on other subtasks — never on the epic, which would deadlock since the epic completes last)
3. Ensure it's scoped to one focused sitting (~15-45 min), has explicit paths, testable criteria
4. Document in checkpoint summary that new task was added

---

### 3. Create the Next Wave

Choose a runnable delivery slice before applying the width rule below. Prefer the smallest path
to the next user outcome, not independently polished foundations. A foundation is justified by a
concrete required dependency; name its next real consumer and integration point. Module completion
is not end-to-end delivery. Harvest parallelism within that slice rather than displacing it.

After a wave completes, build the NEXT wave from what you learned — and make it **as wide as the design genuinely supports**. Author EVERY follow-on task that passes the pluckability test, not just the single next step. Defaulting to one task when three are pluckable wastes the parallel machinery.

**The pluckability test:** a task belongs in the next wave iff its brief can be written entirely from code that exists right now — exact file set, anchors cited by `file:line`, testable criteria — with no placeholder for anything another open task will produce. If the brief needs a stand-in ("use whatever interface task N exposes"), it isn't pluckable; it waits.

**Genuinely serial — a later wave (or a solo wave), never widened into this one:**
- **Output consumers** — the task needs another open task's code, interface, schema, or answer.
- **Unsettled design** — a cross-file contract (API shape, data model, error policy) is still open. Settle it first (Step 2), then author its consumers.
- **Shared files, including hidden ones** — beyond the named file sets, check surfaces tasks touch *implicitly*: lockfiles/manifests when both add dependencies, generated code, migration sequence numbers, barrel/index/`mod.rs` files, route tables, DI registries, snapshot directories. A collision on any of these is overlap, same as a named file.
- **Repo-wide sweeps** — renames, dependency upgrades, format passes conflict with everything; always a solo wave.
- **Speculative specs** — work whose shape depends on what this wave will teach stays *unauthored*. Tasks are created iteratively as reality unfolds, never all upfront — an upfront task tree goes stale the moment the first task teaches you something.

**Never manufacture disjointness.** Don't split one behavior along a file boundary to fake width — two halves of one change brief badly and integrate worse. Harvest width where the design provides it; don't engineer it.

**Harvest width when the suite is slow.** A ≥2 wave pays for one combined wave/component gate, not one gate per worker, so independent work captures more speedup as the suite gets slower. Width is limited by real ownership, dependency, review-attention, and conflict surfaces — never manufacture disjointness merely to make a wave wider.

**Review what you learned:**
1. What did we discover during implementation?
2. What existing functionality, blockers, or limitations appeared?
3. Are we still moving toward epic success criteria?
4. What's the logical next step?

Unrequired machinery may be removed rather than hardened when no requirement, existing obligation,
or admitted finding depends on it. Trace the remaining behavior and test the retained guarantees.
Prior approval of an approach and sunk effort do not independently make its mechanisms immutable.
Explicit user-selected mechanisms and safety/compatibility constraints still bind. This does not
bypass architecture admission for new ownership or protocol invariants. Case C below applies to
changes to those approved constraints, not removal of incidental machinery.

**Three cases:**

**A) Clear next step(s)** → `TaskCreate` every pluckable task as the next wave, set dependencies for the serial remainder, proceed to checkpoint

**B) Planned next task now redundant:**
- Discovery makes it unnecessary
- Document why in checkpoint
- Mark completed with note: "SKIPPED: [reason]"
- Create the actual next task if one exists

**C) Need to adjust approach:**
- Document learnings in checkpoint
- Let user decide how to adapt

**Task quality check:**
- Scoped: one focused sitting (~15-45 min)
- Self-contained: Can execute without asking questions
- Explicit: `Files owned` is an exact path allowlist; `Hidden shared surfaces` records implicit collision checks; `Neighbors` gives every concurrent worker's exact allowlist
- Definitive: Steps reference verified file paths — never conditional ("if exists", "if present"). Verify against the codebase first, then write the step.
- Testable: Has verification command with expected output
- Anchored: names the exact existing functions/files to mirror and the established idiom to follow — anchor quality visibly drives worker output quality
- Disjoint: names its exact file set; no overlap and no output-dependency with any other task in the same wave (overlap or dependency → a later wave)

#### Convergence Gate

Before retaining any next-wave brief, compare the current result with the last durable checkpoint and record which success criteria or named blockers were retired, which remain, and which new items appeared.

- **Positive convergence** means the wave retired at least one approved success criterion or
  named blocker without unauthorized scope growth. A named blocker is a failing declared gate or
  a confirmed, admitted finding tied to required behavior or an evidenced failure—not a newly
  named prerequisite or optional improvement. Report the actual integration milestone; polishing
  a foundation or retiring optional improvements does not reset the convergence counter.
- **Negative convergence circuit breaker:** if two consecutive checkpoints retire no success criterion or named blocker, or remaining work grows at both checkpoints, STOP autonomous continuation. Present the evidence and require explicit user approval to re-scope, change architecture, or extend the delivery budget. Do not silently add another repair wave.
- **Repair limit:** one implementation, then at most one informed repair on the `escalation`
  rung, then `awaiting_user`. No judge, no second repair, no higher rung, and no renamed or split
  descendant continues a task the user has not answered. The negative-convergence circuit breaker
  remains an additional stop.
- **Scope admission:** every new worker must map to an immutable requirement, an admitted open
  frozen-ledger finding, or a failing declared validation gate. Review confirmation alone does
  not authorize work. Do not strengthen the epic to justify a task; report additional guarantees
  as proposed scope and exclude them until explicitly approved.
- **Architecture admission:** new cross-component ownership, persistence, recovery, ordering, fencing, or protocol invariants that the approved approach does not settle route back through `gambit:brainstorming` before another implementation wave or release-acceptance spend.

---

### 4. Commit and STOP Checkpoint (Mandatory)

Two parts: commit any work that isn't already on the branch, then present the checkpoint and STOP.

#### 4a: Commit Task's Work to Current Branch (Default)

Before presenting the checkpoint, commit the wave's work to whatever branch is currently checked out — `main`, a feature branch, a worktree branch, whichever is active. The checkpoint is the agreed "one wave done" unit; a commit at this boundary makes each task a durable, reviewable history entry so the user's next action (review, clear context, hand off, walk away) finds the work preserved. A successful ≥2 wave already reached the branch through one tested atomic fast-forward containing one commit per worker (Step 2), so here you only confirm nothing is left uncommitted.

1. Run `git status` to see what's uncommitted
2. If there are changes:
   - Stage each task's files by name — avoid `git add -A`, which can sweep in accidentally-created files. One commit per task, even within a wave.
   - Write a concise commit message: one-line subject describing what the task accomplished; optional short body for non-obvious WHY
   - Create a NEW commit (don't amend). Don't skip hooks. Don't push.
3. If `git status` is clean (a ≥2 wave already landed its tested combined history atomically, intra-task commits during the TDD cycle captured everything, or the task was marked SKIPPED with no code changes), note it under "Commit" in the checkpoint summary

Parked work is already committed on its own `parked/<task-slug>` branch and is never staged or committed here; the epic branch carries only accepted work.

**Do NOT push.** Committing is local — the user decides when to push.

**Skip the commit ONLY if** the user has explicitly said "don't commit yet" earlier in the current session. Absent that directive, commit.

#### 4b: Present Checkpoint Summary

**Present this summary, then STOP:**

```markdown
## Checkpoint

### What Was Done
- [Summary of implementation]
- [Key decisions made]

### Commit
- [Short SHA and subject line, e.g. `a1b2c3d feat: add OAuth callback handler`]
- [Or: "Nothing new to commit — intra-task commits during TDD already captured all changes"]

### Gate verdict
- [DONE — every owned criterion evidenced, within Files owned, floor clean, RED/GREEN genuine, wiring complete]
- [Or: the NOT DONE items (clause, cause, evidence) and the repair dispatched on the `escalation` rung, with `file:line`]
- [Or: `awaiting_user` — work parked on `parked/<task-slug>`; the one question: <exact decision needed>]

### Notes
- [Observations from the worker's `## Notes` and your own gate that are outside the baseline — for you to read; no task was created from them]

### Learnings
- [Discoveries during implementation]
- [Anything that affects future tasks]

### Task Status
[TaskList output — completed, in-progress, pending]

### Epic Progress
- [X/Y success criteria met]
- [What remains]

### Convergence
- [Success criteria or named blockers retired this checkpoint]
- [New remaining work and its requirement, frozen-ledger ID, or failing gate]
- [Positive / first negative / circuit breaker reached]

### Next Task
- [Title and brief description]
- [Why this is the right next step based on learnings]

### To Continue
Run `/gambit:executing-plans` to execute the next task.
```

**Why STOP is mandatory:**
- User can review implementation quality
- User can clear context if conversation is long
- User can adjust direction based on learnings
- Prevents runaway execution without oversight
- Ending the turn is also what lets a goal Stop-hook fire and re-invoke you for the next cycle — so STOP is what *arms* autonomous continuation, never what blocks it. Continuing in the same turn would skip the hook entirely.

---

### 5. Epic Review

When all subtasks completed:

1. `TaskList` — verify all subtasks show "completed"
2. `TaskGet` on epic — review each success criterion
3. Run an **architecture/scope preflight** before release acceptance. Compare the complete epic diff with the approved Approach, Scope Boundaries, and Anti-Patterns. If the work introduced a new cross-component ownership, persistence, recovery, ordering, fencing, or protocol invariant, dispatch the existing `skills/review/reviewers/conformance.md` reviewer on the rung the `finder` role resolves to (`contracts/models.md`) for an independent preflight and adjudicate its cited findings. Any unapproved architecture or scope growth routes back through `gambit:brainstorming`; do not spend acceptance to discover a design decision review could catch.
4. Run the declared wave/component gate fresh on the complete integrated epic.
5. Run release acceptance only after the preflight and wave/component gate pass, with the declared freshness setup and within the declared acceptance budget. If the budget is exhausted, STOP and request explicit user approval; never hide an extra run as ordinary verification.
6. Verify every success criterion with the evidence at its declared validation tier.

**Then invoke review directly using the Skill tool:**

```
Skill skill="gambit:review"
```

Do not tell the user to run it manually — invoke it and follow its process immediately. Review validates architecture, security, completeness, dead code, test quality, and code quality across the entire epic before allowing finishing-branch.

For obstacle handling and checkpoint-brief examples, read `references/examples.md`.

## Integration

Called by `gambit:brainstorming` or the user. Dispatches contracted workers, runs the checkpoint gate itself, and invokes `gambit:review` after the final wave.
Each worker runs on the rung the `worker` role resolves to in `contracts/models.md`, and a NOT DONE gets exactly one informed repair on the `escalation` rung before the user decides.
