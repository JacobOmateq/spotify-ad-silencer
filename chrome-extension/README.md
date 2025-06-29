# 🎵 Spotify Ad Silencer - Chrome Extension

A powerful Chrome extension that automatically detects and silences Spotify ads, playing your own music instead!

## ✨ Features

- **🔇 Automatic Ad Muting**: Instantly mutes Spotify tabs when ads are detected
- **🎵 Music Playback**: Plays random music from your collection during ads
- **🌍 Multi-language Support**: Detects ads in 15+ languages
- **📊 Statistics Tracking**: Monitor ads blocked and session time
- **🔔 Desktop Notifications**: Get notified when ads are blocked
- **⚡ Zero Configuration**: Works immediately after installation

## 🚀 Installation

### Method 1: Install from Chrome Web Store (Coming Soon)
*Extension will be available on the Chrome Web Store soon*

### Method 2: Install as Developer Extension

1. **Download the Extension**
   ```bash
   git clone https://github.com/JacobOmateq/spotify-ad-silencer.git
   cd spotify-ad-silencer/chrome-extension
   ```

2. **Open Chrome Extensions**
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)

3. **Load the Extension**
   - Click "Load unpacked"
   - Select the `chrome-extension` folder
   - The extension will appear in your extensions list

4. **Pin the Extension**
   - Click the puzzle piece icon in Chrome toolbar
   - Find "Spotify Ad Silencer" and click the pin icon
   - The extension icon will now appear in your toolbar

## 🎯 How to Use

### Quick Start
1. **Open Spotify** in a Chrome tab (`open.spotify.com`)
2. **Click the extension icon** in your toolbar
3. **Click "Start Monitoring"** in the popup
4. **Play music** on Spotify - ads will be automatically blocked!

### What Happens When an Ad Plays
1. 🔍 **Detection**: Extension detects ad title patterns
2. 🔇 **Muting**: Spotify tab is instantly muted
3. 🎵 **Music**: Random music plays from the extension
4. 📱 **Notification**: Desktop notification shows ad was blocked
5. ✅ **Resume**: When ad ends, Spotify is unmuted automatically

## 🎵 Music Files

The extension comes with ambient music files that play during ads. You can customize this by:

1. **Adding Your Music**:
   - Place MP3 files in `chrome-extension/audio/music/`
   - Update the file list in `content.js`
   - Reload the extension

2. **Supported Formats**: MP3, WAV, OGG

## 🌍 Supported Languages

The extension detects ads in these languages:
- 🇺🇸 English
- 🇪🇸 Spanish  
- 🇫🇷 French
- 🇩🇪 German
- 🇵🇹 Portuguese
- 🇮🇹 Italian
- 🇳🇱 Dutch
- 🇸🇪 Swedish
- 🇳🇴 Norwegian
- 🇩🇰 Danish
- 🇫🇮 Finnish
- 🇵🇱 Polish
- 🇷🇺 Russian
- 🇯🇵 Japanese
- 🇰🇷 Korean
- 🇨🇳 Chinese

## 📊 Features Overview

| Feature | Chrome Extension | Web App | Desktop App |
|---------|------------------|---------|-------------|
| Ad Detection | ✅ Perfect | ✅ Perfect | ✅ Perfect |
| Auto Mute/Unmute | ✅ Full Control | ⚠️ Limited | ✅ Full Control |
| Music Playback | ✅ Built-in | ✅ Built-in | ✅ Built-in |
| Cross-platform | ✅ Chrome Only | ✅ Any Browser | ✅ Win/Mac/Linux |
| Installation | ✅ One-click | ✅ No install | ✅ Download |
| Permissions | ✅ Tab control | ⚠️ Limited | ✅ System access |

## 🔧 Permissions Explained

The extension requests these permissions:

- **`tabs`**: To find and control Spotify tabs
- **`activeTab`**: To monitor current tab titles
- **`storage`**: To save your preferences and statistics
- **`notifications`**: To show desktop notifications
- **`*://*.spotify.com/*`**: To access Spotify web player

## 🛠️ Development

### Project Structure
```
chrome-extension/
├── manifest.json       # Extension configuration
├── background.js       # Background service worker
├── content.js          # Content script for Spotify pages
├── popup.html          # Extension popup interface
├── popup.css           # Popup styling
├── popup.js            # Popup functionality
├── audio/              # Music files
│   └── music/          # Music played during ads
└── icons/              # Extension icons
```

### Building from Source
```bash
# Clone repository
git clone https://github.com/JacobOmateq/spotify-ad-silencer.git
cd spotify-ad-silencer/chrome-extension

# Load in Chrome
# 1. Go to chrome://extensions/
# 2. Enable Developer mode
# 3. Click "Load unpacked"
# 4. Select this folder
```

## 🐛 Troubleshooting

### Extension Not Working?
1. **Check Permissions**: Make sure you granted all permissions
2. **Reload Extension**: Go to `chrome://extensions/` and click reload
3. **Restart Chrome**: Sometimes a restart helps
4. **Check Console**: Open DevTools and check for errors

### No Music Playing?
1. **Audio Files**: Ensure music files are in `audio/music/` folder
2. **File Format**: Use MP3, WAV, or OGG files
3. **Browser Audio**: Check Chrome's audio settings

### Ads Not Detected?
1. **Language Support**: Check if your language is supported
2. **Update Extension**: Make sure you have the latest version
3. **Report Issue**: Create an issue on GitHub with the ad title

## 📝 Privacy & Security

- **🔒 No Data Collection**: Extension doesn't collect or send any data
- **🏠 Local Processing**: All ad detection happens locally
- **🔐 Secure**: Only accesses Spotify tabs, nothing else
- **🌐 Open Source**: Full source code available for review

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/JacobOmateq/spotify-ad-silencer/issues)
- **Discussions**: [Join the community](https://github.com/JacobOmateq/spotify-ad-silencer/discussions)

## 🎉 Acknowledgments

- Thanks to all contributors and users
- Inspired by the need for ad-free music experience
- Built with ❤️ for the community

---

**Enjoy ad-free Spotify! 🎵** 