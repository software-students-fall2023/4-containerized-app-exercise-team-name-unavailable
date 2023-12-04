# Audio Transcription Project

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/software-students-fall2023/4-containerized-app-exercise-team-name-unavailable/actions/workflows/ci-cd.yml)
[![Test Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/software-students-fall2023/4-containerized-app-exercise-team-name-unavailable/actions/workflows/ci-cd.yml)

## Description

[This Project](https://unavailable.duckdns.org) allows users to make a recording and then view this recording and all previous recordings they have made as text.

## Team Members

- [Michael Lin](https://github.com/freerainboxbox)
- [Ethan Delgado](https://github.com/ethan-delgado)
- [Seolin Jung](https://github.com/seolinjung)
- [Erick Cho](https://github.com/ec3566)

## Getting Started

To successfully run this project, you'll need to follow these steps:

### Prerequisites

Before you begin, ensure you have the following:

1. **Domain Name and SSL Certificate**: Store these in a directory named `certs`. You can obtain a domain name and a free SSL certificate through services like [Let's Encrypt](https://letsencrypt.org/) and [DuckDNS](https://www.duckdns.org/).
2. **Environment File**: Create a `.env` file with your MongoDB credentials, specifying `MONGO_USERNAME` and `MONGO_PASSWORD`.
3. **Compose File**: Ensure you have the `compose.yaml` file ready for Docker.
4. **Data Directory**: Create an empty directory named `mongodb-data` to hold MongoDB data.

### Starting the Project

To start the project, follow these steps:

1. **Open Firewall**: Open up the firewall for TCP traffic on port 443.
2. **Docker Compose**: Run the following command:
   ```bash
   docker compose --env-file "certs/.env" up -d
   
### Stopping the Project

To stop the project, execute the following command:

```bash
docker compose down

