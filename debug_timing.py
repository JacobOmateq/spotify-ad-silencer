#!/usr/bin/env python3
"""
Debug timing script for Spotify Ad Silencer
Run this to see detailed timing measurements of the ad detection loop
"""

import os
import sys
import logging

# Set up debug logging to see timing measurements
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('timing_debug.log')
    ]
)

print("🕐 TIMING DEBUG MODE ENABLED")
print("=" * 50)
print("This will run Spotify Ad Silencer with detailed timing measurements.")
print("Timing logs will be shown in console and saved to 'timing_debug.log'")
print("Press Ctrl+C to stop and view timing analysis.")
print("=" * 50)
print()

# Import and run the main application
try:
    from main import main
    main()
except KeyboardInterrupt:
    print("\n🛑 Timing debug session ended.")
    print("Check 'timing_debug.log' for detailed timing analysis.")
except ImportError as e:
    print(f"❌ Error importing main module: {e}")
    print("Make sure you're running this from the same directory as main.py")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 