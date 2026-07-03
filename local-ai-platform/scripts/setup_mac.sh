#!/usr/bin/env bash
# One-time setup for the Local AI Platform on macOS (Apple Silicon optimized).
# Installs Ollama, pulls the starter models, creates a Python venv, and
# installs the platform's dependencies. Everything stays on this machine.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/4 Ollama (local model runtime)"
if ! command -v ollama >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install ollama
  else
    echo "Homebrew not found. Install Ollama from https://ollama.com/download/mac then re-run."
    exit 1
  fi
fi
# Start the Ollama server if it isn't already running.
if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Starting ollama serve in the background..."
  (ollama serve >/tmp/ollama.log 2>&1 &)
  sleep 3
fi

echo "==> 2/4 Pulling starter models (fast chat + quality chat + embeddings)"
ollama pull llama3.2:3b        # fast: quick tasks, classification, extraction
ollama pull qwen2.5:7b         # quality: reasoning, summaries, drafting
ollama pull nomic-embed-text   # embeddings: document search / RAG

echo "==> 3/4 Python environment"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip -q
./.venv/bin/pip install -r requirements.txt -q

echo "==> 4/4 Done"
cat <<'EOF'

Start the platform:
  ./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8130

Then open the dashboard:  http://127.0.0.1:8130
API docs (OpenAPI):       http://127.0.0.1:8130/docs

Everything runs locally. No data leaves this Mac unless you explicitly
start the server with LAP_ALLOW_CLOUD=true AND turn on cloud mode.
EOF
