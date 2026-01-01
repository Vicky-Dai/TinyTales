# Dockerfile for Streamlit Frontend
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Install Streamlit and requests
RUN pip install --no-cache-dir streamlit requests

# Copy application code
COPY . .

# Expose port (Streamlit default is 8501, but Azure uses PORT env var)
EXPOSE 8501

# Run Streamlit
# Azure App Service will set PORT environment variable
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true

