
#!/usr/bin/env python3
"""
Debug script for testing ad detection
Use this to test specific window titles and see why they might not be detected as ads
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_ad_detection import EnhancedAdDetector

def test_ad_detection(title: str):
    """Test a specific title with detailed output"""
    detector = EnhancedAdDetector()
    
    print(f"\n🔍 TESTING: '{title}'")
    print("=" * 50)
    
    # Test with different confidence levels
    confidence_levels = [0.5, 0.6, 0.7, 0.8, 0.9]
    
    for confidence in confidence_levels:
        result = detector.is_ad_playing(title, confidence)
        status = "🔇 AD" if result else "🎵 MUSIC"
        print(f"Confidence {confidence}: {status}")
    
    # Show detailed analysis
    print(f"\nTitle length: {len(title)} characters")
    print(f"Contains ' - ': {' - ' in title}")
    print(f"Is empty/whitespace: {not title or not title.strip()}")
    print(f"Looks like file path: {any(x in title for x in [':\\', '.exe', '/', '\\'])}")
    
    # Test against specific patterns
    common_ad_words = ['Premium', 'Free', 'Ad', 'Commercial', 'Upgrade', 'Watch', 'Video']
    found_words = [word for word in common_ad_words if word.lower() in title.lower()]
    if found_words:
        print(f"Contains ad keywords: {found_words}")
    
    print("=" * 50)

def main():
    """Interactive debug session"""
    print("🎯 SPOTIFY AD DETECTION DEBUGGER")
    print("="*50)
    print("This will help debug why certain titles aren't detected as ads")
    print("Enter window titles you've seen during ads that weren't detected")
    print("Type 'quit' to exit")
    print("="*50)
    
    # Test some common cases first
    test_cases = [
        "Advertisement",
        "Spotify Free", 
        "Titta nu",
        "Premium",
        "Teddy Swims - Bad Dreams",
        "CYRIL - The Power Of Love",
        "",
        "Spotify",
        "Watch now",
        "Get Premium"
    ]
    
    print("\n📋 TESTING COMMON CASES:")
    detector = EnhancedAdDetector()
    for title in test_cases:
        result = detector.is_ad_playing(title)
        status = "🔇 AD" if result else "🎵 MUSIC"
        print(f"{status} '{title}'")
    
    print("\n" + "="*50)
    print("Now test your own titles:")
    
    while True:
        try:
            title = input("\nEnter window title to test (or 'quit'): ").strip()
            if title.lower() == 'quit':
                break
            if title:
                test_ad_detection(title)
        except KeyboardInterrupt:
            break
    
    print("\n👋 Debug session ended. Check the results above!")

if __name__ == "__main__":
    main() 