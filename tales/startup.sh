#!/bin/bash
# Startup script for Azure App Service
# This script starts the Streamlit app

# Start Streamlit server
# Azure App Service sets PORT environment variable
exec streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true

