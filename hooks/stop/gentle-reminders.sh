#!/usr/bin/env bash
# gentle-reminders.sh
#
# Stop hook that shows contextual reminders based on what happened in the session.
# Non-blocking - always exits 0.

# Don't use set -e because grep returns 1 when no match (expected behavior)
set -uo pipefail

# Read response from stdin (Claude passes JSON with session info)
input=$(cat)

# Try to extract response text
response=""
if command -v jq >/dev/null 2>&1; then
    response=$(echo "$input" | jq -r '.response // .text // ""' 2>/dev/null) || response=""
fi

# Track which reminders to show
show_tdd=false
show_verify=false
show_commit=false

# Check for completion claims without verification
if echo "$response" | grep -qiE '(done|complete|finished|ready|fixed|works|implemented)' 2>/dev/null; then
    # Check if verification was mentioned
    if ! echo "$response" | grep -qiE '(test.*pass|all.*pass|verified|ran.*test|test.*green)' 2>/dev/null; then
        show_verify=true
    fi
fi

# Check for code changes without test mentions
if echo "$response" | grep -qiE '(Edit|Write|created|modified|updated|changed).*\.(go|ts|js|py|rs|java)' 2>/dev/null; then
    if ! echo "$response" | grep -qiE '(test|spec|_test\.|\.test\.)' 2>/dev/null; then
        show_tdd=true
    fi
fi

# Check for many file edits (suggest commit)
edit_count=$(echo "$response" | grep -oE '(Edit|Write)' 2>/dev/null | wc -l | tr -d '[:space:]') || edit_count=0
edit_count=${edit_count:-0}
if [[ "$edit_count" -ge 3 ]]; then
    show_commit=true
fi

# Display reminders if any apply
if [[ "$show_tdd" == "true" ]] || [[ "$show_verify" == "true" ]] || [[ "$show_commit" == "true" ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ "$show_tdd" == "true" ]]; then
        echo "💭 Remember: Write tests first (gambit:tdd)"
    fi

    if [[ "$show_verify" == "true" ]]; then
        echo "✅ Before claiming complete: Run tests (gambit:verification)"
    fi

    if [[ "$show_commit" == "true" ]]; then
        echo "💾 Consider: Multiple files edited - commit incrementally"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Always succeed (non-blocking)
exit 0
