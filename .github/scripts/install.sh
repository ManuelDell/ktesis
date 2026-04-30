#!/bin/bash

set -e

cd ~ || exit

sudo apt-get update
sudo apt-get install -y redis-server libmariadb-dev libffi-dev python3-dev libcups2-dev mariadb-client

echo "Installing frappe-bench..."
pip install --upgrade pip
pip install frappe-bench

echo "Initializing bench (skip assets — backend-only CI)..."
bench init frappe-bench \
  --frappe-branch "${FRAPPE_BRANCH:-version-15}" \
  --python "$(which python)" \
  --skip-assets

cd ~/frappe-bench || exit

echo "Starting Redis on bench-configured ports..."
redis-server config/redis_cache.conf --daemonize yes
redis-server config/redis_queue.conf --daemonize yes
sleep 2

echo "Pre-installing fints von GitHub..."
~/frappe-bench/env/bin/pip install git+https://github.com/raphaelm/python-fints.git

echo "Installing app..."
bench get-app ktesis "${GITHUB_WORKSPACE}"

echo "Creating site..."
bench new-site test_site \
    --db-type mariadb \
    --db-host 127.0.0.1 \
    --db-root-username root \
    --db-root-password "" \
    --admin-password admin \
    --no-mariadb-socket

echo "Installing app to site..."
bench --site test_site install-app ktesis

echo "Setup complete!"
