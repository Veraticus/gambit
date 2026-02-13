#!/usr/bin/env bash
# skill-activator.sh
#
# UserPromptSubmit hook that identifies relevant skills and mandates their use.
# Reads skill-rules.json for keyword/pattern matching.

set -euo pipefail

# Check for jq
if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

# Find plugin root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RULES_FILE="${PLUGIN_ROOT}/hooks/skill-rules.json"

if [[ ! -f "$RULES_FILE" ]]; then
    exit 0
fi

# Read prompt from stdin
input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // .text // ""' 2>/dev/null || echo "")

if [[ -z "$prompt" ]]; then
    echo '{}'
    exit 0
fi

# Check for bypass keywords
prompt_lower=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')
if [[ "$prompt_lower" == *"no skill"* ]] || [[ "$prompt_lower" == *"skip skill"* ]]; then
    echo '{}'
    exit 0
fi

# Find matching skills
matches=()

# Read each skill from rules
for skill in $(jq -r 'keys[] | select(startswith("_") | not)' "$RULES_FILE"); do
    matched=false

    # Check keywords (use while read to preserve multi-word keywords)
    while IFS= read -r keyword; do
        [[ -z "$keyword" ]] && continue
        keyword_lower=$(echo "$keyword" | tr '[:upper:]' '[:lower:]')
        if [[ "$prompt_lower" == *"$keyword_lower"* ]]; then
            matched=true
            break
        fi
    done < <(jq -r ".\"$skill\".keywords // [] | .[]" "$RULES_FILE" 2>/dev/null)

    # Check patterns if no keyword match
    if [[ "$matched" == "false" ]]; then
        while IFS= read -r pattern; do
            [[ -z "$pattern" ]] && continue
            if echo "$prompt_lower" | grep -qE "$pattern" 2>/dev/null; then
                matched=true
                break
            fi
        done < <(jq -r ".\"$skill\".patterns // [] | .[]" "$RULES_FILE" 2>/dev/null)
    fi

    if [[ "$matched" == "true" ]]; then
        matches+=("$skill")
    fi
done

# No matches - return empty
if [[ ${#matches[@]} -eq 0 ]]; then
    echo '{}'
    exit 0
fi

# Take top 3
top_matches=("${matches[@]:0:3}")

# Build output message
lines=()
lines+=("")
lines+=("<EXTREMELY-IMPORTANT>")
lines+=("MANDATORY SKILL ACTIVATION — You MUST invoke one of these skills BEFORE proceeding:")
lines+=("")

for skill in "${top_matches[@]}"; do
    lines+=("- **gambit:$skill** — Invoke with: Skill tool, skill=\"gambit:$skill\"")
done

lines+=("")
lines+=("YOU DO NOT HAVE A CHOICE. If a skill matched, you MUST use it.")
lines+=("Do not respond, explore, or take any action until you have invoked the Skill tool.")
lines+=("To bypass: user must include 'no skill' or 'skip skill' in their prompt.")
lines+=("</EXTREMELY-IMPORTANT>")
lines+=("")

# Join lines with \n for JSON
context=$(printf '%s\\n' "${lines[@]}")

# Output JSON
cat <<EOF
{
  "additionalContext": "$context"
}
EOF

exit 0
