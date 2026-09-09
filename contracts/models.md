# Roles and rungs

## Roles

| Role | Does | Writes? | Contract |
|---|---|---|---|
| `worker` | Implements one task under the worker contract and a brief, test first. | Yes, owned files only. | `contracts/worker.md` |
| `escalation` | Takes the next ladder step for a task whose gate says NOT DONE. | Yes, owned files only. | `contracts/worker.md` |
| `scout` | Finds facts in the tree and returns `file:line` evidence or NOT FOUND. | No. | `contracts/scout.md` |
| `steelman` | Runs one discovery pass and at most one closure pass on an agreed design. | No. | `contracts/steelman.md` |
| `finder` | Reviews one dimension of the frozen candidate. | No. | The assigned dimension file under `skills/review/reviewers/`. |
| `verifier` | Adversarially confirms or drops each finding. | No. | `skills/review/reviewers/verifier.md` |
| `test-runner` | Executes a command that needs writable scratch state in an isolated workspace. | Yes, scratch only. | The command it is given, in the isolated workspace. |

## Rungs and ladders

A rung is a model at an effort level, with a writing variant and a read-only variant. Every role has an entry rung. `worker` and `escalation` also have a ladder: an ordered list of rungs beginning at the entry and continuing upward.

Every dispatch starts at the role's entry rung. A rung gets at most two attempts at a task; the second only when the gate record names the exact fix the first lacked: an owned path the brief omitted, a value or decision it left out, or one named check with its failing output. That attempt carries the corrected brief, the gate record, and the current work.

A NOT DONE gate naming no such fix advances the task exactly one rung. A gate finding the task too large splits it at once, at any rung; a lineage splits once, and descendants never split. A task never moves down, and an agent never selects or changes its own rung. No role enters above its entry rung.

When the top rung fails, the orchestrator makes one final attempt itself, in the task's workspace under the worker contract, gated like any return. If that fails, the lineage is a gap.

## The registry

Rungs are named in exactly one place: `~/.claude/gambit/models.json`. The harness's configuration renders this registry, and both harnesses share it.

`rungs` maps each rung name to one of these shapes:

- `{"agent": <name>, "readonly_agent": <name>}` names dispatch targets that the harness resolves by name.
- `{"model": <alias>}` names a harness model alias for the dispatch operation.

`roles` maps each role name to `{"entry": <rung>, "ladder": [<rungs>]?, "readonly": true?}`. The ladder and read-only marker are optional. A read-only role dispatches the rung's read-only variant.

No contract or skill names a rung, model, or provider. Skills name roles and resolve them through this registry.

## Resolving a dispatch

To dispatch a role:

1. Look up the role in the registry.
2. Select its entry rung, the same rung for a second attempt, or the next rung in its ladder when a NOT DONE gate record requires advancement.
3. Select the rung's agent, using its read-only variant for a read-only role, or select its model alias.
4. Invoke the harness's dispatch operation, passing the role's contract by path and its brief as text.

Nothing is supplied implicitly. If the registry is missing or cannot resolve a role, record the unresolved role in the Decision Log. Every task that needs that role becomes a gap citing it. Independent work continues. The run ends with gaps only when no executable work remains.
