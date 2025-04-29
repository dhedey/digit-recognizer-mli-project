# Running ubuntu on a cx22 Hetzner server with Docker installed
# Run as root, by running: ssh root@<server-ip>

sudo apt update
sudo apt install -y git

cd ~
git clone https://github.com/dhedey/digit-recognizer-mli-project.git
cd digit-recognizer-mli-project
docker compose up -d

# Install caddy to act as a reverse proxy
# Keeping this out of the docker compose setup makes it a little easier to separate concerns
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
caddy start # It might have already started
caddy reload --config ./deployment/Caddyfile
