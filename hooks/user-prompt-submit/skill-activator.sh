#!/usr/bin/env bash
# skill-activator.sh
#
# UserPromptSubmit hook that suggests relevant skills based on prompt keywords.
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

# Convert prompt to lowercase for matching
prompt_lower=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')

# Find matching skills
matches=()
match_reasons=()

# Read each skill from rules
for skill in $(jq -r 'keys[] | select(startswith("_") | not)' "$RULES_FILE"); do
    matched=false
    reason=""

    # Check keywords
    keywords=$(jq -r ".\"$skill\".keywords // [] | .[]" "$RULES_FILE" 2>/dev/null)
    for keyword in $keywords; do
        keyword_lower=$(echo "$keyword" | tr '[:upper:]' '[:lower:]')
        if [[ "$prompt_lower" == *"$keyword_lower"* ]]; then
            matched=true
            reason="keyword: $keyword"
            break
        fi
    done

    # Check patterns if no keyword match
    if [[ "$matched" == "false" ]]; then
        patterns=$(jq -r ".\"$skill\".patterns // [] | .[]" "$RULES_FILE" 2>/dev/null)
        for pattern in $patterns; do
            if echo "$prompt_lower" | grep -qE "$pattern" 2>/dev/null; then
                matched=true
                reason="pattern: $pattern"
                break
            fi
        done
    fi

    if [[ "$matched" == "true" ]]; then
        priority=$(jq -r ".\"$skill\".priority // \"medium\"" "$RULES_FILE")
        matches+=("$priority|$skill|$reason")
    fi
done

# No matches - return empty
if [[ ${#matches[@]} -eq 0 ]]; then
    echo '{}'
    exit 0
fi

# Sort by priority (high > medium > low) and take top 3
sorted_matches=$(printf '%s\n' "${matches[@]}" | sort -t'|' -k1,1 | head -3)

# Build output message
lines=()
lines+=("")
lines+=("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
lines+=("🎯 SKILL ACTIVATION CHECK")
lines+=("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
lines+=("")
lines+=("Relevant skills for this prompt:")
lines+=("")

while IFS='|' read -r priority skill reason; do
    case "$priority" in
        high) emoji="⭐" ;;
        medium) emoji="📌" ;;
        low) emoji="💡" ;;
        *) emoji="📌" ;;
    esac
    lines+=("$emoji **gambit:$skill** ($priority priority)")
done <<< "$sorted_matches"

lines+=("")
lines+=("Use: Skill tool with skill=\"gambit:<skill-name>\"")
lines+=("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
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
