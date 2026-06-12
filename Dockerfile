FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY backend/ ./app/

# Expose port
EXPOSE 8000

# Run with uvicorn (use Railway's PORT env var, default to 8000)
CMD python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}