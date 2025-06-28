import requests
import json
import logging
from typing import Optional, Dict
import webbrowser

logger = logging.getLogger(__name__)

class UpdateChecker:
    def __init__(self, current_version: str, repo_owner: str = "JacobOmateq", repo_name: str = "spotify-ad-silencer"):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.releases_url = f"https://github.com/{repo_owner}/{repo_name}/releases"
    
    def check_for_updates(self, show_notification: bool = True) -> Optional[Dict]:
        """Check GitHub for latest release and compare with current version."""
        try:
            logger.debug(f"Checking for updates... Current version: {self.current_version}")
            
            response = requests.get(self.github_api_url, timeout=10)
            if response.status_code == 404:
                logger.debug("No releases found yet - this is normal for new repositories")
                return None
            elif response.status_code != 200:
                logger.warning(f"Failed to check for updates: HTTP {response.status_code}")
                return None
            
            release_data = response.json()
            latest_version = release_data.get("tag_name", "").lstrip("v")
            
            if not latest_version:
                logger.warning("No version information found in latest release")
                return None
            
            # Simple version comparison (assumes semantic versioning)
            if self._compare_versions(latest_version, self.current_version) > 0:
                update_info = {
                    "latest_version": latest_version,
                    "current_version": self.current_version,
                    "release_name": release_data.get("name", f"Version {latest_version}"),
                    "release_notes": release_data.get("body", "No release notes available"),
                    "download_url": self.releases_url,
                    "published_at": release_data.get("published_at", ""),
                    "assets": release_data.get("assets", [])
                }
                
                if show_notification:
                    self._show_update_notification(update_info)
                
                return update_info
            else:
                logger.debug("Application is up to date")
                return None
                
        except Exception as e:
            logger.warning(f"Error checking for updates: {e}")
            return None
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if version1 > version2, -1 if version1 < version2, 0 if equal."""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except:
            # Fallback string comparison
            return 1 if version1 > version2 else (-1 if version1 < version2 else 0)
    
    def _show_update_notification(self, update_info: Dict):
        """Show update notification to user"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            message = (
                f"🎉 New Version Available!\n\n"
                f"Current Version: {update_info['current_version']}\n"
                f"Latest Version: {update_info['latest_version']}\n\n"
                f"Release: {update_info['release_name']}\n\n"
                f"Would you like to download the update?"
            )
            
            result = messagebox.askyesno(
                "Spotify Ad Silencer - Update Available",
                message,
                icon="info"
            )
            
            if result:
                webbrowser.open(update_info['download_url'])
                logger.info("Opened browser to download update")
            
            root.destroy()
            
        except ImportError:
            # Fallback for systems without tkinter
            logger.info(f"Update available: v{update_info['latest_version']} (current: v{update_info['current_version']})")
            logger.info(f"Download from: {update_info['download_url']}")
        except Exception as e:
            logger.error(f"Error showing update notification: {e}")

def check_for_updates_async(current_version: str):
    """Check for updates in background thread"""
    import threading
    
    def check_updates():
        checker = UpdateChecker(current_version)
        checker.check_for_updates(show_notification=True)
    
    thread = threading.Thread(target=check_updates, daemon=True)
    thread.start()
    return thread 