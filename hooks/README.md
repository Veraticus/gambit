# Gambit Hooks

Bash hooks for Claude Code lifecycle events. Fast startup (~5ms).

## Design Philosophy

Gambit achieves skill compliance through **strong prompting, not mechanical enforcement**. This follows the approach proven by [superpowers](https://github.com/obra/superpowers): authority language with `<EXTREMELY-IMPORTANT>` tags, explicit rationalization blocking, and mandatory framing drive Claude to invoke skills without needing PreToolUse blockers.

The hooks reinforce this by:
- **SessionStart** — Injecting the full `using-gambit` skill with mandatory activation language
- **PostToolUse/Stop** — Tracking state and providing contextual nudges

Skills are invoked manually by the user via slash commands (e.g., `/gambit:debugging`).

## Installation

The `hooks.json` file configures all hooks. When using gambit as a plugin, hooks are automatically configured via `${CLAUDE_PLUGIN_ROOT}`.

For manual installation, add to your project's `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          { "type": "command", "command": "/path/to/gambit/hooks/session-start/inject-using-gambit.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command", "command": "/path/to/gambit/hooks/post-tool-use/track-edits.sh" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "/path/to/gambit/hooks/stop/gentle-reminders.sh" }
        ]
      }
    ]
  }
}
```

## Activation Chain

```
Session starts
  → inject-using-gambit.sh loads using-gambit skill with <EXTREMELY_IMPORTANT> tags
  → Claude sees: "IF A SKILL APPLIES, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT."

User invokes skills manually
  → /gambit:debugging, /gambit:review, etc.

Claude works
  → track-edits.sh logs file modifications

Claude stops
  → gentle-reminders.sh checks for TDD/verification/commit gaps
```

## Available Hooks

### SessionStart: inject-using-gambit.sh

Injects the full `using-gambit` skill into context at session start.

- Reads `skills/using-gambit/SKILL.md`
- Wraps in `<EXTREMELY_IMPORTANT>` tags
- Contains the 1% threshold rule, Red Flags rationalization table, and skill routing flowchart

### PostToolUse: track-edits.sh

Logs Edit, Write, and MultiEdit tool calls to `context/edit-log.txt`. Records timestamp, tool name, and file path. Auto-rotates at 500 lines. Used by `gentle-reminders.sh` to detect TDD gaps (source edits without test edits).

### Stop: gentle-reminders.sh

Non-blocking contextual reminders when Claude's turn ends:
- TDD reminder if source files edited without test files
- Verification reminder if claiming "done" without test evidence
- Commit reminder if 3+ files edited

## Dependencies

- `jq` (for JSON parsing)
- `bash` 4.0+

## Testing Hooks

```bash
# Gentle reminders
echo '{"response": "Done! The feature is complete."}' | ./hooks/stop/gentle-reminders.sh
```
