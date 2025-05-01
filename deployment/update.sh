# Running ubuntu on a cx22 Hetzner server with Docker installed
# Run as root, by running: ssh root@<server-ip>
cd ~/digit-recognizer-mli-project
git pull
cp ./deployment/Caddyfile /etc/caddy/Caddyfile
caddy reload
docker compose up -d --build