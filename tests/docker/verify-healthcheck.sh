#!/bin/bash
set -eo pipefail

echo "===== Docker Health Check Verification Script ====="
echo

# Remove any existing test container
echo "🔶 Cleaning up any existing test containers..."
docker rm -f api-test 2>/dev/null || true
echo "✅ Cleanup complete"
echo

# Build the image
echo "🔶 Building Docker image..."
docker build -t openai-api-blueprint .
echo "✅ Build successful"
echo

# Start a container
echo "🔶 Starting container to test health check..."
docker run -d --name api-test -p 8000:8000 openai-api-blueprint
container_id=$(docker ps -q --filter "name=api-test")
echo "✅ Container started with ID: $container_id"
echo

# Wait for the container to become healthy
echo "🔶 Waiting for container to be healthy..."
max_wait=60  # seconds
end_time=$(($(date +%s) + max_wait))

while [ $(date +%s) -lt $end_time ]; do
  health_status=$(docker inspect --format='{{.State.Health.Status}}' api-test)
  echo "Health status: $health_status"
  
  if [ "$health_status" = "healthy" ]; then
    echo "✅ Container is healthy!"
    break
  fi
  
  sleep 5
done

if [ "$health_status" != "healthy" ]; then
  echo "❌ Container failed to become healthy within $max_wait seconds"
  docker logs api-test
  docker rm -f api-test
  exit 1
fi
echo

# Test health check failure detection
echo "🔶 Testing health check failure detection..."
echo "Killing the uvicorn process to simulate a failure..."
docker exec api-test pkill uvicorn || echo "Failed to kill process, container may not have the pkill command"

# Wait for health check to detect failure
echo "Waiting for health check to detect failure..."
sleep 10

# Check if the health check detected the failure
health_status=$(docker inspect --format='{{.State.Health.Status}}' api-test)
echo "Health status after killing uvicorn: $health_status"

if [ "$health_status" = "unhealthy" ]; then
  echo "✅ Health check correctly detected failure!"
else
  echo "⚠️ Health check did not detect the failure in time"
fi

# Cleanup
echo "🔶 Cleaning up test containers..."
docker rm -f api-test
echo "✅ Cleanup complete"
echo

echo "===== Health Check Verification Complete =====" 