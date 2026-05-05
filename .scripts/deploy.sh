#!/bin/bash
set -e # exit on first error

REPO="/home/aimebgl3/python/travel-dev"
VENV_ACTIVATE="/home/aimebgl3/virtualenv/python/travel-dev/3.13/bin/activate"

echo "🚀 Starting deployment..."
cd "$REPO"

OLD_COMMIT="$(git rev-parse HEAD)"

echo "📥 Pulling latest code from GitHub..."
git pull origin dev-deni

echo "🔧 Activating virtual environment..."
source "$VENV_ACTIVATE"

echo "📦 Installing/updating dependencies..."
pip install -e .

echo "🧪 Running tests..."
if pytest; then
  :
else
  git reset --hard "$OLD_COMMIT"
  pip install -e .
  echo "❌ Tests failed — reverted back to previous commit"
  exit 1
fi

echo "🔄 Restarting application server..."
touch "tmp/restart.txt"

echo "🏥 Running health check..."
sleep 5
curl -sf https://travel-dev.aime.bg/ || echo "Health check failed"
echo "✅ Project deployed successfully."
