#!/bin/bash
# Startup script for Azure App Service
# This script ensures the stories directory exists and starts the server

# Create stories directory if it doesn't exist
mkdir -p stories

# Start uvicorn server
# Azure App Service sets PORT environment variable
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

