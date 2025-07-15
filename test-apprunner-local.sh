#!/bin/bash

# Test App Runner build locally using Docker
echo "🧪 Testing App Runner build locally..."

# Create a Dockerfile that simulates App Runner environment
cat > Dockerfile.apprunner-test << 'EOF'
# Use the same base image as App Runner for Python
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /var/task

# Copy all files
COPY . .

# Simulate App Runner pre-build commands
RUN echo "Installing Node.js..." && \
    yum update -y && \
    curl -fsSL https://rpm.nodesource.com/setup_16.x -o setup_nodejs.sh && \
    bash setup_nodejs.sh && \
    yum install -y nodejs && \
    npm --version && \
    node --version && \
    npm install -g pnpm@7.32.5 && \
    echo "Building Next.js frontend..." && \
    pnpm install --frozen-lockfile && \
    pnpm build && \
    echo "Frontend build completed"

# Simulate App Runner build commands  
RUN echo "Installing Python dependencies..." && \
    pip install -r requirements.txt && \
    echo "Python dependencies installed"

# Install gunicorn
RUN pip install gunicorn

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=./api
ENV CLINICAL_TRIALS_API_URL=https://clinicaltrials.gov/api/v2
ENV ENABLE_CLAUDE_PROVIDER=true
ENV ENABLE_OPENAI_PROVIDER=true
ENV ENABLE_QA_SYSTEM=true
ENV MAX_EXTRACTION_RETRIES=3
ENV REQUEST_TIMEOUT_MS=30000

# Expose port
EXPOSE 8000

# Run the same command as App Runner
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "api.index:app"]
EOF

echo "🐳 Building Docker image to test App Runner setup..."
docker build -f Dockerfile.apprunner-test -t apprunner-test .

if [ $? -eq 0 ]; then
    echo "✅ Build successful! Testing the application..."
    echo "🚀 Starting the application on port 8000..."
    echo "📱 Open http://localhost:8000 to test your application"
    echo "📋 API docs at http://localhost:8000/docs"
    echo "❤️ Health check at http://localhost:8000/api/health"
    echo ""
    echo "Press Ctrl+C to stop the application"
    
    docker run -p 8000:8000 --rm -it apprunner-test
else
    echo "❌ Build failed! Check the errors above."
    echo "This is likely the same issue affecting App Runner."
fi

# Cleanup
echo "🧹 Cleaning up..."
docker rmi apprunner-test 2>/dev/null || true
rm Dockerfile.apprunner-test 2>/dev/null || true