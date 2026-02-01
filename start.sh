#!/bin/bash

# UKPSC Bot Startup Script for Render.com
# This script runs the bot in a continuous loop

echo "🤖 Starting UKPSC Notification Bot..."
echo "Will check every 3 hours (10800 seconds)"
echo "=========================================="

while true; do
    echo ""
    echo "Starting new check cycle..."
    python ukpsc_bot_render.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Check completed successfully"
    else
        echo "✗ Check failed with error code $?"
    fi
    
    echo "⏸️  Waiting 3 hours before next check..."
    echo "=========================================="
    sleep 10800  # 3 hours = 10800 seconds
    
    # Change this value to adjust check frequency:
    # 1 hour  = 3600
    # 2 hours = 7200
    # 3 hours = 10800
    # 6 hours = 21600
done
