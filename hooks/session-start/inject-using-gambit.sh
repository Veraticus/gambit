#!/usr/bin/env bash
# inject-using-gambit.sh
#
# SessionStart hook that injects the using-gambit skill into context.
# This ensures Claude knows about gambit skills from the start of every session.

set -euo pipefail

# Find plugin root (parent of hooks directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Read using-gambit skill content
SKILL_FILE="${PLUGIN_ROOT}/skills/using-gambit/SKILL.md"

if [[ ! -f "$SKILL_FILE" ]]; then
    # Skill file not found - exit silently
    exit 0
fi

skill_content=$(cat "$SKILL_FILE")

# Escape for JSON (handle newlines, quotes, backslashes)
escaped_content=$(echo "$skill_content" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}')

# Output context injection
cat <<EOF
{
  "additionalContext": "<EXTREMELY_IMPORTANT>\nYou have gambit skills.\n\n**The content below is from skills/using-gambit/SKILL.md - your introduction to using skills:**\n\n${escaped_content}\n\n</EXTREMELY_IMPORTANT>"
}
EOF

exit 0
