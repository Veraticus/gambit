# Delivery judgment

Use this reference only at the execution seam: before a corrective dispatch or quality repair that
materially expands the original executable brief, after an informed repair fails, and before an
escalation or repeat of the terminal rung. It is not a routine reviewer for a healthy first dispatch.

## State and trigger

At Step 0 and on every resume, read the existing task family's `DELIVERY` section before choosing
work. A known fresh initial task with no record may take its ordinary first dispatch. Otherwise, a
`USER-DECISION` record, a consumed allowance whose endpoint failed, or an unrecoverable allowance
is a pause: do not call a judge or worker. A descendant, split, rename, model switch, later
checkpoint, or Goal resume inherits the family identity, allowance, and endpoint; it cannot renew
one.

For Claude, record the compact `DELIVERY` section on the existing Task. For Codex, record it in the
same-session plan/checkpoint only. Codex never reconstructs permission from git or repository
artifacts. The record names family identity, verdict, consumed allowance, endpoint, and evidence
references. Missing state on a known initial task is not lost state; missing recovery state for an
existing family is unknown and therefore `USER-DECISION`.

Material expansion means changed executable ownership, additional required behavior or invariants
outside the original steps, or newly coupled lifecycle/integration work invalidating the bounded
slice. An ordinary first informed repair may proceed only while it remains bounded in that brief.
Do not use elapsed duration alone as a trigger or defect claim. Required supported behavior,
security/correctness, meaningful tests, and material code quality still block; optional ideals and
speculative edges do not create work.

## Fresh independent delivery judgment

Prepare primary evidence, not a root-only summary: verbatim Requirements and Success Criteria, the
original brief, the current task-family `DELIVERY` record with its allowance status explicitly marked
unused, consumed, or unknown, worker returns, diff stat against the wave base and owned files,
focused-gate output, admitted defects with location and consequence, and source references. The
approved packet must supply this authoritative state; the judge must not guess it. Label the root's
proposed route separately. The judge may inspect those artifacts, but is not a new defect finder.

Resolve the existing config-resolved `steelman` role and dispatch it fresh with
`codex-contracts/steelman.md` by path and `Mode: Delivery judgment`; do not inherit a prior judge turn.

```
SpawnSpawnAgent agent_type="steelman" fork_turns="none"
  message="Read <abs>/codex-codex-contracts/steelman.md first. Mode: Delivery judgment. Evaluate only the supplied evidence and return its contracted verdict."
```

One execution-time judgment is available for a task-family intervention, separately from the
Discovery/Closure budget. A failed, malformed, or missing judgment grants no permission. Do not
replace this dispatch with a root check.

- `DESIGN-SATISFIED`: complete normal fresh verification and integration; it is not a release claim.
- `CONTINUE-ONCE`: only when the judge states exact required defect(s), concrete supported
  consequence, minimal finishing route, exact files, and a falsifiable existing-tier endpoint.
  Confidence, sunk cost, real but sprawling defects, or ideal architecture are insufficient.
  Record and consume the allowance **before** dispatching the one corrective worker.
- `USER-DECISION`: preserve partial work uncommitted, leave the family incomplete, checkpoint the
  exact decision needed, and pause autonomous dispatch. Do not automatically call another judge.

If the consumed continuation misses its endpoint, pause for the user without another judge or
worker. Simplifying or re-slicing within existing obligations remains that same allowance; new
guarantees or architecture require existing user admission. An explicit conflicting user-selected
continuation policy requires clarification, not silent replacement.
