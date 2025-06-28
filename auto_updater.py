import os
import shutil
import requests
import platform
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, current_version: str, repo_owner: str = "JacobOmateq", repo_name: str = "spotify-ad-silencer"):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def download_and_install_update(self, update_info: dict) -> bool:
        """Download and install update automatically"""
        try:
            # Get platform-specific download URL
            download_url = self._get_platform_download_url(update_info)
            if not download_url:
                logger.error("No suitable download found for this platform")
                return False
            
            logger.info(f"Downloading update from: {download_url}")
            
            # Download to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "update.zip")
                
                # Download the update
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info("Download completed, installing update...")
                
                # Create update script and restart
                return self._install_update(temp_file)
                
        except Exception as e:
            logger.error(f"Error during auto-update: {e}")
            return False
    
    def _get_platform_download_url(self, update_info: dict) -> Optional[str]:
        """Get download URL for current platform"""
        system = platform.system().lower()
        platform_map = {
            "windows": "windows",
            "darwin": "macos", 
            "linux": "linux"
        }
        
        platform_name = platform_map.get(system)
        if not platform_name:
            return None
        
        # Find matching asset for platform
        for asset in update_info.get("assets", []):
            name = asset.get("name", "").lower()
            if platform_name in name and name.endswith(('.zip', '.exe', '.dmg')):
                return asset.get("browser_download_url")
        
        return None
    
    def _install_update(self, update_file: str) -> bool:
        """Install the downloaded update"""
        try:
            current_exe = Path(__file__).parent.absolute()
            
            if platform.system() == "Windows":
                return self._install_update_windows(update_file, current_exe)
            elif platform.system() == "Darwin":
                return self._install_update_macos(update_file, current_exe)
            else:
                return self._install_update_linux(update_file, current_exe)
                
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            return False
    
    def _install_update_windows(self, update_file: str, current_exe: Path) -> bool:
        """Windows-specific update installation"""
        # Create batch script to replace executable after app exits
        batch_script = f"""
        @echo off
        timeout /t 2 /nobreak > nul
        del "{current_exe}\\*.exe"
        powershell -command "Expand-Archive -Path '{update_file}' -DestinationPath '{current_exe}' -Force"
        start "" "{current_exe}\\SpotifyAdSilencer.exe"
        del "%~f0"
        """
        
        batch_file = current_exe / "update.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_script)
        
        # Run batch script and exit
        subprocess.Popen([str(batch_file)], shell=True)
        return True
    
    def _install_update_macos(self, update_file: str, current_exe: Path) -> bool:
        """macOS-specific update installation"""
        # Similar approach with shell script
        shell_script = f"""#!/bin/bash
        sleep 2
        rm -rf "{current_exe}"/*
        unzip -o "{update_file}" -d "{current_exe}"
        chmod +x "{current_exe}/SpotifyAdSilencer"
        open "{current_exe}/SpotifyAdSilencer"
        rm "$0"
        """
        
        script_file = current_exe / "update.sh"
        with open(script_file, 'w') as f:
            f.write(shell_script)
        
        os.chmod(script_file, 0o755)
        subprocess.Popen([str(script_file)])
        return True
    
    def _install_update_linux(self, update_file: str, current_exe: Path) -> bool:
        """Linux-specific update installation"""
        # Similar to macOS
        shell_script = f"""#!/bin/bash
        sleep 2
        rm -rf "{current_exe}"/*
        unzip -o "{update_file}" -d "{current_exe}"
        chmod +x "{current_exe}/SpotifyAdSilencer"
        "{current_exe}/SpotifyAdSilencer" &
        rm "$0"
        """
        
        script_file = current_exe / "update.sh"
        with open(script_file, 'w') as f:
            f.write(shell_script)
        
        os.chmod(script_file, 0o755)
        subprocess.Popen([str(script_file)])
        return True 