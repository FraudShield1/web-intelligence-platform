# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements-full.txt /app/backend/requirements-full.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements-full.txt

# Copy the rest of the application
COPY backend /app/backend
COPY railway.json /app/
COPY Procfile /app/

# Set Python path
ENV PYTHONPATH=/app/backend:$PYTHONPATH

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start command (Railway will use Procfile, but this is fallback)
CMD cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

