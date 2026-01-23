# Gambit Hooks

Bash hooks for Claude Code. Fast startup (~5ms).

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

## Available Hooks

### SessionStart

#### inject-using-gambit.sh

Injects the `using-gambit` skill content into context at session start.

**Behavior:**
- Reads `skills/using-gambit/SKILL.md`
- Wraps content in `<EXTREMELY_IMPORTANT>` tags
- Ensures Claude knows about gambit skills from the start

**Why:**
Claude needs to know about available skills to use them. This hook ensures skill awareness without relying on Claude to remember to check.

---

### UserPromptSubmit

#### skill-activator.sh

Suggests relevant skills based on keywords in the user's prompt.

**Behavior:**
- Reads prompt text from stdin
- Matches against keywords/patterns in `skill-rules.json`
- Returns top 3 matching skills by priority
- Shows activation guidance

**Configuration:**
Edit `skill-rules.json` to customize keyword triggers:

```json
{
  "debugging": {
    "priority": "high",
    "type": "workflow",
    "keywords": ["bug", "broken", "failing", "error"],
    "patterns": ["test.*fail", "doesn't work"]
  }
}
```

**Why:**
Users often describe problems without knowing which skill applies. This hook bridges the gap between natural language and skill activation.

---

### PostToolUse

#### track-edits.sh

Tracks which files were edited during the session.

**Behavior:**
- Logs Edit, Write, and MultiEdit tool calls to `context/edit-log.txt`
- Records timestamp, tool name, and file path
- Auto-rotates log at 500 lines

**Used by:**
`gentle-reminders.sh` reads this log to give accurate feedback about which files were edited.

**Why:**
Parsing Claude's response text for edit mentions is unreliable. Tracking actual tool calls gives accurate data for TDD and commit reminders.

---

### PreToolUse

#### block-pre-existing-checks.sh

Prevents Claude from investigating git history to check if test failures are "pre-existing."

**Behavior:**
- Checks if repo has pre-commit hooks (`.pre-commit-config.yaml`, `.git/hooks/pre-commit`, `lefthook.yml`)
- If no pre-commit hooks: allows everything
- If pre-commit hooks exist: blocks commands that look like "checkout old commit + run tests"

**Smarts:**
- Reads the `description` field to understand Claude's intent
- Pattern matches on keywords like "pre-existing", "before changes", "already broken"
- Falls back to command pattern matching (git checkout + test command)

**Why:**
Pre-commit hooks guarantee the previous commit was clean. If tests fail, it's from current changes. Fix directly instead of wasting time investigating history.

---

### Stop

#### gentle-reminders.sh

Shows contextual reminders when Claude stops responding.

**Behavior:**
- Reads edit log from `track-edits.sh` to know which files were edited
- Analyzes Claude's response for completion claims
- Checks if verification was mentioned
- Shows relevant reminders (max 3)

**Reminders:**
- 💭 TDD reminder if code edited without tests
- ✅ Verification reminder if claiming "done" without running tests
- 💾 Commit reminder if many files edited

**Why:**
Gentle nudges help maintain discipline without blocking workflow. Non-blocking - always exits 0.

---

## Dependencies

- `jq` (for JSON parsing)
- `bash` 4.0+

## Writing New Hooks

Hooks read JSON from stdin, optionally write JSON to stdout.

### Input Formats

**PreToolUse:**
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

**UserPromptSubmit:**
```json
{
  "prompt": "Fix the bug in the login flow",
  "session_id": "abc123"
}
```

**Stop:**
```json
{
  "response": "I've implemented the feature and it's ready.",
  "session_id": "abc123"
}
```

### Output Formats

**To block (PreToolUse only):**
```json
{
  "decision": "block",
  "reason": "Explanation shown to Claude"
}
```

**To inject context:**
```json
{
  "additionalContext": "Context message shown to Claude"
}
```

**To allow (no output needed):**
Exit with code 0 and no output.

## Performance

Bash + jq hooks start in ~5ms. For hooks that run on every tool call or prompt, startup time matters.

## Testing Hooks

```bash
# Test skill-activator
echo '{"prompt": "Fix this bug"}' | ./hooks/user-prompt-submit/skill-activator.sh

# Test block-pre-existing-checks
echo '{"tool_name": "Bash", "tool_input": {"command": "git checkout HEAD~1 && go test", "description": "check pre-existing"}}' | ./hooks/pre-tool-use/block-pre-existing-checks.sh

# Test gentle-reminders
echo '{"response": "Done! The feature is complete."}' | ./hooks/stop/gentle-reminders.sh
```
