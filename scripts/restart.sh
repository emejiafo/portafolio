#!/bin/bash
# Clean restart script for docker-compose

set -e

echo "Stopping all containers..."
docker-compose down --remove-orphans 2>/dev/null || true

echo "Killing any processes on required ports..."
for port in 5432 8000 7860 80; do
    pid=$(sudo lsof -ti:$port 2>/dev/null) || true
    if [ -n "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        sudo kill -9 $pid 2>/dev/null || true
    fi
done

sleep 1

echo "Starting containers..."
docker-compose up -d

echo "Following backend logs..."
docker-compose logs -f backend