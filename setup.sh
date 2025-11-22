#!/bin/bash

# Spotify Music Downloader - Quick Setup Script
# This script helps you set up the downloader with FLAC support

echo "============================================"
echo "Spotify Music Downloader - Setup"
echo "============================================"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check FFmpeg
echo "Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found."
    echo "   Install FFmpeg for audio processing:"
    echo "   - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Arch Linux: sudo pacman -S ffmpeg"
    read -p "Continue without FFmpeg? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ FFmpeg found: $(ffmpeg -version | head -n 1)"
fi
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Configuration
echo "============================================"
echo "Configuration Setup"
echo "============================================"
echo ""

# Check if config exists
if [ ! -f "config/config.yaml" ]; then
    echo "Creating default configuration..."
    mkdir -p config
    python3 main.py --help > /dev/null 2>&1  # This will create default config
    echo "✓ Configuration file created"
fi

echo "To download FLAC files from Deezer, you need:"
echo "1. A Deezer account (free or premium)"
echo "2. Your Deezer ARL token"
echo ""
echo "Do you want to set up Deezer for FLAC downloads now?"
read -p "(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Follow these steps to get your ARL token:"
    echo "1. Go to https://www.deezer.com and log in"
    echo "2. Press F12 to open Developer Tools"
    echo "3. Go to Application → Cookies → https://www.deezer.com"
    echo "4. Find the 'arl' cookie and copy its value"
    echo ""
    read -p "Enter your Deezer ARL token: " arl_token
    
    if [ ! -z "$arl_token" ]; then
        # Update config file
        sed -i "s/arl_token: \"\"/arl_token: \"$arl_token\"/" config/config.yaml
        sed -i "s/enabled: false/enabled: true/" config/config.yaml
        echo "✓ Deezer configuration saved"
    fi
fi

echo ""
echo "Do you have Spotify API credentials?"
read -p "(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Enter your Spotify credentials:"
    read -p "Client ID: " spotify_id
    read -p "Client Secret: " spotify_secret
    
    if [ ! -z "$spotify_id" ] && [ ! -z "$spotify_secret" ]; then
        sed -i "s/client_id: \"YOUR_SPOTIFY_CLIENT_ID\"/client_id: \"$spotify_id\"/" config/config.yaml
        sed -i "s/client_secret: \"YOUR_SPOTIFY_CLIENT_SECRET\"/client_secret: \"$spotify_secret\"/" config/config.yaml
        echo "✓ Spotify credentials saved"
    fi
else
    echo ""
    echo "To get Spotify API credentials:"
    echo "1. Go to https://developer.spotify.com/dashboard"
    echo "2. Create a new app"
    echo "3. Copy your Client ID and Client Secret"
    echo "4. Update config/config.yaml with your credentials"
fi

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Review and update config/config.yaml"
echo "2. For FLAC downloads, see FLAC_SETUP_GUIDE.md"
echo "3. Run: python main.py --help for usage"
echo ""
echo "Example commands:"
echo "  python main.py --playlist <url> --format flac"
echo "  python main.py --album <url> --format mp3 --quality 320"
echo "  python main.py --track <url>"
echo ""
echo "Enjoy! 🎵"
