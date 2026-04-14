#!/bin/bash

# Run script for Wazy Agent using Generic Agent Docker Image
# Usage: ./run.sh [OPTIONS]

set -e

# Default values
TAG="${TAG:-latest}"
IMAGE_NAME="declarative-agent"
CONTAINER_NAME="wazy-agent-container"
PORT="${PORT:-10004}"

# Get the script directory (wazy_agent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if .env file exists
if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    echo "Warning: .env file not found at ${SCRIPT_DIR}/.env"
    echo "Please create one from .env.example"
    exit 1
fi

echo "========================================"
echo "Running Wazy Agent Container" 
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Container: ${CONTAINER_NAME}"
echo "Port: ${PORT}"
echo "Mounting agent: ${SCRIPT_DIR}"
echo "Mounting skills: ${PROJECT_ROOT}/skills"
echo "========================================"

# Stop and remove existing container if it exists
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping and removing existing container..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi

# Run the container with wazy_agent directory mounted
docker run -d \
    --rm \
    --name "${CONTAINER_NAME}" \
    --add-host host.docker.internal:host-gateway \
    -p "${PORT}:10004" \
    --env-file "${SCRIPT_DIR}/.env" \
    -e PORT=10004 \
    -e SDK_LOG_LEVEL=DEBUG \
    -v "${SCRIPT_DIR}:/app/agent" \
    -v "${PROJECT_ROOT}/skills:/app/skills" \
    "${IMAGE_NAME}:${TAG}"

echo ""
echo "========================================"
echo "Container started successfully!"
echo "========================================"
echo ""
echo "Container name: ${CONTAINER_NAME}"
echo "Access the agent at: http://localhost:${PORT}"
echo "Agent directory mounted from: ${SCRIPT_DIR}"
echo "Skills directory mounted from: ${PROJECT_ROOT}/skills"
echo ""
echo "Useful commands:"
echo "  View logs:         docker logs -f ${CONTAINER_NAME}"
echo "  Stop container:    docker stop ${CONTAINER_NAME}"
echo "  Remove container:  docker rm ${CONTAINER_NAME}"
echo "  Execute shell:     docker exec -it ${CONTAINER_NAME} /bin/bash"
echo ""
echo "Viewing recent logs..."
docker logs --tail 50 -f "${CONTAINER_NAME}"
