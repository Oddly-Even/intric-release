# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

#!/bin/bash
set -euf -o pipefail

# Install system dependencies
sudo apt-get update
sudo apt-get install -y libmagic1 ffmpeg

# Install Python dependencies
pip install --no-cache-dir poetry

cd /workspace/backend

poetry install

# Install Node.js dependencies
cd /workspace/frontend

npm install -g pnpm@8.9.0
# Set pnpm store directory
pnpm config set store-dir $HOME/.pnpm-store
pnpm run setup

# Ensure .env files are present
env_file_errors=()
env_files=("backend/.env" "frontend/apps/web/.env")
for file in "${env_files[@]}"; do
    if [ ! -f "/workspace/$file" ]; then
        env_file_errors+=("Error: .env file not found in $file folder. Please create one.")
    fi
done
echo "Environment variables ------------------------------"
if [ ${#env_file_errors[@]} -ne 0 ]; then
    for message in "${env_file_errors[@]}"; do
        echo "$message"
    done
else
    echo "All .env files found!"
fi

# Show instructions on how to run the project
echo ""
echo "To run the project, use the following commands"
echo ""
echo "Backend --------------------------------------------"
echo "$ cd /workspace/backend"
echo ""
echo "If this is your first run, execute migrations:"
echo "$ poetry run python init_db.py"
echo ""
echo "Start the backend:"
echo "$ poetry run start"
echo ""
echo "Frontend --------------------------------------------"
echo "$ cd /workspace/frontend"
echo "$ pnpm run dev"
echo ""
echo "Open your browser and go to http://localhost:3000"
echo "Login with"
echo "email: user@example.com"
echo "password: Password1!"
echo ""
echo "You can now start developing!"
echo ""
