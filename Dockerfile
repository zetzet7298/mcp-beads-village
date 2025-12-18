FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (git is required for beads)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy project definition
COPY pyproject.toml README.md ./
COPY beads_village/ ./beads_village/

# Install beads CLI (required dependency)
RUN pip install beads

# Install beads-village with HTTP support
RUN pip install --no-cache-dir ".[http]"

# Expose HTTP port
EXPOSE 8080

# Run the HTTP server
# Host 0.0.0.0 is crucial for Docker networking
CMD ["beads-village-http", "--host", "0.0.0.0", "--port", "8080"]
