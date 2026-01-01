# Dockerfile for FastAPI Backend
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create stories directory
RUN mkdir -p stories

# Expose port (Azure App Service uses PORT env var, but we'll default to 8000)
EXPOSE 8000

# Use uvicorn to run the app
# Azure App Service will set PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

