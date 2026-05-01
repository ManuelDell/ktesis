#!/bin/bash
# Pre-push tests fuer ktesis — Frontend/Backend Sync
set -e

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "=== ktesis Pre-Push Tests ==="

cd "$APP_DIR"

# 1. Frontend-Backend Sync Tests
echo ""
echo "--- Frontend-Backend Sync ---"
python3 ktesis/tests/test_api_sync.py -v
if [ $? -ne 0 ]; then
  echo "FEHLER: Frontend-Backend Sync Tests fehlgeschlagen!"
  exit 1
fi

# 2. CSV Import Unit Tests
echo ""
echo "--- CSV Import Unit Tests ---"
python3 ktesis/tests/test_csv_import.py -v
if [ $? -ne 0 ]; then
  echo "FEHLER: CSV Import Tests fehlgeschlagen!"
  exit 1
fi

# 3. Python Syntax Check aller API-Dateien
echo ""
echo "--- Python Syntax Check ---"
find ktesis/api -name "*.py" | while read f; do
  python3 -m py_compile "$f" && echo "  OK: $f" || { echo "  FEHLER: $f"; exit 1; }
done

echo ""
echo "=== Alle Tests bestanden ✓ ==="
