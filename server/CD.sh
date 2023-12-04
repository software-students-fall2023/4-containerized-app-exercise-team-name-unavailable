# Stops, updates, and restarts docker compose.
# This script is triggered by the CD pipeline.

curl https://github.com/software-students-fall2023/4-containerized-app-exercise-team-name-unavailable/blob/main/compose.yaml compose.yaml
docker compose down
docker compose pull
docker compose --env-file="certs/.env" up -d