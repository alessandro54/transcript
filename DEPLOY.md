# Deployment Guide

## Deploy to VM

### 1. Provision a VPS

Recommended providers:

- Hetzner - 4 EUR/month (CX22)
- DigitalOcean - 6 USD/month (Basic Droplet)
- Vultr - 6 USD/month

Minimum specs: 1 vCPU, 2GB RAM, 20GB SSD

### 2. Initial Server Setup

```bash
# SSH into your server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create bot user
useradd -m -s /bin/bash botuser
usermod -aG docker botuser

# Switch to bot user
su - botuser
```

### 3. Deploy the Bot

```bash
# Clone repository
git clone <repository-url> transcript-bot
cd transcript-bot

# Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
ENVIRONMENT=production
EOF

# Start the bot
docker compose --profile prod up -d

# Check logs
docker compose --profile prod logs -f
```

### 4. Setup Auto-Restart (systemd)

```bash
# Create systemd service
sudo tee /etc/systemd/system/transcript-bot.service << EOF
[Unit]
Description=Transcript Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=botuser
WorkingDirectory=/home/botuser/transcript-bot
ExecStart=/usr/bin/docker compose --profile prod up -d
ExecStop=/usr/bin/docker compose --profile prod down

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable transcript-bot
sudo systemctl start transcript-bot
```

### 5. Updates

```bash
cd ~/transcript-bot
git pull
docker compose --profile prod build --no-cache
docker compose --profile prod up -d
```

## Docker Commands

```bash
# Start
docker compose --profile prod up -d

# Stop
docker compose --profile prod down

# Logs
docker compose --profile prod logs -f

# Rebuild
docker compose --profile prod build --no-cache

# Restart
docker compose --profile prod restart
```

## Troubleshooting

**Bot doesn't respond**
- Check `TELEGRAM_BOT_TOKEN` in `.env`

**Transcription fails**
- Check logs: `docker compose --profile prod logs`

**Out of memory**
- Use production mode (OpenAI API) instead of local

**Permission denied**
- Run `sudo usermod -aG docker $USER` and re-login
