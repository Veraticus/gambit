# Gambit Hooks

Bash hooks for Claude Code lifecycle events. Fast startup (~5ms).

## Design Philosophy

Gambit achieves skill compliance through **strong prompting, not mechanical enforcement**. This follows the approach proven by [superpowers](https://github.com/obra/superpowers): authority language with `<EXTREMELY-IMPORTANT>` tags, explicit rationalization blocking, and mandatory framing drive Claude to invoke skills without needing PreToolUse blockers.

The hooks reinforce this by:
- **SessionStart** — Injecting the full `using-gambit` skill with mandatory activation language
- **UserPromptSubmit** — Matching prompts to skills and presenting matches as non-negotiable
- **PostToolUse/PreToolUse/Stop** — Tracking state and providing contextual nudges

Every skill match is mandatory. There are no priority tiers — if a keyword matches, Claude must invoke the skill. Users bypass with "no skill" or "skip skill" in their prompt.

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
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "/path/to/gambit/hooks/user-prompt-submit/skill-activator.sh" }
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
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "/path/to/gambit/hooks/pre-tool-use/block-pre-existing-checks.sh" }
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

## Skill Activation Chain

```
Session starts
  → inject-using-gambit.sh loads using-gambit skill with <EXTREMELY_IMPORTANT> tags
  → Claude sees: "IF A SKILL APPLIES, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT."

User sends prompt
  → skill-activator.sh matches keywords/patterns from skill-rules.json
  → If match found: outputs <EXTREMELY-IMPORTANT> mandatory activation directive
  → If "no skill"/"skip skill" in prompt: bypasses silently
  → Claude must invoke the Skill tool before proceeding

Claude works
  → track-edits.sh logs file modifications
  → block-pre-existing-checks.sh prevents wasted git archaeology

Claude stops
  → gentle-reminders.sh checks for TDD/verification/commit gaps
```

## Available Hooks

### SessionStart: inject-using-gambit.sh

Injects the full `using-gambit` skill into context at session start.

- Reads `skills/using-gambit/SKILL.md`
- Wraps in `<EXTREMELY_IMPORTANT>` tags
- Contains the 1% threshold rule, Red Flags rationalization table, and skill routing flowchart

### UserPromptSubmit: skill-activator.sh

Matches prompts to skills and mandates activation.

- Matches keywords and regex patterns from `skill-rules.json`
- Returns up to 3 matching skills wrapped in `<EXTREMELY-IMPORTANT>` tags
- Every match is mandatory — no priority tiers, no soft suggestions
- Bypass: user includes "no skill" or "skip skill" in their prompt

**Configuration** — edit `skill-rules.json`:

```json
{
  "debugging": {
    "keywords": ["bug", "broken", "failing", "error"],
    "patterns": ["test.*fail", "doesn't work"]
  }
}
```

Keywords are case-insensitive substring matches. Multi-word keywords (e.g., "code review") match as complete phrases. Patterns are regex matched via `grep -E`.

### PostToolUse: track-edits.sh

Logs Edit, Write, and MultiEdit tool calls to `context/edit-log.txt`. Records timestamp, tool name, and file path. Auto-rotates at 500 lines. Used by `gentle-reminders.sh` to detect TDD gaps (source edits without test edits).

### PreToolUse: block-pre-existing-checks.sh

Blocks Claude from checking out old commits to verify if failures are "pre-existing." Only activates in repos with pre-commit hooks (`.pre-commit-config.yaml`, `.git/hooks/pre-commit`, `lefthook.yml`), since those guarantee the previous commit was clean.

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
# Skill activator — should match debugging
echo '{"prompt": "I found a bug in the login"}' | ./hooks/user-prompt-submit/skill-activator.sh

# Skill activator — should match nothing
echo '{"prompt": "What time is it?"}' | ./hooks/user-prompt-submit/skill-activator.sh

# Skill activator — bypass
echo '{"prompt": "Fix this typo, no skill"}' | ./hooks/user-prompt-submit/skill-activator.sh

# Block pre-existing checks
echo '{"tool_name": "Bash", "tool_input": {"command": "git checkout HEAD~1 && go test", "description": "check pre-existing"}}' | ./hooks/pre-tool-use/block-pre-existing-checks.sh

# Gentle reminders
echo '{"response": "Done! The feature is complete."}' | ./hooks/stop/gentle-reminders.sh
```
