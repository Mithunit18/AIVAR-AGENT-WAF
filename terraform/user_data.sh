#!/bin/bash
set -euo pipefail

# Log all output to a log file and to the console
exec > >(tee -a /var/log/aivar-agent-waf-bootstrap.log) 2>&1

echo "Starting AIVAR Agent WAF bootstrap..."

# Update and install dependencies
apt-get update -y
apt-get install -y ca-certificates curl gnupg git

# Install Docker safely using valid Bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Verify Docker installation
if ! docker --version; then
    echo "ERROR: Docker installation failed."
    exit 1
fi

if ! docker compose version; then
    echo "ERROR: Docker Compose installation failed."
    exit 1
fi

# Prepare application directory
APP_DIR="/opt/aivar-agent-waf"
mkdir -p "$${APP_DIR}"
chown ubuntu:ubuntu "$${APP_DIR}"

# Clone repository safely
REPO_URL="${repository_url}"

if [ -z "$${REPO_URL}" ]; then
    echo "No repository URL provided. Skipping application clone and start."
    echo "Bootstrap completed successfully."
    exit 0
fi

if [ ! -d "$${APP_DIR}/.git" ]; then
    echo "Cloning repository..."
    # Clone directly; if directory exists and is empty, git clone succeeds
    git clone "$${REPO_URL}" "$${APP_DIR}"
else
    echo "Git repository already exists in $${APP_DIR}, skipping clone."
fi

chown -R ubuntu:ubuntu "$${APP_DIR}"
cd "$${APP_DIR}"

# Verify production compose configuration exists
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "ERROR: docker-compose.prod.yml does not exist."
    exit 1
fi

# Safely setup .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Copying .env.example to .env..."
        cp .env.example .env
    else
        echo "Creating placeholder .env..."
        echo "GEMINI_API_KEY=placeholder" > .env
    fi
    chown ubuntu:ubuntu .env
    echo "IMPORTANT: Gemini API key must be configured before running the LangGraph agent."
else
    echo ".env file already exists, skipping creation/copy."
fi

# Verify production compose configuration
if ! docker compose -f docker-compose.prod.yml config -q; then
    echo "ERROR: docker-compose.prod.yml configuration is invalid."
    exit 1
fi

# Start application
echo "Starting application stack..."
docker compose -f docker-compose.prod.yml up -d --build

# Verify services
docker compose -f docker-compose.prod.yml ps

echo "Waiting for health and readiness endpoints..."
MAX_RETRIES=24 # 2 minutes at 5s intervals
RETRY_COUNT=0
HEALTH_OK=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl --fail --silent http://localhost/health > /dev/null && curl --fail --silent http://localhost/ready > /dev/null; then
        HEALTH_OK=true
        break
    fi
    echo "Endpoints not ready yet. Retrying in 5 seconds... ($$((RETRY_COUNT+1))/$${MAX_RETRIES})"
    sleep 5
    RETRY_COUNT=$$((RETRY_COUNT+1))
done

if [ "$${HEALTH_OK}" = true ]; then
    echo "Application health and readiness verified successfully!"
else
    echo "ERROR: Health/readiness checks failed after $${MAX_RETRIES} attempts."
    exit 1
fi

echo "Bootstrap completed successfully."
exit 0
