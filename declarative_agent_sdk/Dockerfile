# Generic Dockerfile for Declarative Agent SDK Agents
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install declarative-agent-sdk from GitHub
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir git+https://github.com/mngaonkar/google-adk-samples.git#subdirectory=declarative_agent_sdk

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Skills directory will be mounted at runtime
# Agent directory will be mounted at runtime

# Set Python path
ENV PYTHONPATH=/app:${PYTHONPATH}

# Create workspace directory
RUN mkdir -p /app/agent/workspace

# Expose the agent server port (default, can be overridden)
EXPOSE 10004

# Set default environment variables (can be overridden at runtime)
ENV PORT=10004
ENV WORKSPACE_DIRECTORY=/app/agent/workspace

# Set working directory for agent (will be mounted at runtime)
WORKDIR /app/agent

# Default command (can be overridden at runtime)
CMD ["python", "agent.py"]
