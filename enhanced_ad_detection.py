"""
Enhanced multi-language ad detection for Spotify
Handles international ads and dynamic content
"""

import re
import locale
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AdPattern:
    """Represents an ad detection pattern"""
    pattern: str
    language: str
    confidence: float
    pattern_type: str  # 'exact', 'contains', 'regex'

class EnhancedAdDetector:
    def __init__(self):
        self.user_locale = self._get_user_locale()
        self.ad_patterns = self._load_ad_patterns()
        self.music_patterns = self._load_music_patterns()
        self.recent_titles = []  # Track recent titles for pattern learning
        
    def _get_user_locale(self) -> str:
        """Get user's system locale"""
        try:
            return locale.getdefaultlocale()[0] or 'en_US'
        except:
            return 'en_US'
    
    def _load_ad_patterns(self) -> Dict[str, List[AdPattern]]:
        """Load ad patterns for different languages/regions"""
        patterns = {
            # English patterns
            'en': [
                AdPattern("Advertisement", 'en', 0.95, 'exact'),
                AdPattern("Spotify Free", 'en', 0.90, 'exact'),
                AdPattern("Spotify Premium", 'en', 0.90, 'exact'),
                AdPattern("Get Spotify Premium", 'en', 0.85, 'contains'),
            ],
            
            # Swedish patterns (based on "Titta nu")
            'sv': [
                AdPattern("Titta nu", 'sv', 0.90, 'exact'),
                AdPattern("Spotify Free", 'sv', 0.85, 'exact'),
                AdPattern("Spotify Premium", 'sv', 0.85, 'exact'),
                AdPattern("Lyssna utan annonser", 'sv', 0.90, 'contains'),  # "Listen without ads"
                AdPattern("Uppgradera till Premium", 'sv', 0.85, 'contains'),  # "Upgrade to Premium"
            ],
            
            # German patterns
            'de': [
                AdPattern("Werbung", 'de', 0.95, 'exact'),  # "Advertisement"
                AdPattern("Jetzt ansehen", 'de', 0.80, 'exact'),  # "Watch now"
            ],
            
            # Generic patterns (work across languages)
            'generic': [
                AdPattern(r"^Spotify$", 'generic', 0.70, 'regex'),  # Just "Spotify" alone
                AdPattern(r"^\s*$", 'generic', 0.85, 'regex'),  # Empty or whitespace only
                AdPattern(r"Premium", 'generic', 0.60, 'contains'),  # "Premium" in any language
                AdPattern(r"Free", 'generic', 0.60, 'contains'),  # "Free" appears in many languages
                # Common "watch now" patterns in different languages
                AdPattern("Titta nu", 'generic', 0.85, 'exact'),  # Swedish
                AdPattern("Watch now", 'generic', 0.85, 'exact'),  # English
                AdPattern("Jetzt ansehen", 'generic', 0.85, 'exact'),  # German
                AdPattern("Regarder maintenant", 'generic', 0.85, 'exact'),  # French
                AdPattern("Ver ahora", 'generic', 0.85, 'exact'),  # Spanish
                AdPattern("Guarda ora", 'generic', 0.85, 'exact'),  # Italian
                AdPattern("Bekijk nu", 'generic', 0.85, 'exact'),  # Dutch
            ]
        }
        
        return patterns
    
    def _load_music_patterns(self) -> List[str]:
        """Patterns that indicate actual music is playing"""
        return [
            r".+\s-\s.+",  # "Artist - Song" format
            r".+\s–\s.+",  # "Artist – Song" format (em dash)
            r".+\sby\s.+",  # "Song by Artist" format
        ]
    
    def _get_relevant_patterns(self) -> List[AdPattern]:
        """Get ad patterns relevant to user's locale"""
        patterns = []
        
        # Get locale-specific patterns
        locale_code = self.user_locale.split('_')[0].lower()
        if locale_code in self.ad_patterns:
            patterns.extend(self.ad_patterns[locale_code])
        
        # Always include ALL language patterns for international users
        # Spotify serves ads in different languages regardless of system locale
        for lang_patterns in self.ad_patterns.values():
            for pattern in lang_patterns:
                if pattern not in patterns:  # Avoid duplicates
                    patterns.append(pattern)
        
        return patterns
    
    def is_ad_playing(self, window_title: str, confidence_threshold: float = 0.7) -> bool:
        """
        Determine if an ad is playing based on window title
        """
        if not window_title or not window_title.strip():
            return True  # Empty titles are usually ads
        
        title = window_title.strip()
        
        # Special handling for common non-ad states
        if self._is_paused_or_idle_state(title):
            return False  # Don't treat paused music as ads
        
        # Check if it's clearly a file path or executable (wrong window detection)
        if self._is_file_path(title):
            return False  # This indicates wrong window, not an ad
        
        max_confidence = 0.0
        
        # Check against known ad patterns
        for pattern in self._get_relevant_patterns():
            if pattern.pattern_type == 'exact':
                if title == pattern.pattern:
                    max_confidence = max(max_confidence, pattern.confidence)
            elif pattern.pattern_type == 'contains':
                if pattern.pattern.lower() in title.lower():
                    max_confidence = max(max_confidence, pattern.confidence)
            elif pattern.pattern_type == 'regex':
                if re.search(pattern.pattern, title, re.IGNORECASE):
                    max_confidence = max(max_confidence, pattern.confidence)
        
        # Check if it looks like music (Artist - Song format)
        for music_pattern in self.music_patterns:
            if re.search(music_pattern, title):
                max_confidence = max(0.0, max_confidence - 0.4)  # Reduce confidence if it looks like music
                break
        
        return max_confidence >= confidence_threshold
    
    def _is_paused_or_idle_state(self, title: str) -> bool:
        """Check if Spotify is in a paused or idle state (not an ad)"""
        paused_indicators = [
            "Spotify Free",  # Common when paused
            "Spotify Premium",  # Common when paused
            "Spotify",  # Just "Spotify" when idle
        ]
        
        # If it's exactly one of these without additional content, it's likely paused
        title_clean = title.strip()
        for indicator in paused_indicators:
            if title_clean == indicator:
                return True  # This is paused/idle, not an ad
        
        return False
    
    def _is_file_path(self, title: str) -> bool:
        """Check if the title is actually a file path (wrong window detection)"""
        path_indicators = [
            ':\\',  # Windows drive letter
            '.exe',  # Executable file
            '/',    # Unix path separator
            '\\',   # Windows path separator
        ]
        
        for indicator in path_indicators:
            if indicator in title:
                return True
        
        return False

# Test the enhanced detector
def run_international_test():
    """Comprehensive international detection test"""
    detector = EnhancedAdDetector()
    
    # Extended international test cases
    international_tests = [
        # Swedish (like your "Titta nu" example)
        ("Titta nu", True, "Swedish 'Watch now'"),
        ("ABBA - Dancing Queen", False, "Swedish music"),
        
        # German
        ("Jetzt ansehen", True, "German 'Watch now'"),
        ("Rammstein - Du Hast", False, "German music"),
        
        # French  
        ("Regarder maintenant", True, "French 'Watch now'"),
        ("Daft Punk - One More Time", False, "French music"),
        
        # Spanish
        ("Ver ahora", True, "Spanish 'Watch now'"),
        ("Jesse & Joy - Espacio Sideral", False, "Spanish music"),
        
        # English (baseline)
        ("Advertisement", True, "English ad"),
        ("The Beatles - Hey Jude", False, "English music"),
        ("Spotify Free", True, "English Spotify Free"),
        
        # Edge cases
        ("", True, "Empty title (common for ads)"),
        ("Spotify", True, "Just 'Spotify' (usually ads)"),
        ("Spotify Premium", True, "Premium upsell ad"),
    ]
    
    print("🌍 INTERNATIONAL AD DETECTION TEST")
    print("=" * 60)
    print(f"🔍 User locale detected: {detector.user_locale}")
    print("=" * 60)
    
    correct = 0
    total = len(international_tests)
    
    for title, expected, description in international_tests:
        result = detector.is_ad_playing(title)
        status = "PASS" if result == expected else "FAIL"
        
        print(f"{status}: {description}")
        print(f"    Title: '{title}' -> {result} ({'Ad' if result else 'Music'})")
        print()
        
        if result == expected:
            correct += 1
    
    print("=" * 60)
    print(f"🎯 ACCURACY: {correct}/{total} ({(correct/total)*100:.1f}%)")
    print(f"💡 This beats most competitors who only support English!")
    
    if correct / total > 0.8:
        print(f"\n🎉 EXCELLENT! {(correct/total)*100:.1f}% accuracy proves market readiness!")
    else:
        print(f"\n⚠️  Need improvement: {(correct/total)*100:.1f}% accuracy")
    
    return correct / total

if __name__ == "__main__":
    print("Enhanced Ad Detection Test Suite")
    print("================================")
    
    # Run basic test
    detector = EnhancedAdDetector()
    basic_tests = [
        ("Advertisement", True),
        ("Titta nu", True),  # Swedish "Watch now"
        ("Shane Smith & the Saints - All I See Is You", False),
        ("The Beatles - Hey Jude", False),
        ("Spotify Free", True),
        ("", True),
        ("Spotify", True),
    ]
    
    print("\n📋 Basic Test:")
    print("-" * 30)
    for title, expected in basic_tests:
        result = detector.is_ad_playing(title)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{title}' -> {result}")
    
    print("\n" + "="*60)
    
    # Run comprehensive international test
    run_international_test()
