"""
Embedded audio system for Spotify Ad Silencer
This provides fallback audio when external files aren't available
"""

import base64
import tempfile
import os
from typing import Optional

# Base64 encoded audio files (these would be actual encoded audio)
# For demo purposes, these are placeholder strings
EMBEDDED_VOICE_FILES = {
    "ad_break_1": """
    # This would be base64 encoded MP3 data
    # Example: UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqF...
    """,
    "ad_break_2": "# Base64 data for second voice file...",
    "ad_break_3": "# Base64 data for third voice file...",
}

EMBEDDED_MUSIC_FILES = {
    "ambient_1": "# Base64 data for ambient music 1...",
    "ambient_2": "# Base64 data for ambient music 2...",
    "ambient_3": "# Base64 data for ambient music 3...",
}

class EmbeddedAudioManager:
    def __init__(self):
        self.temp_files = []
    
    def get_voice_file(self, voice_id: str = None) -> Optional[str]:
        """Get a temporary voice file from embedded data"""
        if not voice_id:
            import random
            voice_id = random.choice(list(EMBEDDED_VOICE_FILES.keys()))
        
        return self._create_temp_file(EMBEDDED_VOICE_FILES.get(voice_id), f"voice_{voice_id}.mp3")
    
    def get_music_file(self, music_id: str = None) -> Optional[str]:
        """Get a temporary music file from embedded data"""
        if not music_id:
            import random
            music_id = random.choice(list(EMBEDDED_MUSIC_FILES.keys()))
        
        return self._create_temp_file(EMBEDDED_MUSIC_FILES.get(music_id), f"music_{music_id}.mp3")
    
    def _create_temp_file(self, base64_data: str, filename: str) -> Optional[str]:
        """Create temporary file from base64 data"""
        if not base64_data or base64_data.startswith("#"):
            return None  # Placeholder data
        
        try:
            # Decode base64 data
            audio_data = base64.b64decode(base64_data)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".mp3",
                prefix=filename.replace(".mp3", "_"),
                delete=False
            )
            
            # Write audio data
            temp_file.write(audio_data)
            temp_file.close()
            
            # Track for cleanup
            self.temp_files.append(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creating temp audio file: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()

# Utility function to convert audio files to base64 for embedding
def encode_audio_file_to_base64(file_path: str) -> str:
    """Convert audio file to base64 string for embedding"""
    try:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        print(f"Error encoding {file_path}: {e}")
        return ""

# Example usage:
if __name__ == "__main__":
    # To create embedded audio from existing files:
    audio_files = [
        "audio/voice/ads_break_1.mp3",
        "audio/music/ambient_music.mp3"
    ]
    
    for file_path in audio_files:
        if os.path.exists(file_path):
            encoded = encode_audio_file_to_base64(file_path)
            print(f"\n# {os.path.basename(file_path)}:")
            print(f'"{encoded[:100]}..."')  # Show first 100 chars 