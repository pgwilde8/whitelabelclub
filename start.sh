#!/bin/bash

# ClubLaunch Startup Script
# This script ensures the virtual environment is activated and starts the application

# Set working directory
cd /home/adminuser/mymain

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=/home/adminuser/mymain
export ENVIRONMENT=production

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
