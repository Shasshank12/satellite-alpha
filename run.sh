#!/bin/bash
# One-shot launcher. Run from project root.

set -e

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: set ANTHROPIC_API_KEY in .env or environment"
  exit 1
fi

echo "🛰️  Starting Satellite Alpha..."

# Install deps if needed
if ! python -c "import anthropic, fastapi" 2>/dev/null; then
  echo "📦 Installing dependencies..."
  pip install -q -r backend/requirements.txt
fi

# Start backend in background
cd backend
python server.py &
BACKEND_PID=$!
cd ..

trap "kill $BACKEND_PID 2>/dev/null" EXIT

echo ""
echo "✅ Backend on http://localhost:8000"
echo "✅ Frontend on http://localhost:3000"
echo ""
echo "Open http://localhost:3000 in your browser"
echo "Ctrl+C to stop"

cd frontend
python -m http.server 3000
