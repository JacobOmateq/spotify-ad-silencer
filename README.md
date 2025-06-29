# Cross-Platform Spotify Ad Silencer

A universal Spotify ad silencer that works on **Windows**, **macOS**, and **Linux**! 🎵

## Features

- 🖥️ **Cross-platform support** - Windows, macOS, Linux
- 🔇 **Smart audio control** - Platform-specific audio muting
- 🎯 **Accurate ad detection** - Window title analysis
- 🔄 **Automatic recovery** - Restores audio when music resumes
- 📊 **Detailed logging** - Track what's happening

## How It Works

### Detection Method
- **Ads**: Window title shows "Spotify Free", "Spotify Premium", or "Advertisement"
- **Music**: Window title shows actual song/artist names (e.g., "The Beatles - Hey Jude")

### Audio Control
- **Windows**: Uses Windows Audio API (`pycaw`)
- **macOS**: Uses AppleScript to control system volume
- **Linux**: Uses PulseAudio (`pulsectl`)

## Installation & Setup

### Quick Install (macOS) 🍺

**Homebrew (Recommended for macOS users):**
```bash
# Add the tap
brew tap JacobOmateq/spotify-ad-silencer

# Install
brew install spotify-ad-silencer

# Run
spotify-ad-silencer
```

### Manual Installation

#### 1. Install Python Dependencies

**All Platforms:**
```bash
pip install -r requirements.txt
```

**Linux Additional Setup:**
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt update
sudo apt install pulseaudio pulseaudio-utils wmctrl xdotool

# Fedora/RHEL:
sudo dnf install pulseaudio pulseaudio-utils wmctrl xdotool
```

#### 2. Platform-Specific Setup

#### Windows
- ✅ **Ready to go!** - All dependencies install automatically
- Requires Windows 7+ with Windows Audio Session API

#### macOS
- ✅ **Ready to go!** - Uses built-in AppleScript
- Requires macOS 10.9+ 
- **Note**: You may need to grant Terminal/Python accessibility permissions:
  - System Preferences → Security & Privacy → Privacy → Accessibility
  - Add Terminal or your Python interpreter

#### Linux
- Requires **PulseAudio** (default on most distributions)
- Requires **wmctrl** or **xdotool** for window detection
- Works on **X11** and **Wayland** (with some limitations on Wayland)

## Usage

### Run the Application
```bash
python main.py
```

### Expected Output
```
2024-01-01 12:00:00,000 - INFO - Detected OS: windows
2024-01-01 12:00:00,001 - INFO - Windows audio control initialized
2024-01-01 12:00:00,002 - INFO - Starting Cross-Platform Spotify Ad Silencer on windows
2024-01-01 12:00:01,000 - INFO - Current Spotify window title: The Beatles - Hey Jude
2024-01-01 12:00:02,000 - INFO - Current Spotify window title: Spotify Free
2024-01-01 12:00:02,001 - INFO - Advertisement detected. Muting system audio.
2024-01-01 12:00:35,000 - INFO - Current Spotify window title: Queen - Bohemian Rhapsody  
2024-01-01 12:00:35,001 - INFO - Music playing. Unmuting system audio.
```

## Troubleshooting

### Windows Issues

**Audio control not working:**
```bash
# Check if Windows Audio Service is running
sc query AudioSrv

# Restart if needed
sc stop AudioSrv
sc start AudioSrv
```

**Window detection not working:**
```bash
# Check if Spotify is running
tasklist | findstr Spotify
```

### macOS Issues

**Permission denied errors:**
```bash
# Grant accessibility permissions to Terminal
# System Preferences → Security & Privacy → Privacy → Accessibility
# Add Terminal and/or Python
```

**AppleScript errors:**
```bash
# Test AppleScript manually
osascript -e "get volume settings"
osascript -e "set volume output volume 50"
```

### Linux Issues

**Audio control not working:**
```bash
# Check PulseAudio status
pulseaudio --check -v

# Restart PulseAudio if needed
pulseaudio -k
pulseaudio --start

# Test audio control
pactl info
pactl list sinks short
```

**Window detection not working:**
```bash
# Check if required tools are installed
which wmctrl
which xdotool

# Test window detection
wmctrl -l | grep -i spotify
xdotool search --name "Spotify"
```

**Wayland compatibility:**
```bash
# On Wayland, try switching to X11 session
# Or install additional Wayland tools
sudo apt install wlr-randr  # For wlroots-based compositors
```

## Platform Comparison

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Audio Control | ✅ Native API | ✅ AppleScript | ✅ PulseAudio |
| Window Detection | ✅ Win32 API | ✅ AppleScript | ✅ wmctrl/xdotool |
| Process Detection | ✅ | ✅ | ✅ |
| Auto-start Support | ✅ | ✅ | ✅ |

## Advanced Configuration

### Running as a Service

**Windows (Task Scheduler):**
```cmd
# Create a scheduled task to run at startup
schtasks /create /tn "SpotifyAdSilencer" /tr "python C:\path\to\main.py" /sc onstart
```

**macOS (launchd):**
```bash
# Create ~/Library/LaunchAgents/com.spotify.adsilencer.plist
# See documentation for launchd plist format
```

**Linux (systemd):**
```bash
# Create ~/.config/systemd/user/spotify-ad-silencer.service
# Enable with: systemctl --user enable spotify-ad-silencer.service
```

### Logging Configuration

Modify logging level in the script:
```python
# For debug output
logging.basicConfig(level=logging.DEBUG, ...)

# For minimal output  
logging.basicConfig(level=logging.WARNING, ...)
```

## Known Limitations

### General
- Requires Spotify desktop app (doesn't work with web player)
- May have a brief delay when switching between ads and music
- Window title detection depends on Spotify's title format

### Platform-Specific

**Windows:**
- Requires Windows Audio Session API (Windows 7+)
- May conflict with other audio management software

**macOS:**
- Requires accessibility permissions for window detection
- Volume control affects system-wide volume (not just Spotify)

**Linux:**
- Wayland support limited compared to X11
- Requires PulseAudio (doesn't work with ALSA-only setups)
- Some desktop environments may block window title access

## Contributing

Feel free to:
- Report bugs for your specific OS/distribution
- Add support for additional audio systems
- Improve window detection algorithms
- Add new features

## Original Version

If you prefer the Windows-only version with the original approach:
```bash
python main.py  # Original Windows version
```

## License

This project is open source. Use responsibly and respect Spotify's terms of service. 