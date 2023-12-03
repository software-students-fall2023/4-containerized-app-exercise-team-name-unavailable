# Stops, updates, and restarts docker compose.
# This script is triggered by the CD pipeline.
docker compose down
docker compose pull
docker compose up -d