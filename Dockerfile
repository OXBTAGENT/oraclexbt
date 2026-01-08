FROM python:3.11-slim

LABEL maintainer="OracleXBT"
LABEL description="AI-powered prediction market trading platform"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-production.txt .
RUN pip install --no-cache-dir -r requirements-production.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data website

# Expose port
EXPOSE 7777

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7777/api/health')"

# Run with gunicorn
CMD ["gunicorn", "--config", "gunicorn_config.py", "bin.api_server:app"]
