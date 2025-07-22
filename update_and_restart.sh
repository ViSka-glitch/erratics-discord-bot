#!/bin/bash

cd /home/botuser/discord-bot || exit

echo "🔄 Pulling latest Git changes..."
git pull

echo "🚀 Restarting bot via systemd..."
sudo /bin/systemctl restart discord-bot.service

echo "✅ Bot restarted successfully."
