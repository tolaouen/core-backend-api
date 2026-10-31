#!/usr/bin/env sh
set -eu

echo "Building and deploying services with Docker Compose..."
docker compose up -d --build

echo "Applying migrations inside web container..."
docker compose exec web alembic upgrade head

echo "Running test suite inside web container..."
docker compose exec web pytest -q

echo "Running HTTP smoke test on deployed container..."
curl --fail --silent --show-error http://localhost:8000/ > /dev/null

echo "Docker deploy + migration + tests completed successfully."
