def after_install():
    _build_frontend()
    _print_https_hint()


def _build_frontend():
    import os
    import shutil
    import subprocess

    bench_path = os.path.abspath(".")
    frontend_path = os.path.join(bench_path, "apps", "ktesis", "frontend")

    if not os.path.isdir(frontend_path):
        print(f"\n  WARNUNG: Frontend-Verzeichnis nicht gefunden: {frontend_path}")
        print("  Frontend-Build übersprungen.\n")
        return

    if not shutil.which("npm"):
        print("\n  WARNUNG: npm nicht gefunden – Frontend-Build übersprungen.")
        print("  Manuell nachholen:")
        print(f"    cd {frontend_path} && npm install && npm run build\n")
        return

    print("\nBaue ktesis Frontend...")

    for cmd in [["npm", "install"], ["npm", "run", "build"]]:
        result = subprocess.run(cmd, cwd=frontend_path)
        if result.returncode != 0:
            print(f"\n  Fehler bei: {' '.join(cmd)}")
            print("  Manuell nachholen:")
            print(f"    cd {frontend_path} && npm install && npm run build\n")
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
│  ⚠  Development Stage – nicht für Produktionsumgebungen.            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
""")
