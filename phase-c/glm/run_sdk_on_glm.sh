#!/usr/bin/env bash
# Run the Claude Agent SDK exercises against GLM via Z.AI proxy.
#
# This reuses phase-c/claude-agent-sdk/ex01-06 but routes API calls
# through Z.AI so GLM models handle everything instead of Claude.
#
# Usage:
#   cd phase-c/glm
#   bash run_sdk_on_glm.sh           # run all
#   bash run_sdk_on_glm.sh ex01      # run one (matches filename)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SDK_DIR="$REPO_ROOT/phase-c/claude-agent-sdk"

# ── Load Z.AI credentials from settings.local.json ───────────
LOCAL_SETTINGS="$SCRIPT_DIR/.claude/settings.local.json"
if [[ ! -f "$LOCAL_SETTINGS" ]]; then
    echo "ERROR: $LOCAL_SETTINGS not found"
    echo "Create it with your Z.AI API key:"
    echo '  {"env": {"ANTHROPIC_AUTH_TOKEN": "your-key"}}'
    exit 1
fi

# Parse ANTHROPIC_AUTH_TOKEN from settings.local.json
AUTH_TOKEN=$(python3 -c "import json; print(json.load(open('$LOCAL_SETTINGS'))['env']['ANTHROPIC_AUTH_TOKEN'])")
if [[ "$AUTH_TOKEN" == "your-zai-api-key-here" ]]; then
    echo "ERROR: Replace placeholder in $LOCAL_SETTINGS with your real Z.AI API key"
    exit 1
fi

# ── Set Z.AI environment ─────────────────────────────────────
export ANTHROPIC_AUTH_TOKEN="$AUTH_TOKEN"
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export API_TIMEOUT_MS="3000000"

# Model mapping: SDK exercises use CLAUDE_MODEL env var
# Z.AI maps model aliases automatically, but we can also set explicit model
export CLAUDE_MODEL="${GLM_SDK_MODEL:-sonnet}"  # sonnet → glm-4.7 via Z.AI

echo "=========================================="
echo "Running Claude Agent SDK exercises on GLM"
echo "=========================================="
echo "  Base URL:  $ANTHROPIC_BASE_URL"
echo "  Model:     $CLAUDE_MODEL (mapped by Z.AI)"
echo ""

# ── Run exercises ─────────────────────────────────────────────
FILTER="${1:-}"

for f in "$SDK_DIR"/ex0*.py; do
    name="$(basename "$f")"
    if [[ -n "$FILTER" && "$name" != *"$FILTER"* ]]; then
        continue
    fi
    echo "══════════════════════════════════════════"
    echo "  $name (via GLM)"
    echo "══════════════════════════════════════════"
    uv run python "$f" 2>&1
    echo ""
done
