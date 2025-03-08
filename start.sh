#!/bin/bash
# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

# Wait for Xvfb to start
sleep 2

# Set display
export DISPLAY=:99

# Run the Python script
python mapping.py