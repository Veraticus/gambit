# Gambit Hooks

Bash hooks for Claude Code. Fast startup, no Python.

## Installation

Add to your project's `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/gambit/hooks/pre-tool-use/block-pre-existing-checks.sh"
          }
        ]
      }
    ]
  }
}
```

Or your global `~/.claude/settings.json` for all projects.

## Available Hooks

### PreToolUse

#### block-pre-existing-checks.sh

Prevents Claude from investigating git history to check if test failures are "pre-existing."

**Behavior:**
- Checks if repo has pre-commit hooks (`.pre-commit-config.yaml`, `.git/hooks/pre-commit`, `lefthook.yml`)
- If no pre-commit hooks: allows everything
- If pre-commit hooks exist: blocks commands that look like "checkout old commit + run tests"

**Why:**
Pre-commit hooks guarantee the previous commit was clean. If tests fail, it's from current changes. Fix directly instead of wasting time investigating history.

**Smarts:**
- Reads the `description` field to understand Claude's intent
- Pattern matches on keywords like "pre-existing", "before changes", "already broken"
- Falls back to command pattern matching (git checkout + test command)

## Dependencies

- `jq` (for JSON parsing)

## Writing New Hooks

Hooks read JSON from stdin, optionally write JSON to stdout.

**Input format (PreToolUse):**
```json
{
  "session_id": "abc123",
  "tool_name": "Bash",
  "tool_input": {
    "command": "git checkout abc123 && go test ./...",
    "description": "Check if failure existed before my changes"
  }
}
```

**Output format (to block):**
```json
{
  "decision": "block",
  "reason": "Explanation shown to Claude"
}
```

**Output format (to allow):**
Exit with code 0 and no output.

## Why Bash?

Python hooks add ~150ms startup overhead per invocation. Bash + jq is ~5ms.

For hooks that run on every tool call, this matters.
