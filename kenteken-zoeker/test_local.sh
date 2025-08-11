#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL moet gezet zijn (bv. Supabase connectiestring)}"
API_PORT="${API_PORT:-8000}"
UPLOAD_TOKEN="${UPLOAD_TOKEN:-lokale-test-token}"

pushd api >/dev/null
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt >/dev/null
UVICORN_LOG_LEVEL=${UVICORN_LOG_LEVEL:-warning} uvicorn api.main:app --port ${API_PORT} --log-level warning &
API_PID=$!
popd >/dev/null

sleep 2

echo "Zoektest (verwacht geen data tenzij je records hebt):"
curl -s "http://localhost:${API_PORT}/search?kenteken=G-123-AB" || true

echo "Uploadtest zonder token (verwacht 401):"
set +e
curl -s -X POST -F "file=@/etc/hosts" -F "source_name=TestUpload" "http://localhost:${API_PORT}/upload"
echo
echo "Uploadtest met token maar geen Excel (verwacht 400):"
curl -s -X POST -H "X-Upload-Token: ${UPLOAD_TOKEN}" -F "file=@/etc/hosts" -F "source_name=TestUpload" "http://localhost:${API_PORT}/upload"
set -e

kill ${API_PID} || true
wait ${API_PID} 2>/dev/null || true

echo "Klaar."