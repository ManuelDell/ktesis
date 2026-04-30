#!/bin/bash
set -e

FRAPPE_BRANCH=${FRAPPE_BRANCH:-version-15}
BENCH_PATH=$HOME/frappe-bench

echo "=== Bench initialisieren (frappe $FRAPPE_BRANCH) ==="
bench init \
  --frappe-branch "$FRAPPE_BRANCH" \
  --skip-assets \
  "$BENCH_PATH"

cd "$BENCH_PATH"

echo "=== MariaDB-Benutzer anlegen ==="
mariadb -h 127.0.0.1 -u root -proot << 'SQL'
CREATE USER IF NOT EXISTS 'test_frappe'@'localhost' IDENTIFIED BY 'test_frappe';
GRANT ALL PRIVILEGES ON *.* TO 'test_frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SQL

echo "=== Site anlegen ==="
bench new-site test_site \
  --db-root-username root \
  --db-root-password root \
  --admin-password admin \
  --no-mariadb-socket

echo "=== ktesis aus lokalem Checkout installieren ==="
bench get-app ktesis "$GITHUB_WORKSPACE"
bench --site test_site install-app ktesis

echo "=== Setup abgeschlossen ==="
