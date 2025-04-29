# Running ubuntu on a cx22 Hetzner server with Docker installed
# Run as root, by running: ssh root@<server-ip>
cd ~/digit-recognizer-mli-project
git pull
caddy reload --config ./deployment/Caddyfile
docker compose up -d --build