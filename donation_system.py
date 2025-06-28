"""
Donation system for Spotify Ad Silencer
Handles donation reminders and support messaging in a non-intrusive way
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class DonationManager:
    def __init__(self, config_dir: str = "."):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "donation_config.json")
        self.donation_links = {
            "paypal": "https://paypal.me/jacobscode?country.x=SE&locale.x=sv_SE",
            "github": "https://github.com/sponsors/yourusername",
            "bitcoin": "your-bitcoin-address"
        }
        self.load_config()
    
    def load_config(self) -> Dict:
        """Load donation configuration from file"""
        default_config = {
            "first_run": True,
            "runs_count": 0,
            "last_reminder": None,
            "reminder_dismissed": False,
            "donation_made": False,
            "remind_every_runs": 50,  # Show reminder every 50 runs
            "remind_every_days": 14   # Or every 14 days
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to handle new keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                return default_config
        except Exception as e:
            logger.warning(f"Failed to load donation config: {e}")
            return default_config
    
    def save_config(self, config: Dict):
        """Save donation configuration to file"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save donation config: {e}")
    
    def should_show_reminder(self) -> bool:
        """Check if we should show a donation reminder"""
        config = self.load_config()
        
        # Don't show if user already donated or permanently dismissed
        if config.get("donation_made") or config.get("reminder_dismissed"):
            return False
        
        # Show on first run after 5 minutes of usage
        if config.get("first_run"):
            return False  # Handle first run separately
        
        runs_count = config.get("runs_count", 0)
        last_reminder = config.get("last_reminder")
        
        # Check if enough runs have passed
        if runs_count >= config.get("remind_every_runs", 50):
            return True
        
        # Check if enough days have passed
        if last_reminder:
            try:
                last_date = datetime.fromisoformat(last_reminder)
                days_since = (datetime.now() - last_date).days
                if days_since >= config.get("remind_every_days", 14):
                    return True
            except:
                pass
        
        return False
    
    def show_welcome_message(self):
        """Show welcome message on first run"""
        print("\n" + "="*60)
        print("🎵 Welcome to Spotify Ad Silencer!")
        print("="*60)
        print("This tool is completely FREE and always will be!")
        print("If it saves you from annoying ads, consider supporting development.")
        print("💖 Check DONATIONS.txt for ways to contribute")
        print("="*60 + "\n")
        
        # Update config
        config = self.load_config()
        config["first_run"] = False
        config["runs_count"] = 1
        self.save_config(config)
    
    def show_donation_reminder(self) -> bool:
        """Show donation reminder and return whether to continue"""
        print("\n" + "="*60)
        print("💖 Enjoying Spotify Ad Silencer?")
        print("="*60)
        print("This tool has been working hard to block ads for you!")
        print("If it's saving you time and frustration, consider supporting:")
        print(f"💳 PayPal: {self.donation_links['paypal']}")
        print(f"⭐ GitHub Sponsors: {self.donation_links['github']}")
        print(f"₿ Bitcoin: {self.donation_links['bitcoin']}")
        print("\nEven $1 helps keep this project alive! 🙏")
        print("="*60)
        
        # Update config
        config = self.load_config()
        config["last_reminder"] = datetime.now().isoformat()
        config["runs_count"] = 0  # Reset counter
        self.save_config(config)
        
        return True
    
    def increment_run_counter(self):
        """Increment the run counter"""
        config = self.load_config()
        config["runs_count"] = config.get("runs_count", 0) + 1
        self.save_config(config)
    
    def mark_donation_made(self):
        """Mark that user has made a donation"""
        config = self.load_config()
        config["donation_made"] = True
        self.save_config(config)
        print("🎉 Thank you for your support! This reminder will no longer appear.")
    
    def dismiss_reminder(self):
        """Permanently dismiss donation reminders"""
        config = self.load_config()
        config["reminder_dismissed"] = True
        self.save_config(config)
        print("ℹ️ Donation reminders disabled. You can re-enable them by deleting donation_config.json")
    
    def show_stats_message(self, ads_blocked: int, time_saved: int):
        """Show stats with optional donation message"""
        if ads_blocked > 0:
            print(f"\n📊 Session Stats:")
            print(f"   🔇 Ads blocked: {ads_blocked}")
            print(f"   ⏰ Time saved: ~{time_saved} seconds")
            
            # Show donation message occasionally
            if ads_blocked % 10 == 0 and ads_blocked > 0:
                print(f"   💖 Love this tool? Consider supporting development!")
                print(f"   💳 {self.donation_links['paypal']}")

# Global instance
donation_manager = DonationManager() 