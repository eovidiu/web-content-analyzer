# Simple Railway-friendly Docker setup
FROM python:3.12-slim

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Start the server (will fall back to HTTP scraping if Playwright fails)
CMD ["uv", "run", "python", "server.py"]
