import time
import psutil
import platform
import subprocess
import os
import logging
import random
import glob
from typing import Optional, Dict, Any

# Try to import pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pygame not available. Random audio playback will be disabled.")
    logger.info("To enable random audio playback, install pygame with: pip install pygame")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Detect the operating system
CURRENT_OS = platform.system().lower()
logger.info(f"Detected OS: {CURRENT_OS}")

# Import platform-specific libraries
if CURRENT_OS == 'windows':
    try:
        import pygetwindow as gw
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
        from comtypes import CLSCTX_ALL
        import win32gui
        import win32process
        WINDOWS_LIBS_AVAILABLE = True
    except ImportError as e:
        logger.error(f"Windows libraries not available: {e}")
        WINDOWS_LIBS_AVAILABLE = False

elif CURRENT_OS == 'darwin':  # macOS
    try:
        # macOS uses AppleScript for window detection and audio control
        MACOS_LIBS_AVAILABLE = True
    except ImportError as e:
        logger.error(f"macOS libraries not available: {e}")
        MACOS_LIBS_AVAILABLE = False

elif CURRENT_OS == 'linux':
    try:
        import pulsectl
        LINUX_LIBS_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Linux audio libraries not available: {e}")
        LINUX_LIBS_AVAILABLE = False
else:
    logger.warning(f"Unsupported OS: {CURRENT_OS}")

class ProcessSpecificAudioController:
    def __init__(self):
        self.is_spotify_muted = False
        self.spotify_original_volume = 1.0
        self.spotify_process_names = self._get_spotify_process_names()
        self._setup_audio_control()
    
    def _get_spotify_process_names(self):
        """Get Spotify process names for the current OS"""
        if CURRENT_OS == 'windows':
            return ['Spotify.exe']
        elif CURRENT_OS == 'darwin':
            return ['Spotify']
        elif CURRENT_OS == 'linux':
            return ['spotify', 'Spotify']
        else:
            return ['spotify', 'Spotify', 'Spotify.exe']
    
    def _setup_audio_control(self):
        """Initialize audio control based on the current OS"""
        if CURRENT_OS == 'windows' and WINDOWS_LIBS_AVAILABLE:
            self._setup_windows_audio()
        elif CURRENT_OS == 'darwin':
            self._setup_macos_audio()
        elif CURRENT_OS == 'linux' and LINUX_LIBS_AVAILABLE:
            self._setup_linux_audio()
        else:
            logger.warning("Process-specific audio control not available on this platform")
    
    def _setup_windows_audio(self):
        """Setup Windows audio control using pycaw"""
        try:
            logger.info("Windows process-specific audio control initialized")
        except Exception as e:
            logger.error(f"Failed to setup Windows audio control: {e}")
    
    def _setup_macos_audio(self):
        """Setup macOS audio control using AppleScript"""
        logger.info("macOS process-specific audio control initialized")
    
    def _setup_linux_audio(self):
        """Setup Linux audio control using PulseAudio"""
        try:
            self.pulse = pulsectl.Pulse('spotify-ad-silencer')
            logger.info("Linux PulseAudio process-specific control initialized")
        except Exception as e:
            logger.error(f"Failed to setup Linux audio control: {e}")
            self.pulse = None
    
    def set_spotify_mute(self, mute: bool):
        """Set Spotify process audio mute state (cross-platform)"""
        if CURRENT_OS == 'windows':
            self._set_spotify_mute_windows(mute)
        elif CURRENT_OS == 'darwin':
            self._set_spotify_mute_macos(mute)
        elif CURRENT_OS == 'linux':
            self._set_spotify_mute_linux(mute)
        else:
            logger.warning("Process-specific mute operation not supported on this platform")
    
    def _set_spotify_mute_windows(self, mute: bool):
        """Windows-specific Spotify process mute control"""
        if not WINDOWS_LIBS_AVAILABLE:
            logger.warning("Windows audio control not available")
            return
        
        try:
            # Get all audio sessions
            sessions = AudioUtilities.GetAllSessions()
            spotify_sessions = []
            
            # Find Spotify audio sessions
            for session in sessions:
                if session.Process and session.Process.name() in self.spotify_process_names:
                    spotify_sessions.append(session)
            
            if not spotify_sessions:
                logger.warning("No Spotify audio sessions found")
                return
            
            # Control each Spotify session
            for session in spotify_sessions:
                volume = session.SimpleAudioVolume
                if mute and not self.is_spotify_muted:
                    # Store original volume before muting
                    self.spotify_original_volume = volume.GetMasterVolume()
                    volume.SetMute(True, None)
                    logger.info(f"Muted Spotify process (PID: {session.Process.pid})")
                elif not mute and self.is_spotify_muted:
                    # Unmute and restore original volume
                    volume.SetMute(False, None)
                    volume.SetMasterVolume(self.spotify_original_volume, None)
                    logger.info(f"Unmuted Spotify process (PID: {session.Process.pid})")
            
            self.is_spotify_muted = mute
            
        except Exception as e:
            logger.error(f"Failed to control Spotify audio on Windows: {e}")
    
    def _set_spotify_mute_macos(self, mute: bool):
        """macOS-specific Spotify process mute control using AppleScript"""
        try:
            if mute and not self.is_spotify_muted:
                # Get current Spotify volume
                result = subprocess.run([
                    'osascript', '-e', 
                    'tell application "Spotify" to get sound volume'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.spotify_original_volume = int(result.stdout.strip())
                
                # Mute Spotify
                subprocess.run([
                    'osascript', '-e', 
                    'tell application "Spotify" to set sound volume to 0'
                ], check=True)
                
                self.is_spotify_muted = True
                logger.info("Muted Spotify on macOS")
                
            elif not mute and self.is_spotify_muted:
                # Restore Spotify volume
                subprocess.run([
                    'osascript', '-e', 
                    f'tell application "Spotify" to set sound volume to {self.spotify_original_volume}'
                ], check=True)
                
                self.is_spotify_muted = False
                logger.info("Unmuted Spotify on macOS")
                
        except Exception as e:
            logger.error(f"Failed to control Spotify audio on macOS: {e}")
    
    def _set_spotify_mute_linux(self, mute: bool):
        """Linux-specific Spotify process mute control using PulseAudio"""
        if not hasattr(self, 'pulse') or not self.pulse:
            logger.warning("Linux audio control not available")
            return
        
        try:
            # Get all sink inputs (application audio streams)
            sink_inputs = self.pulse.sink_input_list()
            spotify_inputs = []
            
            # Find Spotify sink inputs
            for sink_input in sink_inputs:
                if hasattr(sink_input, 'proplist') and sink_input.proplist:
                    app_name = sink_input.proplist.get('application.name', '').lower()
                    process_name = sink_input.proplist.get('application.process.binary', '').lower()
                    
                    if ('spotify' in app_name or 
                        any(proc.lower() in process_name for proc in self.spotify_process_names)):
                        spotify_inputs.append(sink_input)
            
            if not spotify_inputs:
                logger.warning("No Spotify audio streams found")
                return
            
            # Control each Spotify audio stream
            for sink_input in spotify_inputs:
                if mute and not self.is_spotify_muted:
                    # Store original volume before muting
                    self.spotify_original_volume = sink_input.volume.value_flat
                    self.pulse.volume_set_all_chans(sink_input, 0.0)
                    logger.info(f"Muted Spotify audio stream (index: {sink_input.index})")
                elif not mute and self.is_spotify_muted:
                    # Restore original volume
                    self.pulse.volume_set_all_chans(sink_input, self.spotify_original_volume)
                    logger.info(f"Unmuted Spotify audio stream (index: {sink_input.index})")
            
            self.is_spotify_muted = mute
            
        except Exception as e:
            logger.error(f"Failed to control Spotify audio on Linux: {e}")

class CrossPlatformSpotifyDetector:
    def __init__(self):
        self.spotify_process_names = self._get_spotify_process_names()
    
    def _get_spotify_process_names(self):
        """Get Spotify process names for the current OS"""
        if CURRENT_OS == 'windows':
            return ['Spotify.exe']
        elif CURRENT_OS == 'darwin':
            return ['Spotify']
        elif CURRENT_OS == 'linux':
            return ['spotify', 'Spotify']
        else:
            return ['spotify', 'Spotify', 'Spotify.exe']
    
    def is_spotify_running(self) -> bool:
        """Check if Spotify process is running (cross-platform)"""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in self.spotify_process_names:
                return True
        return False
    
    def get_spotify_window(self) -> Optional[Any]:
        """Get Spotify window (cross-platform)"""
        if CURRENT_OS == 'windows':
            return self._get_spotify_window_windows()
        elif CURRENT_OS == 'darwin':
            return self._get_spotify_window_macos()
        elif CURRENT_OS == 'linux':
            return self._get_spotify_window_linux()
        else:
            logger.warning("Window detection not supported on this platform")
            return None
    
    def _get_spotify_window_windows(self):
        """Windows-specific window detection"""
        if not WINDOWS_LIBS_AVAILABLE:
            return None
        
        try:
            # Try to find windows with "Spotify" in the title first
            all_windows = gw.getAllWindows()
            spotify_titled_windows = []
            
            for window in all_windows:
                if window.title and 'Spotify' in window.title:
                    # Exclude IDE windows
                    if not any(ide in window.title for ide in ['Cursor', 'VSCode', 'Visual Studio', 'Atom', 'Sublime', '.py', '.txt', '.js', '.html']):
                        spotify_titled_windows.append(window)
            
            if spotify_titled_windows:
                return spotify_titled_windows[0]
            
            # If no "Spotify" titled windows found, look for Spotify process windows
            spotify_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in self.spotify_process_names:
                    spotify_processes.append(proc.info['pid'])
            
            if not spotify_processes:
                return None
            
            # Find windows belonging to Spotify processes
            def enum_windows_callback(hwnd, spotify_windows):
                if win32gui.IsWindowVisible(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid in spotify_processes:
                        title = win32gui.GetWindowText(hwnd)
                        if title and len(title.strip()) > 0:
                            if not any(skip in title.lower() for skip in ['spotify helper', 'crashpad']):
                                spotify_windows.append((hwnd, title))
            
            spotify_windows = []
            win32gui.EnumWindows(enum_windows_callback, spotify_windows)
            
            if spotify_windows:
                hwnd, title = spotify_windows[0]
                class SpotifyWindow:
                    def __init__(self, hwnd, title):
                        self.title = title
                        self._hwnd = hwnd
                return SpotifyWindow(hwnd, title)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding Spotify window on Windows: {e}")
            return None
    
    def _get_spotify_window_macos(self):
        """macOS-specific window detection using AppleScript"""
        try:
            # Get window title of Spotify app
            result = subprocess.run([
                'osascript', '-e', 
                'tell application "System Events" to get the title of every window of application process "Spotify"'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                titles = result.stdout.strip().split(', ')
                if titles and titles[0]:
                    class SpotifyWindow:
                        def __init__(self, title):
                            self.title = title.strip('"')
                    return SpotifyWindow(titles[0])
            
            return None
        except Exception as e:
            logger.error(f"Error finding Spotify window on macOS: {e}")
            return None
    
    def _get_spotify_window_linux(self):
        """Linux-specific window detection using wmctrl or xdotool"""
        try:
            # Try wmctrl first
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Spotify' in line or any(proc in line.lower() for proc in self.spotify_process_names):
                        # Extract window title (after the third space)
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            title = parts[3]
                            class SpotifyWindow:
                                def __init__(self, title):
                                    self.title = title
                            return SpotifyWindow(title)
            
            # Try xdotool as fallback
            result = subprocess.run(['xdotool', 'search', '--name', 'Spotify'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                window_id = result.stdout.strip().split('\n')[0]
                result = subprocess.run(['xdotool', 'getwindowname', window_id], capture_output=True, text=True)
                if result.returncode == 0:
                    class SpotifyWindow:
                        def __init__(self, title):
                            self.title = title.strip()
                    return SpotifyWindow(result.stdout)
            
            return None
        except Exception as e:
            logger.error(f"Error finding Spotify window on Linux: {e}")
            return None

class EnhancedAudioPlayer:
    def __init__(self, audio_directory="audio"):
        self.audio_directory = audio_directory
        self.music_directory = os.path.join(audio_directory, "music")
        self.voice_directory = os.path.join(audio_directory, "voice")
        self.current_audio = None
        self.is_playing = False
        self.current_stage = None  # 'voice' or 'music'
        self.music_queue = []
        self._initialize_pygame()
    
    def _initialize_pygame(self):
        """Initialize pygame mixer for audio playback"""
        if not PYGAME_AVAILABLE:
            logger.warning("pygame not available. Random audio playback will be disabled.")
            return
            
        try:
            pygame.mixer.init()
            logger.info("Audio player initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio player: {e}")
            logger.warning("Random audio playback will be disabled")
    
    def get_random_voice_file(self) -> Optional[str]:
        """Get a random voice file from the voice directory"""
        return self._get_random_file_from_directory(self.voice_directory, "voice")
    
    def get_random_music_file(self) -> Optional[str]:
        """Get a random music file from the music directory"""
        return self._get_random_file_from_directory(self.music_directory, "music")
    
    def _get_random_file_from_directory(self, directory: str, file_type: str) -> Optional[str]:
        """Get a random audio file from specified directory"""
        try:
            if not os.path.exists(directory):
                logger.warning(f"{file_type.capitalize()} directory not found: {directory}")
                return None
                
            # Get all audio files from the directory
            audio_extensions = ['*.mp3', '*.wav', '*.ogg', '*.m4a']
            audio_files = []
            
            for extension in audio_extensions:
                pattern = os.path.join(directory, extension)
                audio_files.extend(glob.glob(pattern))
            
            if not audio_files:
                logger.warning(f"No {file_type} files found in {directory}")
                return None
            
            # Select a random file
            random_file = random.choice(audio_files)
            logger.info(f"Selected random {file_type} file: {os.path.basename(random_file)}")
            return random_file
            
        except Exception as e:
            logger.error(f"Error selecting random {file_type} file: {e}")
            return None
    
    def create_music_queue(self):
        """Create a shuffled queue of all music files"""
        try:
            if not os.path.exists(self.music_directory):
                logger.warning(f"Music directory not found: {self.music_directory}")
                return
                
            audio_extensions = ['*.mp3', '*.wav', '*.ogg', '*.m4a']
            music_files = []
            
            for extension in audio_extensions:
                pattern = os.path.join(self.music_directory, extension)
                music_files.extend(glob.glob(pattern))
            
            if music_files:
                random.shuffle(music_files)
                self.music_queue = music_files
                logger.info(f"Created music queue with {len(self.music_queue)} files")
            else:
                logger.warning("No music files found for queue")
                
        except Exception as e:
            logger.error(f"Error creating music queue: {e}")
    
    def get_next_music_file(self) -> Optional[str]:
        """Get the next music file from the queue"""
        if not self.music_queue:
            self.create_music_queue()  # Recreate queue if empty
            
        if self.music_queue:
            next_file = self.music_queue.pop(0)
            logger.info(f"Next music file: {os.path.basename(next_file)}")
            return next_file
        
        return None
    
    def start_ad_audio_sequence(self):
        """Start the two-stage audio sequence: voice first, then music"""
        if self.is_playing:
            return  # Already playing
        
        self.create_music_queue()  # Prepare music queue
        self._play_voice_announcement()
    
    def _play_voice_announcement(self):
        """Play a random voice announcement"""
        try:
            # Check if pygame is available and properly initialized
            if not PYGAME_AVAILABLE or not pygame.mixer.get_init():
                logger.warning("Audio player not initialized, skipping voice announcement")
                return
                
            voice_file = self.get_random_voice_file()
            if not voice_file:
                logger.warning("No voice files available, skipping to music")
                self._play_ambient_music()
                return
            
            # Load and play the voice file (play once, not looped)
            pygame.mixer.music.load(voice_file)
            pygame.mixer.music.set_volume(1.0)  # Voice at 80% volume for clarity
            pygame.mixer.music.play(0)  # Play once
            
            self.current_audio = voice_file
            self.current_stage = 'voice'
            self.is_playing = True
            logger.info(f"Playing voice announcement: {os.path.basename(voice_file)}")
            
        except Exception as e:
            logger.error(f"Error playing voice announcement: {e}")
            self._play_ambient_music()  # Fall back to music
    
    def _play_ambient_music(self):
        """Play ambient music at normal volume"""
        try:
            # Check if pygame is available and properly initialized
            if not PYGAME_AVAILABLE or not pygame.mixer.get_init():
                logger.warning("Audio player not initialized, skipping ambient music")
                return
                
            music_file = self.get_next_music_file()
            if not music_file:
                logger.warning("No music files available")
                return
            
            # Load and play the music file at normal volume
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(1.0)  # Full volume
            pygame.mixer.music.play(0)  # Play once, we'll handle the queue manually
            
            self.current_audio = music_file
            self.current_stage = 'music'
            self.is_playing = True
            logger.info(f"Playing ambient music: {os.path.basename(music_file)}")
            
        except Exception as e:
            logger.error(f"Error playing ambient music: {e}")
            self.is_playing = False
    
    def update_audio_playback(self):
        """Update audio playback - handle transitions and queuing"""
        if not self.is_playing:
            return
            
        try:
            # Check if pygame is available
            if not PYGAME_AVAILABLE or not pygame.mixer.get_init():
                return
                
            # Check if current audio finished playing
            if not pygame.mixer.music.get_busy():
                if self.current_stage == 'voice':
                    # Voice finished, start music
                    logger.info("Voice announcement finished, starting ambient music")
                    self._play_ambient_music()
                elif self.current_stage == 'music':
                    # Music finished, play next music file
                    logger.info("Music track finished, playing next track")
                    self._play_ambient_music()
                    
        except Exception as e:
            logger.error(f"Error updating audio playback: {e}")
    
    def stop_audio(self):
        """Stop the currently playing audio and reset state"""
        if not self.is_playing:
            return
        
        try:
            # Check if pygame is available and properly initialized
            if not PYGAME_AVAILABLE or not pygame.mixer.get_init():
                logger.warning("Audio player not initialized, cannot stop audio")
                return
                
            pygame.mixer.music.stop()
            self.is_playing = False
            self.current_stage = None
            self.music_queue.clear()  # Clear the music queue
            logger.info(f"Stopped playing audio: {os.path.basename(self.current_audio) if self.current_audio else 'Unknown'}")
            self.current_audio = None
            
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    

    
    def is_audio_playing(self) -> bool:
        """Check if audio is currently playing"""
        if not PYGAME_AVAILABLE:
            return False
        return self.is_playing and pygame.mixer.music.get_busy()
    
    def get_current_stage(self) -> Optional[str]:
        """Get current playback stage ('voice' or 'music')"""
        return self.current_stage if self.is_playing else None

def is_ad_playing(window_title: str) -> bool:
    """Determine if an ad is playing based on window title (enhanced multi-language detection)"""
    # Use enhanced ad detector for better international support
    try:
        from enhanced_ad_detection import EnhancedAdDetector
        if not hasattr(is_ad_playing, '_detector'):
            is_ad_playing._detector = EnhancedAdDetector()
        return is_ad_playing._detector.is_ad_playing(window_title)
    except ImportError:
        # Fallback to basic detection if enhanced module not available
        logger.warning("Enhanced ad detection not available, using basic detection")
        return _basic_ad_detection(window_title)

def _basic_ad_detection(window_title: str) -> bool:
    """Basic ad detection as fallback"""
    if not window_title:
        return True  # No title usually means ad or idle
    
    # Basic ad indicators (English-focused)
    ad_indicators = [
        "Advertisement", "Spotify Free", "Spotify Premium", "Spotify",
        "Titta nu", "Watch now", "Jetzt ansehen"  # Common international phrases
    ]
    
    # Check for explicit ad indicators
    for indicator in ad_indicators:
        if indicator in window_title:
            return True
    
    # If the title looks like music (Artist - Song format), it's not an ad
    import re
    music_patterns = [r".+\s-\s.+", r".+\s–\s.+", r".+\sby\s.+"]
    for pattern in music_patterns:
        if re.search(pattern, window_title):
            return False
    
    return True  # Default to ad if uncertain

def main():
    # Import and initialize donation system
    try:
        from donation_system import donation_manager
        
        # Show welcome message on first run
        config = donation_manager.load_config()
        if config.get("first_run", True):
            donation_manager.show_welcome_message()
        else:
            donation_manager.increment_run_counter()
            
        # Check if we should show donation reminder
        if donation_manager.should_show_reminder():
            donation_manager.show_donation_reminder()
    except ImportError:
        logger.warning("Donation system not available")
    
    logger.info(f"Starting Cross-Platform Spotify Ad Silencer with Process-Specific Audio Control on {CURRENT_OS}")
    
    audio_controller = ProcessSpecificAudioController()
    spotify_detector = CrossPlatformSpotifyDetector()
    enhanced_audio_player = EnhancedAudioPlayer()
    
    was_muted = False
    ads_blocked = 0
    session_start = time.time()
    
    while True:
        try:
            # Check if Spotify is running
            if not spotify_detector.is_spotify_running():
                logger.info("Spotify is not running. Waiting...")
                if was_muted:
                    audio_controller.set_spotify_mute(False)
                    enhanced_audio_player.stop_audio()  # Stop ambient audio when Spotify is not running
                    was_muted = False
                time.sleep(5)
                continue
            
            # Get Spotify window
            spotify_window = spotify_detector.get_spotify_window()
            if spotify_window:
                window_title = spotify_window.title
                logger.info(f"Current Spotify window title: {window_title}")
                
                # Check if ad is playing
                if is_ad_playing(window_title):
                    if not was_muted:
                        audio_controller.set_spotify_mute(True)
                        enhanced_audio_player.start_ad_audio_sequence()  # Start voice then music sequence
                        was_muted = True
                        ads_blocked += 1
                        logger.info("Advertisement detected. Muting Spotify audio and starting voice announcement followed by ambient music.")
                    else:
                        # Update audio playback (handle voice->music transitions and music queue)
                        enhanced_audio_player.update_audio_playback()
                else:
                    if was_muted:
                        audio_controller.set_spotify_mute(False)
                        enhanced_audio_player.stop_audio()  # Stop all audio when music resumes
                        was_muted = False
                        logger.info("Music playing. Unmuting Spotify audio and stopping ambient audio.")
            else:
                logger.info("Spotify window not found. Waiting...")
                if was_muted:
                    audio_controller.set_spotify_mute(False)
                    enhanced_audio_player.stop_audio()  # Stop ambient audio when Spotify window not found
                    was_muted = False
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if was_muted:
                audio_controller.set_spotify_mute(False)
                enhanced_audio_player.stop_audio()  # Stop ambient audio on shutdown
            
            # Show session stats with donation info
            try:
                from donation_system import donation_manager
                session_time = int(time.time() - session_start)
                time_saved = ads_blocked * 30  # Assume 30 seconds per ad
                donation_manager.show_stats_message(ads_blocked, time_saved)
            except ImportError:
                pass
            
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main() 