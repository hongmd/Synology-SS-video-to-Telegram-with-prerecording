#!/bin/bash

# Log viewer script for Synology Surveillance Station Video to Telegram

CONTAINER_NAME="VideoSsToTg"
LINES="${1:-50}"

if [ "$1" == "follow" ] || [ "$1" == "-f" ]; then
    echo "Following logs (press Ctrl+C to stop)..."
    docker-compose logs -f $CONTAINER_NAME
else
    echo "Showing last $LINES lines of logs:"
    echo ""
    docker-compose logs --tail=$LINES $CONTAINER_NAME
fi
