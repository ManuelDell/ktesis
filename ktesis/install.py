def after_install():
    _build_frontend()
    _print_https_hint()


def _build_frontend():
    import os
    import shutil
    import subprocess

    # __file__ = apps/ktesis/ktesis/install.py → app root = apps/ktesis/
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    frontend_path = os.path.join(app_path, "frontend")
    assets_path = os.path.join(app_path, "ktesis", "public", "frontend", "assets")

    # Vorgebaute Assets vorhanden → kein Build noetig
    if os.path.isdir(assets_path) and any(f.endswith(".js") for f in os.listdir(assets_path)):
        return

    if not os.path.isdir(frontend_path):
        print(f"\n  WARNUNG: Frontend-Verzeichnis nicht gefunden: {frontend_path}")
        print("  Frontend-Build uebersprungen.\n")
        return

    if not shutil.which("npm"):
        print("\n  WARNUNG: npm nicht gefunden - Frontend-Build uebersprungen.")
        print(f"  Manuell: cd {frontend_path} && npm install && npm run build\n")
        return

    print("\nBaue ktesis Frontend...")
    for cmd in [["npm", "install"], ["npm", "run", "build"]]:
        result = subprocess.run(cmd, cwd=frontend_path)
        if result.returncode != 0:
            print(f"\n  Fehler bei: {' '.join(cmd)}")
            print(f"  Manuell: cd {frontend_path} && npm install && npm run build\n")
            return
    print("  Frontend erfolgreich gebaut.\n")


def _print_https_hint():
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                       Ktesis installiert ✓                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  HTTPS einrichten (optional, experimentell):                        │
│                                                                     │
│    sudo bench setup-ktesis-https --site <deine-site>                │
│                                                                     │
│  Erfordert root-Rechte (schreibt in /etc/ssl und /etc/nginx).       │
│  Weitere Infos: README.md → HTTPS einrichten                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
""")
