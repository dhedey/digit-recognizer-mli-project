# Running ubuntu on a cx22 Hetzner server with Docker installed
# Run as root, by running: ssh root@<server-ip>

sudo apt update
sudo apt install -y git

cd ~
git clone https://github.com/dhedey/digit-recognizer-mli-project.git
cd digit-recognizer-mli-project
docker compose up -d

# Install caddy to act as a reverse proxy
# Whilst we could use a docker image (https://www.docker.com/blog/deploying-web-applications-quicker-and-easier-with-caddy-2/)
# It's a slightly nicer separation of concerns to keep this out of the docker compose setup, so we can use the same between dev and prod
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# And start/reload Caddy
cp ./deployment/Caddyfile /etc/caddy/Caddyfile
caddy start
caddy reload
