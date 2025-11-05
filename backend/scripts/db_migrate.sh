#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export ALEMBIC_CONFIG=alembic.ini

# Substitute DATABASE_URL from environment if provided
if [[ -n "${DATABASE_URL:-}" ]]; then
  sed -i.bak "s#^sqlalchemy.url = .*#sqlalchemy.url = ${DATABASE_URL}#" "$ALEMBIC_CONFIG"
fi

alembic upgrade head
