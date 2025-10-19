#!/bin/bash

# Fix apt repository issues for Linux Mint
# Run this before setup-native.sh if you have repo errors

echo "🔧 Fixing apt repositories..."

# Backup current sources
sudo cp /etc/apt/sources.list.d/docker.list /etc/apt/sources.list.d/docker.list.bak 2>/dev/null || true

# Fix Docker repo (change xia to noble)
if [ -f /etc/apt/sources.list.d/docker.list ]; then
    echo "Fixing Docker repository..."
    sudo sed -i 's/xia/noble/g' /etc/apt/sources.list.d/docker.list
fi

# Fix Microsoft Code repo key
echo "Fixing Microsoft Code GPG key..."
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null
if [ -f /etc/apt/sources.list.d/vscode.list ]; then
    sudo sed -i 's|deb \[arch=amd64,arm64,armhf\] https://packages.microsoft.com/repos/code|deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code|g' /etc/apt/sources.list.d/vscode.list
fi

# Fix Cursor repo key
echo "Fixing Cursor GPG key..."
wget -qO- https://downloads.cursor.com/linux/debian/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/cursor-archive-keyring.gpg > /dev/null 2>&1 || true

echo "✅ Repositories fixed! Now run: sudo apt update"
