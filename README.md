# GitHub Discord Sync Bot

A Discord bot that automatically forwards new threads from specific Discord Forum channels to GitHub as either Issues or Discussions.

## Features
- **Forum to Issue**: Automatically creates a GitHub Issue when a new thread is created in the designated "Bugs/Issues" forum channel.
- **Forum to Discussion**: Automatically creates a GitHub Discussion when a new thread is created in the designated "Suggestions" forum channel.
- Fully asynchronous and Docker/Podman ready.

## Prerequisites

1. **Discord Bot Token**: Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
   - Ensure you enable the **Message Content Intent** and **Server Members Intent** in the "Bot" tab.
   - Give the bot `View Channels`, `Read Message History`, and `Send Messages` permissions (or simply `Administrator`).
2. **GitHub Personal Access Token (PAT)**: Requires a Classic PAT with `repo` and `discussion` scopes, or a Fine-Grained token with equivalent permissions.
3. **Python 3.11+** (If running locally without Docker)

## Configuration

Rename or create a `.env` file in the root directory with the following variables:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_REPO_OWNER=your_github_username_or_organization
GITHUB_REPO_NAME=your_repository_name

# Discord Channel IDs
FORUM_CHANNEL_ID=123456789012345678
DISCUSSION_CHANNEL_ID=987654321098765432
```

---

## Running 24/7 using Docker / Podman (Recommended)

To ensure the bot runs 24/7 without manual intervention, it is highly recommended to run it inside a container using the provided `docker-compose.yml`. 

The `docker-compose.yml` is configured with `restart: unless-stopped`, which means the container will automatically restart if it crashes, and it will start automatically when the server boots.

### 1. Start the container
Run the following command in the background (detached mode):

```bash
# If using Podman (Default for this project):
podman-compose up -d --build

# If using Docker:
docker-compose up -d --build
```

### 2. Ensure 24/7 uptime across server reboots (Rootless Podman only)
If you are running **Docker**, the Docker daemon automatically starts containers on boot. You don't need to do anything else.

If you are running **Rootless Podman** (running Podman as a regular user), containers do not start automatically when the server reboots unless the user is logged in. To fix this and allow the bot to run 24/7 in the background without being logged in, enable "lingering" for your Linux user:

```bash
# Enable lingering for your current user
loginctl enable-linger $USER
```

### 3. View Logs
To check if the bot is running properly:
```bash
podman logs -f github-discord-bot
# or
docker logs -f github-discord-bot
```

---

## Running Locally (Development)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python githubBOT.py
   ```
