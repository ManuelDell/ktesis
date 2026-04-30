#!/bin/bash

set -e

cd ~ || exit

sudo apt-get update
sudo apt-get install -y redis-server libmariadb-dev libffi-dev python3-dev libcups2-dev

echo "Starting Redis..."
sudo redis-server /etc/redis/redis.conf &

echo "Installing frappe-bench..."
pip install --upgrade pip
pip install frappe-bench

echo "Initializing bench..."
bench init frappe-bench --frappe-branch "${FRAPPE_BRANCH:-version-15}" --python "$(which python)"

cd ~/frappe-bench || exit

echo "Installing app..."
bench get-app ktesis "${GITHUB_WORKSPACE}"

echo "Creating site..."
printf 'root\n' | bench new-site test_site \
    --db-type mariadb \
    --db-root-password root \
    --admin-password admin

echo "Installing app to site..."
bench --site test_site install-app ktesis

echo "Setup complete!"
