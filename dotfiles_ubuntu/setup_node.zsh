#!/usr/bin/env zsh

echo "Starting Node setup"

if exists node; then
  echo "node $(node --version) and npm $(npm --version) already installed, skipping installation..."
else
  echo "Installing node and npm with n..."
  n latest
fi
