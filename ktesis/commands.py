import json
import os
import subprocess
from datetime import datetime

import click


def _get_primary_ip():
    """Detect the primary non-loopback IPv4 address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _write_site_config(bench_path, site, key, value):
    config_path = os.path.join(bench_path, "sites", site, "site_config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"site_config.json nicht gefunden: {config_path}")
    with open(config_path) as f:
        config = json.load(f)
    config[key] = value
    with open(config_path, "w") as f:
        json.dump(config, f, indent="\t")


def _build_nginx_config(ip, gunicorn_port, socketio_port, cert_path, key_path):
    return f"""# Ktesis HTTPS – generiert von `bench setup-ktesis-https`
# DEVELOPMENT STAGE – experimentell, nicht produktionsreif
# Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}

server {{
    listen 443 ssl;
    server_name {ip};

    ssl_certificate     {cert_path};
    ssl_certificate_key {key_path};
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;

    location / {{
        proxy_pass         http://127.0.0.1:{gunicorn_port};
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto https;
        proxy_read_timeout 120;
        proxy_connect_timeout 10;
    }}

    location /socket.io {{
        proxy_pass         http://127.0.0.1:{socketio_port};
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_set_header   X-Forwarded-Proto https;
    }}
}}
"""


@click.command("setup-ktesis-https")
@click.option("--site", required=True, help="Frappe-Site-Name (z.B. mysite.localhost)")
@click.option("--ip", default=None, help="Server-IP (wird automatisch erkannt wenn weggelassen)")
@click.option("--gunicorn-port", default=8000, show_default=True, help="Frappe Gunicorn Port")
@click.option("--socketio-port", default=9000, show_default=True, help="Frappe Socket.IO Port")
@click.option("--cert-dir", default="/etc/ssl/ktesis", show_default=True,
              help="Verzeichnis für SSL-Zertifikat und Schlüssel")
@click.option("--nginx-conf", default="/etc/nginx/conf.d/ktesis-https.conf", show_default=True,
              help="Pfad der zu schreibenden nginx-Konfigurationsdatei")
@click.option("--skip-nginx-reload", is_flag=True,
              help="nginx nicht automatisch neu laden")
def setup_ktesis_https(site, ip, gunicorn_port, socketio_port, cert_dir, nginx_conf, skip_nginx_reload):
    """[EXPERIMENTAL] Self-signed HTTPS für Frappe/Ktesis einrichten.

    \b
    Ablauf:
      1. Self-signed RSA-4096-Zertifikat mit IP-SAN generieren
      2. nginx-Konfiguration nach --nginx-conf schreiben
      3. force_https in site_config.json aktivieren
      4. nginx testen und neu laden

    Erfordert Root-Rechte für /etc/ssl und /etc/nginx.
    Empfohlener Aufruf: sudo bench setup-ktesis-https --site <site>
    """
    click.echo(click.style(
        "\n  DEVELOPMENT STAGE – experimentell, nicht produktionsreif\n",
        fg="yellow", bold=True,
    ))

    if not ip:
        ip = _get_primary_ip()
        click.echo(f"  IP automatisch erkannt: {ip}")

    bench_path = os.path.abspath(".")

    click.echo(f"  Site:         {site}")
    click.echo(f"  Bench:        {bench_path}")
    click.echo(f"  Zertifikat:   {cert_dir}/")
    click.echo(f"  nginx-Config: {nginx_conf}")
    click.echo()

    # --- 1. Zertifikat ---
    cert_path = os.path.join(cert_dir, "server.crt")
    key_path  = os.path.join(cert_dir, "server.key")

    click.echo("Generiere self-signed Zertifikat (RSA 4096, 10 Jahre Laufzeit)...")
    try:
        os.makedirs(cert_dir, mode=0o755, exist_ok=True)
    except PermissionError:
        click.echo(click.style(f"  Keine Schreibrechte für {cert_dir}. Als root ausführen.", fg="red"), err=True)
        raise SystemExit(1)

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
        click.echo(click.style(f"  openssl fehlgeschlagen:\n{result.stderr}", fg="red"), err=True)
        raise SystemExit(1)

    os.chmod(key_path, 0o600)
    click.echo(click.style(f"  ✓ {cert_path}", fg="green"))
    click.echo(click.style(f"  ✓ {key_path} (chmod 600)", fg="green"))

    # --- 2. nginx-Config ---
    click.echo("Schreibe nginx-Konfiguration...")
    nginx_content = _build_nginx_config(ip, gunicorn_port, socketio_port, cert_path, key_path)
    try:
        os.makedirs(os.path.dirname(nginx_conf), exist_ok=True)
        with open(nginx_conf, "w") as f:
            f.write(nginx_content)
        click.echo(click.style(f"  ✓ {nginx_conf}", fg="green"))
    except PermissionError:
        click.echo(click.style(f"  Keine Schreibrechte für {nginx_conf}. Als root ausführen.", fg="red"), err=True)
        raise SystemExit(1)

    # --- 3. force_https ---
    click.echo("Aktiviere force_https in site_config.json...")
    try:
        _write_site_config(bench_path, site, "force_https", 1)
        click.echo(click.style("  ✓ force_https = 1", fg="green"))
    except FileNotFoundError as e:
        click.echo(click.style(f"  {e}", fg="red"), err=True)
        click.echo("  force_https manuell setzen: bench --site <site> set-config force_https 1")
    except Exception as e:
        click.echo(click.style(f"  site_config konnte nicht geschrieben werden: {e}", fg="red"), err=True)

    # --- 4. nginx testen und neu laden ---
    if not skip_nginx_reload:
        click.echo("Teste nginx-Konfiguration...")
        test = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if test.returncode != 0:
            click.echo(click.style(f"  nginx-Fehler:\n{test.stderr}", fg="red"), err=True)
            click.echo("  nginx-Config wurde geschrieben aber nicht geladen.")
            click.echo(f"  Manuell prüfen: nginx -t && systemctl reload nginx")
            raise SystemExit(1)
        click.echo(click.style("  ✓ nginx-Config gültig", fg="green"))

        reload_result = subprocess.run(["systemctl", "reload", "nginx"], capture_output=True, text=True)
        if reload_result.returncode == 0:
            click.echo(click.style("  ✓ nginx neu geladen", fg="green"))
        else:
            click.echo(click.style("  nginx reload fehlgeschlagen – manuell ausführen:", fg="yellow"))
            click.echo("    systemctl reload nginx")

    click.echo(click.style("\n  Fertig!\n", fg="green", bold=True))
    click.echo(f"  Ktesis:  https://{ip}/ktesis")
    click.echo(f"  Desk:    https://{ip}/app")
    click.echo()
    click.echo("  Zertifikatswarnung im Browser einmalig bestätigen.")
    click.echo(click.style(
        "\n  Hinweis: Experimentelles Feature. Sicherheitshinweise in der README beachten.\n",
        fg="yellow",
    ))
