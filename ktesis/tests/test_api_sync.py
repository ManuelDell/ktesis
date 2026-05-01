"""
Frontend-Backend Sync-Tests.
Prueft ob alle API-Calls im Frontend einen passenden @frappe.whitelist() Backend-Endpunkt haben.
"""
from __future__ import annotations
import re
import os
import unittest
from pathlib import Path

APP_ROOT = Path(__file__).parent.parent.parent  # apps/ktesis/
FRONTEND_SRC = APP_ROOT / "frontend" / "src"
BACKEND_API = APP_ROOT / "ktesis" / "api"


def _collect_frontend_calls() -> set[str]:
    """Extrahiert alle ktesis.api.* Aufrufe aus Vue/JS Dateien."""
    calls = set()
    pattern = re.compile(r"['\"]ktesis\.api\.[a-z_.]+['\"]")
    for path in FRONTEND_SRC.rglob("*.vue"):
        text = path.read_text(errors="ignore")
        for match in pattern.findall(text):
            calls.add(match.strip("'\""))
    for path in FRONTEND_SRC.rglob("*.js"):
        if "node_modules" in str(path):
            continue
        text = path.read_text(errors="ignore")
        for match in pattern.findall(text):
            calls.add(match.strip("'\""))
    return calls


def _collect_backend_endpoints() -> set[str]:
    """Findet alle @frappe.whitelist() dekorierten Funktionen."""
    endpoints = set()
    func_re = re.compile(r"^def ([a-z_][a-z0-9_]*)\s*\(", re.MULTILINE)

    for path in BACKEND_API.glob("*.py"):
        if path.name.startswith("_") and path.name != "__init__.py":
            continue
        if path.name == "__init__.py":
            module = "ktesis.api"
        else:
            module = "ktesis.api." + path.stem
        text = path.read_text(errors="ignore")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "@frappe.whitelist()" in line:
                # Find the next def line
                for j in range(i + 1, min(i + 5, len(lines))):
                    m = func_re.match(lines[j])
                    if m:
                        endpoints.add(f"{module}.{m.group(1)}")
                        break
    return endpoints


class TestFrontendBackendSync(unittest.TestCase):

    def setUp(self):
        self.frontend_calls = _collect_frontend_calls()
        self.backend_endpoints = _collect_backend_endpoints()

    def test_all_frontend_calls_have_backend(self):
        """Jeder Frontend-Call muss einen @frappe.whitelist() Backend-Endpunkt haben."""
        missing = self.frontend_calls - self.backend_endpoints
        self.assertEqual(
            missing, set(),
            f"Frontend ruft nicht-existierende Endpunkte auf:\n" +
            "\n".join(f"  - {m}" for m in sorted(missing))
        )

    def test_no_orphan_endpoints(self):
        """Optional: Warnung fuer Backend-Endpunkte die vom Frontend nicht verwendet werden."""
        # Nicht als Fehler, nur als Info
        orphans = self.backend_endpoints - self.frontend_calls
        if orphans:
            print(f"\n  INFO: {len(orphans)} Backend-Endpunkte nicht vom Frontend genutzt:")
            for o in sorted(orphans):
                print(f"    - {o}")

    def test_whitelist_decorator_not_on_constant(self):
        """@frappe.whitelist() darf nicht ueber einer Konstante stehen."""
        for path in BACKEND_API.glob("*.py"):
            text = path.read_text(errors="ignore")
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if "@frappe.whitelist()" in line:
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            self.assertTrue(
                                next_line.startswith("def "),
                                f"{path.name}:{j+1}: @frappe.whitelist() steht ueber '{next_line}' statt ueber einer def"
                            )
                            break

    def test_csrf_token_correct(self):
        """useApi.js soll window.frappe?.csrf_token verwenden."""
        useapi = FRONTEND_SRC / "composables" / "useApi.js"
        if useapi.exists():
            text = useapi.read_text()
            self.assertNotIn(
                "window.csrf_token ||",
                text.replace("window.frappe?.csrf_token || window.csrf_token", "PLACEHOLDER"),
                "useApi.js: window.csrf_token ohne frappe-Fallback gefunden"
            )

    def test_import_bankbuchungen_is_whitelisted(self):
        """import_bankbuchungen() muss @frappe.whitelist() haben."""
        csv_import = BACKEND_API / "csv_import.py"
        self.assertIn(
            "ktesis.api.csv_import.import_bankbuchungen",
            self.backend_endpoints,
            "import_bankbuchungen hat keinen @frappe.whitelist() Decorator!"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
