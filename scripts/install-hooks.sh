#!/bin/bash
# Installiert git hooks fuer ktesis Entwickler
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cp "$SCRIPT_DIR/pre-push-check.sh" "$REPO_DIR/.git/hooks/pre-push"
chmod +x "$REPO_DIR/.git/hooks/pre-push"
echo "✓ pre-push hook installiert"
echo "  Wird ausgefuehrt bei: git push"
