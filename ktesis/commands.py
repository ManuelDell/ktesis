import json
import os
import shutil
import socket
import subprocess
from datetime import datetime

import click


def _get_primary_ip():
    """Detect the primary non-loopback IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _preflight_checks(cert_dir, nginx_conf, ip):
    """Validate prerequisites before making any changes."""
    errors = []
    warnings = []

    # 1. Check nginx
    if not shutil.which("nginx"):
        errors.append("nginx ist nicht installiert oder nicht im PATH.")
    else:
        try:
            subprocess.run(["nginx", "-v"], capture_output=True, check=True)
        except Exception:
            errors.append("nginx-Binaer funktioniert nicht (nginx -v fehlgeschlagen).")

    # 2. Check openssl
    if not shutil.which("openssl"):
        errors.append("openssl ist nicht installiert oder nicht im PATH.")
    else:
        try:
            subprocess.run(["openssl", "version"], capture_output=True, check=True)
        except Exception:
            errors.append("openssl-Binaer funktioniert nicht.")

    # 3. Check port conflicts
    nginx_running = subprocess.run(
        ["pidof", "nginx"], capture_output=True
    ).returncode == 0

    for port in [80, 443]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip, port))
            s.close()
            if result == 0 and not nginx_running:
                errors.append(f"Port {port} ist belegt und nginx laeuft nicht — anderer Prozess blockiert den Port.")
        except Exception:
            pass

    # 4. Check write permissions
    for path in [cert_dir, os.path.dirname(nginx_conf)]:
        if os.path.exists(path):
            if not os.access(path, os.W_OK):
                errors.append(f"Keine Schreibrechte fuer {path}. Als root ausfuehren (sudo).")
        else:
            parent = os.path.dirname(path)
            if not os.path.exists(parent):
                errors.append(f"Verzeichnis {parent} existiert nicht.")
            elif not os.access(parent, os.W_OK):
                errors.append(f"Keine Schreibrechte um {path} anzulegen. Als root ausfuehren (sudo).")

    return errors, warnings


def _backup_file(path):
    """Create a .bak timestamp backup if file exists."""
    if os.path.exists(path):
        backup_path = f"{path}.bak.{datetime.now():%Y%m%d_%H%M%S}"
        shutil.copy2(path, backup_path)
        return backup_path
    return None


def _write_site_config(bench_path, site, key, value):
    config_path = os.path.join(bench_path, "sites", site, "site_config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"site_config.json nicht gefunden: {config_path}")
    with open(config_path) as f:
        config = json.load(f)
    old_value = config.get(key)
    config[key] = value
    with open(config_path, "w") as f:
        json.dump(config, f, indent="\t")
    return old_value, config_path


def _build_nginx_config(ip, site, gunicorn_port, socketio_port, cert_path, key_path):
    bench_root = os.path.abspath(".")
    sites_path = os.path.join(bench_root, "sites")
    return f"""# Ktesis HTTPS — generiert von bench setup-ktesis-https
# Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}

# HTTP -> HTTPS redirect
server {{
    listen 80;
    server_name {ip};
    return 301 https://{ip}$request_uri;
}}

# Port 2024 (Frappe-Dev-Port) -> HTTPS redirect
server {{
    listen 2024;
    server_name {ip};
    return 301 https://{ip}$request_uri;
}}

# HTTPS server — vollstaendige Frappe-Konfiguration
server {{
    listen 443 ssl;
    server_name {ip};

    ssl_certificate     {cert_path};
    ssl_certificate_key {key_path};
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    root {sites_path};

    client_max_body_size 50m;
    client_body_buffer_size 16K;
    client_header_buffer_size 1k;

    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;

    gzip on;
    gzip_http_version 1.1;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_vary on;
    gzip_types application/atom+xml application/javascript application/json
        application/rss+xml application/xhtml+xml application/xml
        font/opentype image/svg+xml image/x-icon text/css text/plain;

    location /assets {{
        try_files $uri =404;
        add_header Cache-Control "max-age=31536000";
    }}

    location ~ ^/protected/(.*) {{
        internal;
        try_files /{site}/$1 =404;
    }}

    location /socket.io {{
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Frappe-Site-Name {site};
        proxy_set_header Origin $scheme://$http_host;
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:{socketio_port};
    }}

    location / {{
        rewrite ^(.+)/$ $1 permanent;
        rewrite ^(.+)/index\\.html$ $1 permanent;
        rewrite ^(.+)\\.html$ $1 permanent;

        location ~* ^/files/.*\\.(htm|html|svg|xml) {{
            add_header Content-Disposition "attachment";
            try_files /{site}/public/$uri @webserver;
        }}

        try_files /{site}/public/$uri @webserver;
    }}

    location @webserver {{
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Frappe-Site-Name {site};
        proxy_set_header Host $host;
        proxy_set_header X-Use-X-Accel-Redirect True;
        proxy_read_timeout 120;
        proxy_redirect off;
        proxy_pass http://127.0.0.1:{gunicorn_port};
    }}

    access_log /var/log/nginx/ktesis-ssl-access.log;
    error_log  /var/log/nginx/ktesis-ssl-error.log;
}}
"""


@click.command("setup-ktesis-https")
@click.option("--site", required=True, help="Frappe-Site-Name (z.B. development)")
@click.option("--ip", default=None, help="Server-IP (wird automatisch erkannt wenn weggelassen)")
@click.option("--gunicorn-port", default=8000, show_default=True, help="Frappe Gunicorn Port")
@click.option("--socketio-port", default=9000, show_default=True, help="Frappe Socket.IO Port")
@click.option("--cert-dir", default="/etc/ssl/ktesis", show_default=True,
              help="Verzeichnis fuer SSL-Zertifikat und Schluessel")
@click.option("--nginx-conf", default="/etc/nginx/conf.d/ktesis-https.conf", show_default=True,
              help="Pfad der zu schreibenden nginx-Konfigurationsdatei")
@click.option("--skip-nginx-reload", is_flag=True,
              help="nginx nicht automatisch neu laden")
@click.option("--dry-run", is_flag=True,
              help="Nur anzeigen was gemacht wuerde, ohne Aenderungen vorzunehmen")
def setup_ktesis_https(site, ip, gunicorn_port, socketio_port, cert_dir, nginx_conf,
                       skip_nginx_reload, dry_run):
    """Self-signed HTTPS fuer Frappe/Ktesis einrichten.

    Ablauf:
      1. Voraussetzungen pruefen (nginx, openssl, Ports)
      2. Self-signed RSA-4096-Zertifikat mit IP-SAN generieren
      3. nginx-Konfiguration schreiben (HTTP-Redirect + HTTPS-Proxy)
      4. force_https in site_config.json aktivieren
      5. nginx testen und neu laden
      6. Rollback bei Validierungsfehler

    Erfordert Root-Rechte fuer /etc/ssl und /etc/nginx.
    Empfohlener Aufruf: sudo bench setup-ktesis-https --site <site>
    """
    click.echo(click.style("\n=== Ktesis HTTPS Setup ===\n", fg="cyan", bold=True))

    if dry_run:
        click.echo(click.style("[DRY-RUN] Es werden keine Aenderungen vorgenommen.\n", fg="yellow", bold=True))

    if not ip:
        ip = _get_primary_ip()

    bench_path = os.path.abspath(".")
    cert_path = os.path.join(cert_dir, "server.crt")
    key_path = os.path.join(cert_dir, "server.key")

    click.echo(f"Site:         {site}")
    click.echo(f"IP:           {ip}")
    click.echo(f"Bench:        {bench_path}")
    click.echo(f"Zertifikat:   {cert_path}")
    click.echo(f"nginx-Config: {nginx_conf}")
    click.echo()

    # --- Schritt 0: Preflight Checks ---
    click.echo("Schritt 1/5: Voraussetzungen pruefen...")
    errors, warnings = _preflight_checks(cert_dir, nginx_conf, ip)
    for w in warnings:
        click.echo(click.style(f"  WARNUNG: {w}", fg="yellow"))
    if errors:
        for e in errors:
            click.echo(click.style(f"  FEHLER: {e}", fg="red"), err=True)
        click.echo(click.style("\nSetup abgebrochen.", fg="red", bold=True), err=True)
        raise SystemExit(1)
    click.echo(click.style("  ✓ Alle Voraussetzungen erfuellt", fg="green"))

    # --- Schritt 1: Zertifikat ---
    click.echo("Schritt 2/5: Self-signed Zertifikat generieren...")
    cert_backup = None
    key_backup = None
    if dry_run:
        click.echo(f"  [DRY-RUN] Wuerde Zertifikat erstellen: {cert_path}, {key_path}")
    else:
        try:
            os.makedirs(cert_dir, mode=0o755, exist_ok=True)
        except PermissionError:
            click.echo(click.style(f"  FEHLER: Keine Schreibrechte fuer {cert_dir}. Als root ausfuehren.", fg="red"), err=True)
            raise SystemExit(1)

        # Backup existing certs
        if os.path.exists(cert_path):
            cert_backup = _backup_file(cert_path)
            click.echo(f"  Backup erstellt: {cert_backup}")
        if os.path.exists(key_path):
            key_backup = _backup_file(key_path)
            click.echo(f"  Backup erstellt: {key_backup}")

        result = subprocess.run(
            [
                "openssl", "req", "-x509",
                "-newkey", "rsa:4096",
                "-keyout", key_path,
                "-out", cert_path,
                "-days", "3650",
                "-nodes",
                "-subj", "/CN=Ktesis Local/O=Ktesis",
                "-addext", f"subjectAltName=IP:{ip},IP:127.0.0.1",
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            click.echo(click.style(f"  FEHLER: openssl fehlgeschlagen:\n{result.stderr}", fg="red"), err=True)
            raise SystemExit(1)

        os.chmod(key_path, 0o600)
        click.echo(click.style(f"  ✓ {cert_path}", fg="green"))
        click.echo(click.style(f"  ✓ {key_path} (chmod 600)", fg="green"))

    # --- Schritt 2: nginx-Config ---
    click.echo("Schritt 3/5: nginx-Konfiguration schreiben...")
    nginx_backup = None
    nginx_content = _build_nginx_config(ip, site, gunicorn_port, socketio_port, cert_path, key_path)
    if dry_run:
        click.echo("  [DRY-RUN] Wuerde folgende nginx-Config schreiben:")
        click.echo("  " + "\n  ".join(nginx_content.splitlines()))
    else:
        nginx_backup = _backup_file(nginx_conf)
        if nginx_backup:
            click.echo(f"  Backup erstellt: {nginx_backup}")
        try:
            os.makedirs(os.path.dirname(nginx_conf), exist_ok=True)
            with open(nginx_conf, "w") as f:
                f.write(nginx_content)
            click.echo(click.style(f"  ✓ {nginx_conf}", fg="green"))
        except PermissionError:
            click.echo(click.style(f"  FEHLER: Keine Schreibrechte fuer {nginx_conf}. Als root ausfuehren.", fg="red"), err=True)
            raise SystemExit(1)

    # --- Schritt 3: force_https ---
    click.echo("Schritt 4/5: force_https in site_config.json aktivieren...")
    old_force_https = None
    site_config_path = None
    if dry_run:
        click.echo(f"  [DRY-RUN] Wuerde force_https = 1 setzen in site_config.json")
    else:
        try:
            old_force_https, site_config_path = _write_site_config(bench_path, site, "force_https", 1)
            click.echo(click.style("  ✓ force_https = 1", fg="green"))
        except FileNotFoundError as e:
            click.echo(click.style(f"  FEHLER: {e}", fg="red"), err=True)
            click.echo("  force_https manuell setzen: bench --site <site> set-config force_https 1")
        except Exception as e:
            click.echo(click.style(f"  FEHLER: site_config konnte nicht geschrieben werden: {e}", fg="red"), err=True)

    # --- Schritt 4: nginx testen und neu laden ---
    if not skip_nginx_reload and not dry_run:
        click.echo("Schritt 5/5: nginx-Konfiguration testen...")
        test = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if test.returncode != 0:
            click.echo(click.style(f"  FEHLER: nginx-Validierung fehlgeschlagen:\n{test.stderr}", fg="red"), err=True)
            click.echo(click.style("\n  ROLLBACK wird durchgefuehrt...\n", fg="yellow", bold=True))

            # Rollback nginx config
            if nginx_backup and os.path.exists(nginx_backup):
                shutil.copy2(nginx_backup, nginx_conf)
                click.echo(f"  ✓ nginx-Config wiederhergestellt: {nginx_conf}")
            else:
                if os.path.exists(nginx_conf):
                    os.remove(nginx_conf)
                    click.echo(f"  ✓ nginx-Config entfernt: {nginx_conf}")

            # Rollback certs
            if cert_backup and os.path.exists(cert_backup):
                shutil.copy2(cert_backup, cert_path)
                click.echo(f"  ✓ Zertifikat wiederhergestellt: {cert_path}")
            else:
                if os.path.exists(cert_path):
                    os.remove(cert_path)
                    click.echo(f"  ✓ Zertifikat entfernt: {cert_path}")

            if key_backup and os.path.exists(key_backup):
                shutil.copy2(key_backup, key_path)
                click.echo(f"  ✓ Schluessel wiederhergestellt: {key_path}")
            else:
                if os.path.exists(key_path):
                    os.remove(key_path)
                    click.echo(f"  ✓ Schluessel entfernt: {key_path}")

            # Rollback site config
            if old_force_https is not None and site_config_path:
                with open(site_config_path) as f:
                    config = json.load(f)
                config["force_https"] = old_force_https
                with open(site_config_path, "w") as f:
                    json.dump(config, f, indent="\t")
                click.echo(f"  ✓ force_https auf {old_force_https} zurueckgesetzt")

            # Re-test nginx after rollback
            retest = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
            if retest.returncode == 0:
                click.echo(click.style("  ✓ nginx-Config nach Rollback gueltig", fg="green"))
                subprocess.run(["systemctl", "reload", "nginx"], capture_output=True)
                click.echo(click.style("  ✓ nginx neu geladen (nach Rollback)", fg="green"))
            else:
                click.echo(click.style(f"  WARNUNG: nginx-Config nach Rollback immer noch ungueltig!\n{retest.stderr}", fg="yellow"), err=True)

            click.echo(click.style("\nSetup abgebrochen (Rollback durchgefuehrt).", fg="red", bold=True), err=True)
            raise SystemExit(1)

        click.echo(click.style("  ✓ nginx-Config gueltig", fg="green"))

        reload_result = subprocess.run(["systemctl", "reload", "nginx"], capture_output=True, text=True)
        if reload_result.returncode == 0:
            click.echo(click.style("  ✓ nginx neu geladen", fg="green"))
        else:
            click.echo(click.style("  WARNUNG: nginx reload fehlgeschlagen – manuell ausfuehren:", fg="yellow"))
            click.echo("    systemctl reload nginx")
    elif dry_run:
        click.echo("Schritt 5/5: [DRY-RUN] Wuerde nginx testen und neu laden")
    else:
        click.echo("Schritt 5/5: Uebersprungen (--skip-nginx-reload)")

    click.echo(click.style("\n=== Setup abgeschlossen! ===\n", fg="green", bold=True))
    click.echo(f"  Ktesis:  https://{ip}/ktesis")
    click.echo(f"  Desk:    https://{ip}/app")
    click.echo()
    click.echo("  Zertifikatswarnung im Browser einmalig bestaetigen.")


# Frappe bench helper discovery
commands = [setup_ktesis_https]
