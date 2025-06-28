#!/usr/bin/env python3
"""Build script for creating distributable packages"""

import os
import sys
import subprocess
import shutil
import platform
import zipfile
from pathlib import Path

class PackageBuilder:
    def __init__(self):
        self.current_os = platform.system().lower()
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def clean_build_dirs(self):
        """Clean previous build artifacts"""
        print("Cleaning build directories...")
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.dist_dir.mkdir(exist_ok=True)
        
    def build_executable(self):
        """Build standalone executable with donation integration"""
        print(f"Building executable for {self.current_os}...")
        
        # Platform-specific executable name
        if self.current_os == "windows":
            exe_name = "SpotifyAdSilencer.exe"
        else:
            exe_name = "SpotifyAdSilencer"
        
        cmd = [
            "python", "-m", "PyInstaller", 
            "--onefile",
            "--name", "SpotifyAdSilencer",
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.build_dir),
            "--specpath", str(self.build_dir),
            # Windows-specific options
        ]
        
        # Add data files if they exist
        audio_path = self.project_root / "audio"
        readme_path = self.project_root / "README.md"
        
        if audio_path.exists() and any(audio_path.iterdir()):
            cmd.extend(["--add-data", f"{audio_path}{os.pathsep}audio"])
        
        if readme_path.exists():
            cmd.extend(["--add-data", f"{readme_path}{os.pathsep}."])
        
        if self.current_os == "windows":
            cmd.extend([
                "--console",  # Keep console for now, can be changed to --windowed later
            ])
            # Only add icon if it exists
            icon_path = self.project_root / "icon.ico"
            if icon_path.exists():
                cmd.extend(["--icon", str(icon_path)])
        
        cmd.append("main.py")
        
        try:
            result = subprocess.run(cmd, check=True)
            print(f"Executable built successfully: {exe_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            return False
    
    def create_portable_package(self):
        """Create a portable package with all necessary files"""
        print("Creating portable package...")
        
        package_name = f"SpotifyAdSilencer-{self.current_os}-portable"
        package_dir = self.dist_dir / package_name
        
        # Create package directory
        package_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_name = "SpotifyAdSilencer.exe" if self.current_os == "windows" else "SpotifyAdSilencer"
        exe_path = self.dist_dir / exe_name
        
        if exe_path.exists():
            shutil.copy2(exe_path, package_dir / exe_name)
        
        # Copy essential files
        files_to_copy = [
            "README.md",
            "requirements.txt",
            "audio"
        ]
        
        for file_item in files_to_copy:
            src = self.project_root / file_item
            dst = package_dir / file_item
            
            if src.exists():
                if src.is_file():
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Create installation instructions
        self.create_installation_guide(package_dir)
        
        # Create donation info
        self.create_donation_info(package_dir)
        
        # Create startup scripts
        self.create_startup_scripts(package_dir)
        
        # Create ZIP archive
        zip_path = self.dist_dir / f"{package_name}.zip"
        self.create_zip_archive(package_dir, zip_path)
        
        print(f"Portable package created: {zip_path}")
        return zip_path
    
    def create_installation_guide(self, package_dir):
        """Create platform-specific installation guide"""
        if self.current_os == "windows":
            guide_content = """# 🎵 Spotify Ad Silencer - Installation Guide (Windows)

## Quick Start (5 minutes)
1. Extract this ZIP file to a folder (e.g., C:\\SpotifyAdSilencer)
2. Double-click `SpotifyAdSilencer.exe` to run
3. That's it! The app will detect Spotify ads automatically

## Running at Startup (Optional)
1. Press Win+R, type `shell:startup`, press Enter
2. Copy `SpotifyAdSilencer.exe` to this folder
3. The app will start automatically when Windows boots

## Troubleshooting
- If Windows shows a security warning, click "More info" → "Run anyway"
- Make sure Spotify desktop app is installed (not web version)
- Check that Windows Audio Service is running

## 💖 Support This Project
If this app saves you from Spotify ads, consider supporting development:
- See DONATIONS.txt for ways to contribute
- Star us on GitHub: [Your GitHub URL]
- Share with friends who hate Spotify ads!

## Need Help?
- GitHub Issues: [Your GitHub URL]/issues
- Email: [Your Email]
"""
        elif self.current_os == "darwin":  # macOS
            guide_content = """# 🎵 Spotify Ad Silencer - Installation Guide (macOS)

## Quick Start (5 minutes)
1. Extract this ZIP file to Applications folder
2. Double-click `SpotifyAdSilencer` to run
3. Grant accessibility permissions when prompted
4. That's it! The app will detect Spotify ads automatically

## Granting Permissions
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Click the lock icon and enter your password
3. Add SpotifyAdSilencer to the list
4. Restart the app

## Running at Startup (Optional)
1. System Preferences → Users & Groups → Login Items
2. Click "+" and add SpotifyAdSilencer
3. The app will start automatically when you log in

## 💖 Support This Project
If this app saves you from Spotify ads, please consider supporting:
- See DONATIONS.txt for contribution options
- Star us on GitHub: [Your GitHub URL]
- Tell other Mac users about this tool!

## Need Help?
- GitHub Issues: [Your GitHub URL]/issues
- Email: [Your Email]
"""
        else:  # Linux
            guide_content = """# 🎵 Spotify Ad Silencer - Installation Guide (Linux)

## Quick Start (5 minutes)
1. Extract this ZIP file to ~/Applications or /opt/
2. Make executable: `chmod +x SpotifyAdSilencer`
3. Run: `./SpotifyAdSilencer`
4. Install system dependencies if needed (see below)

## System Dependencies
### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install pulseaudio pulseaudio-utils wmctrl xdotool
```

### Fedora/RHEL:
```bash
sudo dnf install pulseaudio pulseaudio-utils wmctrl xdotool
```

### Arch Linux:
```bash
sudo pacman -S pulseaudio wmctrl xdotool
```

## Running at Startup (Optional)
1. Create ~/.config/autostart/spotify-ad-silencer.desktop
2. Add the provided desktop entry
3. Or use your desktop environment's startup applications

## 💖 Support This Project
If this tool improves your Spotify experience:
- See DONATIONS.txt for ways to contribute
- Star us on GitHub: [Your GitHub URL]
- Package for your favorite Linux distro!

## Need Help?
- GitHub Issues: [Your GitHub URL]/issues
- Email: [Your Email]
"""
        
        with open(package_dir / "INSTALL.md", "w", encoding="utf-8") as f:
            f.write(guide_content)
    
    def create_donation_info(self, package_dir):
        """Create donation information file"""
        donation_content = """# 💖 Support Spotify Ad Silencer

This software is **completely free** and will always remain so!

However, if this tool saves you from annoying Spotify ads and you'd like to support continued development, here are ways to contribute:

## 🎯 Why Donate?
- Keep the project alive and updated
- Support new features and platform compatibility
- Help with hosting costs for updates
- Show appreciation for 100+ hours of development

## 💳 Donation Options

### One-time Donations
- **PayPal**: https://paypal.me/jacobscode?country.x=SE&locale.x=sv_SE
- **GitHub Sponsors**: https://github.com/sponsors/JacobOmateq
- **Bitcoin**: 33MvnRKM9QmimTuhTZMVmKbYRBBf2umdoM

### Monthly Support
- **GitHub Sponsors**: Starting at $1/month

## 🎁 Donation Tiers (Optional Recognition)

### 🥉 Supporter ($5+)
- Warm fuzzy feeling knowing you supported open source
- Listed in SUPPORTERS.md (if you want)

### 🥈 Contributor ($25+)
- Priority email support
- Early access to beta features
- Your name in app credits (optional)

### 🥇 Sponsor ($100+)
- Direct influence on feature roadmap
- Custom thank-you in app
- Video call with developer (if desired)

## 🌟 Alternative Ways to Support

**Can't donate? No problem! You can help by:**
- ⭐ Starring the GitHub repository
- 🐛 Reporting bugs and issues
- 📢 Sharing with friends who use Spotify
- 💬 Joining discussions and providing feedback
- 🔧 Contributing code (if you're a developer)

## 📊 Transparency

All donations help with:
- 🖥️ Development tools and software licenses
- ☁️ Server costs for update distribution
- 🧪 Testing on different operating systems
- 📖 Documentation and video tutorials
- ⏰ Time to maintain and improve the project

## Current Supporters

*Thank you to all supporters! You make this project possible.*

[This section would list supporters who agreed to be mentioned]

---

**Remember**: This software will always be free, regardless of donations. Donate only if you want to and can afford it! 💙
"""
        
        with open(package_dir / "DONATIONS.txt", "w", encoding="utf-8") as f:
            f.write(donation_content)
    
    def create_startup_scripts(self, package_dir):
        """Create platform-specific startup scripts"""
        if self.current_os == "windows":
            # Create batch file for easy startup
            batch_content = """@echo off
echo Starting Spotify Ad Silencer...
echo Minimize this window - the app is running in the background
echo Close this window to stop the app
SpotifyAdSilencer.exe
pause
"""
            with open(package_dir / "Start_AdSilencer.bat", "w") as f:
                f.write(batch_content)
                
        elif self.current_os == "darwin":
            # Create shell script for macOS
            script_content = """#!/bin/bash
echo "Starting Spotify Ad Silencer..."
echo "This will run in the background. Close this terminal to stop."
./SpotifyAdSilencer
"""
            script_path = package_dir / "start_adsilencer.sh"
            with open(script_path, "w") as f:
                f.write(script_content)
            script_path.chmod(0o755)
            
        else:  # Linux
            # Create desktop entry
            desktop_content = f"""[Desktop Entry]
Name=Spotify Ad Silencer
Comment=Automatically mutes Spotify ads
Exec={package_dir}/SpotifyAdSilencer
Icon=audio-x-generic
Terminal=false
Type=Application
Categories=AudioVideo;Audio;
StartupNotify=true
"""
            with open(package_dir / "spotify-ad-silencer.desktop", "w") as f:
                f.write(desktop_content)
    
    def create_zip_archive(self, source_dir, zip_path):
        """Create ZIP archive of the package"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arc_name = file_path.relative_to(source_dir.parent)
                    zip_file.write(file_path, arc_name)
    
    def build_all_platforms(self):
        """Build for all supported platforms"""
        print("Starting cross-platform build process...")
        
        self.clean_build_dirs()
        
        if self.build_executable():
            self.create_portable_package()
            print(f"Build completed for {self.current_os}")
        else:
            print(f"Build failed for {self.current_os}")
            return False
        
        return True

if __name__ == "__main__":
    builder = PackageBuilder()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        builder.clean_build_dirs()
        print("Build directories cleaned")
    else:
        success = builder.build_all_platforms()
        if success:
            print("Build process completed successfully!")
            print("Check the 'dist' folder for your distributable packages")
        else:
            print("Build process failed")
            sys.exit(1)
