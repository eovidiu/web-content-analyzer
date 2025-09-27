# Use Python 3.12 with system dependencies for Playwright
FROM python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libgconf-2-4 \
    libxcomposite1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies with uv
RUN uv sync

# Install Playwright browsers
RUN uv run playwright install chromium
RUN uv run playwright install-deps

# Expose port
EXPOSE 8000

# Start command
CMD ["uv", "run", "python", "server.py"]