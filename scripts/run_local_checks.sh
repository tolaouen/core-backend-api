#!/usr/bin/env sh
set -eu

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "Running Alembic migrations locally..."
"$PYTHON" -m alembic upgrade head

echo "Running local tests..."
"$PYTHON" -m pytest -q

echo "Local migration + tests completed successfully."
