#!/bin/bash


# === CONFIGURATION ===
BOTDIR="/opt/discord-bot"
BACKUPDIR="$BOTDIR/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOGFILE="$BOTDIR/logs/update.log"

# Load .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

WEBHOOK_URL="$DISCORD_WEBHOOK_URL"

cd "$BOTDIR" || exit 1

# === Function: Send message to Discord via webhook ===
function discord_log() {
  local MSG="$1"
  curl -H "Content-Type: application/json" \
    -X POST \
    -d "{\"content\": \"$MSG\"}" \
    "$WEBHOOK_URL" >/dev/null 2>&1
}

# === Function: Check for git updates ===
echo "🔍 Checking for updates..." | tee -a "$LOGFILE"
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin main | awk '{print $1}')

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Already up to date. No update necessary. woOp woOp" | tee -a "$LOGFILE"
    exit 0
fi

# === Create backup before updating ===
echo "🗄️ Creating backup..." | tee -a "$LOGFILE"
mkdir -p "$BACKUPDIR"
tar czf "$BACKUPDIR/backup-$TIMESTAMP.tar.gz" \
    requirements.txt docker-compose.yml Dockerfile .env tickets.json logs/

echo "Backup saved: $BACKUPDIR/backup-$TIMESTAMP.tar.gz" | tee -a "$LOGFILE"
discord_log ":floppy_disk: Backup created: \`backup-$TIMESTAMP.tar.gz\`"

# === Perform git pull ===
echo "🔄 Pulling latest Git changes..." | tee -a "$LOGFILE"
git pull | tee -a "$LOGFILE"

# === Stop running container ===
echo "🛑 Stopping running container..." | tee -a "$LOGFILE"
docker-compose down | tee -a "$LOGFILE"

# === Rebuild Docker image ===
echo "🔧 Rebuilding Docker image..." | tee -a "$LOGFILE"
docker-compose build | tee -a "$LOGFILE"

# === Start container ===
echo "🚀 Starting container..." | tee -a "$LOGFILE"
docker-compose up -d | tee -a "$LOGFILE"

MSG=":arrows_counterclockwise: **Bot updated and restarted!**
Git updated from \`$LOCAL\` to \`$REMOTE\`
Backup: \`backup-$TIMESTAMP.tar.gz\`"
discord_log "$MSG"

echo "✅ Bot updated and restarted successfully." | tee -a "$LOGFILE"
