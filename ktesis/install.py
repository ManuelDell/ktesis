def after_install():
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
