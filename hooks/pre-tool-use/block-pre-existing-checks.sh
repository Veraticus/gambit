#!/usr/bin/env bash
# block-pre-existing-checks.sh
#
# Blocks Claude from investigating git history to check if test failures
# are "pre-existing" -- but ONLY if the repo has pre-commit hooks.
#
# If pre-commit hooks exist, previous commit was clean by definition.
# Failures must be from current changes. Fix directly.

input=$(cat)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
[[ "$tool_name" != "Bash" ]] && exit 0

command=$(echo "$input" | jq -r '.tool_input.command // empty')
description=$(echo "$input" | jq -r '.tool_input.description // empty' | tr '[:upper:]' '[:lower:]')

# Only block if repo has pre-commit hooks
has_precommit=false
[[ -f ".pre-commit-config.yaml" ]] && has_precommit=true
[[ -f ".git/hooks/pre-commit" && -x ".git/hooks/pre-commit" ]] && has_precommit=true
[[ -f "lefthook.yml" ]] && has_precommit=true

[[ "$has_precommit" == "false" ]] && exit 0

# Check description for "investigating history" intent
investigating_history=false
if [[ "$description" =~ (pre-exist|before.*(change|commit)|previous.*(commit|version)|already.*(broken|failing)|was.*(broken|failing)|history|bisect) ]]; then
  investigating_history=true
fi

# Check command pattern as backup
if [[ "$command" =~ git[[:space:]]+(checkout|stash|bisect) ]] && \
   [[ "$command" =~ (pytest|go[[:space:]]+test|npm[[:space:]]+test|cargo[[:space:]]+test|make[[:space:]]+test) ]]; then
  investigating_history=true
fi

if [[ "$investigating_history" == "true" ]]; then
  cat << 'EOF'
{
  "decision": "block",
  "reason": "This repo has pre-commit hooks, so previous commit was clean. Test failures are from current changes - fix directly."
}
EOF
  exit 0
fi

exit 0
