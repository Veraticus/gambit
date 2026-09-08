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

Every dispatch starts at the role's entry rung. A NOT DONE gate record advances that task exactly one rung. A task never moves down, and an agent never selects or changes its own rung. No role enters above its entry rung.

When a task fails at the top rung, the loop re-decomposes it once. Its descendants climb their ladders under the same gate rule, but they are never split again. A descendant that fails at the top becomes a gap.

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
2. Select its entry rung, or the next rung in its ladder when a NOT DONE gate record requires advancement.
3. Select the rung's agent, using its read-only variant for a read-only role, or select its model alias.
4. Invoke the harness's dispatch operation, passing the role's contract by path and its brief as text.

Nothing is supplied implicitly. If the registry is missing or cannot resolve a role, record the unresolved role in the Decision Log. Every task that needs that role becomes a gap citing it. Independent work continues. The run ends with gaps only when no executable work remains.
