# Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will provide PORT env var)
EXPOSE 8000

# Health check (using shell form to expand env vars)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$(echo ${PORT:-8000})/health || exit 1

# Run the application (using shell form to expand PORT env var)
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"