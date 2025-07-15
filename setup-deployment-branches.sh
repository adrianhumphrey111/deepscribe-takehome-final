#!/bin/bash

# Setup separate Git branches for backend and frontend deployments
set -e

echo "🌿 Setting up deployment branches for App Runner..."

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Create and setup backend branch
echo "🐍 Creating backend deployment branch..."
git checkout -b backend-deploy

# Replace apprunner.yaml with backend configuration
cat > apprunner.yaml << 'EOF'
version: 1.0
runtime: python3
build:
  commands:
    build:
      - echo "Installing Python dependencies..."
      - pip install -r requirements.txt
run:
  runtime-version: 3.11
  command: gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 300 api.index:app
  network:
    port: 8000
    env: PORT
  env:
    - name: FLASK_ENV
      value: production
    - name: PORT
      value: "8000"
    - name: CLINICAL_TRIALS_API_URL
      value: https://clinicaltrials.gov/api/v2
    - name: ENABLE_CLAUDE_PROVIDER
      value: "true"
    - name: ENABLE_OPENAI_PROVIDER
      value: "true"
    - name: ENABLE_QA_SYSTEM
      value: "true"
    - name: MAX_EXTRACTION_RETRIES
      value: "3"
    - name: REQUEST_TIMEOUT_MS
      value: "30000"
EOF

# Remove frontend-specific files from backend branch
echo "🗑️  Removing frontend files from backend branch..."
rm -rf app/ components/ lib/api.ts
rm -f next.config.js tailwind.config.js tsconfig.json
rm -f package.json pnpm-lock.yaml
rm -f .env.production

# Commit backend configuration
git add .
git commit -m "Backend deployment configuration

- Python runtime with Flask/Gunicorn
- Only backend API files included
- Production environment variables set"

echo "✅ Backend branch created and configured"

# Switch back to main and create frontend branch
git checkout $CURRENT_BRANCH
echo "🌐 Creating frontend deployment branch..."
git checkout -b frontend-deploy

# Replace apprunner.yaml with frontend configuration
cat > apprunner.yaml << 'EOF'
version: 1.0
runtime: nodejs20
build:
  commands:
    build:
      - echo "Installing Node.js dependencies..."
      - npm install -g pnpm
      - pnpm install
      - echo "Building Next.js application..."
      - NODE_ENV=production pnpm build
run:
  runtime-version: 20
  command: pnpm start
  network:
    port: 3000
    env: PORT
  env:
    - name: NODE_ENV
      value: production
    - name: PORT
      value: "3000"
    - name: NEXT_PUBLIC_API_URL
      value: "https://your-backend-url.us-east-1.awsapprunner.com"
EOF

# Remove backend-specific files from frontend branch
echo "🗑️  Removing backend files from frontend branch..."
rm -rf api/
rm -f requirements.txt run_flask.py

# Commit frontend configuration
git add .
git commit -m "Frontend deployment configuration

- Node.js runtime with Next.js
- Only frontend files included
- Environment variable for backend API URL"

echo "✅ Frontend branch created and configured"

# Switch back to main branch
git checkout $CURRENT_BRANCH

echo ""
echo "🎉 Deployment branches created successfully!"
echo ""
echo "📋 Deployment Instructions:"
echo ""
echo "1️⃣  Deploy Backend:"
echo "   - Push backend branch: git push origin backend-deploy"
echo "   - Create App Runner service pointing to 'backend-deploy' branch"
echo "   - Copy the backend URL when deployment completes"
echo ""
echo "2️⃣  Update Frontend Config:"
echo "   - git checkout frontend-deploy"
echo "   - Update NEXT_PUBLIC_API_URL in apprunner.yaml with backend URL"
echo "   - git commit -am 'Update backend API URL' && git push origin frontend-deploy"
echo ""
echo "3️⃣  Deploy Frontend:"
echo "   - Create second App Runner service pointing to 'frontend-deploy' branch"
echo ""
echo "🌿 Available branches:"
echo "   - $CURRENT_BRANCH (main development)"
echo "   - backend-deploy (Flask API only)"
echo "   - frontend-deploy (Next.js app only)"