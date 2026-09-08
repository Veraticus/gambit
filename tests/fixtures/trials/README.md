# Behavioral trial fixtures

Place fixtures at `tests/fixtures/trials/<skill>/<name>.json`:

```json
{
  "skill": "<skill>",
  "text": "<repo-relative tested text>",
  "neighbors": ["<repo-relative reference text>"],
  "exercise": "<facts and requested response>",
  "checklist": ["<binary scoring item>"]
}
```

Each fixture produces one cell per fixed subject. Its ID is `<skill>/<name>@<subject>`. The tested text is placed between `BEGIN/END SKILL`, neighbors between path-named `BEGIN/END REFERENCE` markers, and the exercise between `BEGIN/END EXERCISE`.

`results.json` maps each cell ID to:

```json
{
  "status": "ok|transport_failure|judge_failure",
  "pass": true,
  "hashes": {
    "fixture": "<sha256>",
    "text": "<sha256>",
    "neighbors": {"<path>": "<sha256>"}
  },
  "subject": {"model": "<route>", "effort": "<effort>"},
  "judge": {"model": "<route>", "effort": "xhigh"},
  "response": "<subject response>",
  "items": [{"item": "<checklist item>", "pass": true, "evidence": "<quote>"}],
  "judge_raw": "<last raw judge reply; judge_failure only>",
  "at": "<ISO timestamp>"
}
```

Run `python3 tests/trials/run.py --skill <skill>` to refresh cells, `--all` to refresh every fixture, `--check-fresh` to verify hashes and passing scores without network access, `--probe` to test routes, or `--dry-run --skill <skill>` to inspect prompts.
