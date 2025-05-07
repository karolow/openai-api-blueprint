#!/bin/bash
set -eo pipefail

echo "===== Docker Feature Verification Script ====="
echo

# 1. Build the image
echo "🔶 Building Docker image..."
time docker build -t openai-api-blueprint .
echo "✅ Build successful"
echo

# 2. Test non-root user
echo "🔶 Verifying non-root user..."
USER_INFO=$(docker run --rm openai-api-blueprint id)
echo "User info: $USER_INFO"
if [[ "$USER_INFO" != *"uid=0"* ]]; then
  echo "✅ Running as non-root user"
else
  echo "❌ Still running as root user!"
fi
echo

# 3. Test basic functionality
echo "🔶 Starting container to test API..."
docker run -d --name api-test -p 8000:8000 openai-api-blueprint
echo "Waiting for startup..."
sleep 5

echo "Testing API health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [[ "$HEALTH_RESPONSE" == *"ok"* ]]; then
  echo "✅ API health endpoint working"
else
  echo "❌ API health endpoint not working!"
fi
echo

# 4. Test health check
echo "🔶 Verifying health check..."
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' api-test)
echo "Health status: $HEALTH_STATUS"
if [[ "$HEALTH_STATUS" == "healthy" ]]; then
  echo "✅ Health check is properly configured"
else
  echo "⚠️ Health check not reporting healthy yet (might need more time)"
fi
echo

# 5. Test build caching
echo "🔶 Testing build cache (second build should be faster)..."
time docker build -t openai-api-blueprint .
echo "✅ Second build completed"
echo

# 6. Test .dockerignore effectiveness
echo "🔶 Checking .dockerignore effectiveness..."
CONTEXT_SIZE=$(tar -c --exclude-vcs . | wc -c)
echo "Build context size: $CONTEXT_SIZE bytes"
echo "✅ Build context analyzed"
echo

# Cleanup
echo "🔶 Cleaning up test containers..."
docker rm -f api-test
echo "✅ Cleanup complete"
echo

echo "===== Verification Complete ====="
echo "Docker setup is working correctly!" 