// Spotify Ad Silencer - Content Script
let currentAudio = null;
let musicFiles = [
  'audio/music/11L-Crickets,_Field,_Gra-1751120161151.mp3',
  'audio/music/11L-forest_ambience-1751120201424.mp3'
];

// Global error handler for extension context invalidation
window.addEventListener('error', (event) => {
  if (event.error && event.error.message && event.error.message.includes('Extension context invalidated')) {
    // Stop all monitoring to prevent further errors
    stopDOMMonitoring();
  }
});

// Spotify DOM selectors for extracting player information
const SPOTIFY_SELECTORS = {
  // Now playing bar selectors
  nowPlayingBar: '[data-testid="now-playing-widget"]',
  trackName: '[data-testid="now-playing-widget"] [data-testid="context-item-link"]',
  artistName: '[data-testid="now-playing-widget"] [data-testid="context-item-info-artist"]',
  
  // Alternative selectors
  trackNameAlt: '.Root__now-playing-bar [data-testid="context-item-link"]',
  artistNameAlt: '.Root__now-playing-bar .react-contextmenu-wrapper a',
  
  // Player controls
  playerControls: '[data-testid="player-controls"]',
  playButton: '[data-testid="control-button-playpause"]',
  
  // More specific selectors
  nowPlayingTitle: '.now-playing .track-info__name a',
  nowPlayingArtist: '.now-playing .track-info__artists a',
  
  // Generic fallbacks
  trackTitle: '.player-controls__track-info .track-info__name',
  trackArtist: '.player-controls__track-info .track-info__artists'
};

// Create audio element for playing music
function createAudioElement() {
  const audio = new Audio();
  audio.volume = 0.7;
  audio.loop = false;
  return audio;
}

// Play random music from the audio/music folder
function playMusic() {
  try {
    // Stop current audio if playing
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    
    // Select random music file
    const randomMusic = musicFiles[Math.floor(Math.random() * musicFiles.length)];
    
    // Check if extension context is still valid
    if (!chrome.runtime || !chrome.runtime.getURL) {
      return;
    }
    
    const audioUrl = chrome.runtime.getURL(randomMusic);
    
    currentAudio = createAudioElement();
    currentAudio.src = audioUrl;
    
    // Play the music
    currentAudio.play().then(() => {
      // Show visual indicator on page
      showMusicIndicator();
      
    }).catch(error => {
      console.error('Failed to play music:', error);
    });
    
    // When music ends, try to play another track
    currentAudio.addEventListener('ended', () => {
      // Only continue if we're still in an ad (tab is muted)
      try {
        if (chrome.runtime && chrome.runtime.sendMessage) {
          chrome.runtime.sendMessage({action: 'checkTabMuted'}, (response) => {
            if (chrome.runtime.lastError) {
              // Extension context invalidated, ignore
              return;
            }
            if (response && response.muted) {
              playMusic(); // Play another track
            }
          });
        }
      } catch (error) {
        // Extension context invalidated, ignore
      }
    });
    
  } catch (error) {
    console.error('Error playing music:', error);
  }
}

// Stop playing music
function stopMusic() {
  try {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
      
      // Hide visual indicator
      hideMusicIndicator();
    }
  } catch (error) {
    console.error('Error stopping music:', error);
  }
}

// Show visual indicator that music is playing instead of ad
function showMusicIndicator() {
  // Remove existing indicator
  hideMusicIndicator();
  
  // Create indicator element
  const indicator = document.createElement('div');
  indicator.id = 'spotify-ad-silencer-indicator';
  indicator.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #1ed760 0%, #1db954 100%);
      color: white;
      padding: 12px 20px;
      border-radius: 25px;
      font-family: 'Spotify Circular', Arial, sans-serif;
      font-weight: 600;
      font-size: 14px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 8px;
      animation: slideIn 0.3s ease-out;
    ">
      <span style="font-size: 16px;">🎵</span>
      <span>Ad Blocked - Playing Music</span>
    </div>
  `;
  
  // Add CSS animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(indicator);
  
  // Auto-hide after 3 seconds
  setTimeout(() => {
    if (indicator && indicator.parentNode) {
      indicator.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => {
        if (indicator && indicator.parentNode) {
          indicator.parentNode.removeChild(indicator);
        }
      }, 300);
    }
  }, 3000);
}

// Hide music indicator
function hideMusicIndicator() {
  const indicator = document.getElementById('spotify-ad-silencer-indicator');
  if (indicator && indicator.parentNode) {
    indicator.parentNode.removeChild(indicator);
  }
}

// Extract current playing information from Spotify DOM
function extractSpotifyInfo() {
  try {
    let trackName = '';
    let artistName = '';
    let isPlaying = false;
    
    // Try multiple selectors to get track name
    const trackSelectors = [
      SPOTIFY_SELECTORS.trackName,
      SPOTIFY_SELECTORS.trackNameAlt,
      SPOTIFY_SELECTORS.nowPlayingTitle,
      SPOTIFY_SELECTORS.trackTitle
    ];
    
    for (const selector of trackSelectors) {
      const element = document.querySelector(selector);
      if (element && element.textContent) {
        trackName = element.textContent.trim();
        break;
      }
    }
    
    // Try multiple selectors to get artist name
    const artistSelectors = [
      SPOTIFY_SELECTORS.artistName,
      SPOTIFY_SELECTORS.artistNameAlt,
      SPOTIFY_SELECTORS.nowPlayingArtist,
      SPOTIFY_SELECTORS.trackArtist
    ];
    
    for (const selector of artistSelectors) {
      const element = document.querySelector(selector);
      if (element && element.textContent) {
        artistName = element.textContent.trim();
        break;
      }
    }
    
    // Check if something is playing
    const playButton = document.querySelector(SPOTIFY_SELECTORS.playButton);
    if (playButton) {
      // If play button shows pause icon, something is playing
      isPlaying = playButton.getAttribute('aria-label')?.toLowerCase().includes('pause') || false;
    }
    
    // Fallback: check if page title contains track info
    if (!trackName && !artistName) {
      const title = document.title;
      if (title && title.includes(' - ') && !title.startsWith('Spotify')) {
        const parts = title.split(' - ');
        if (parts.length >= 2) {
          artistName = parts[0].trim();
          trackName = parts[1].trim();
        }
      }
    }
    
    return {
      trackName: trackName || '',
      artistName: artistName || '',
      isPlaying: isPlaying,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      title: document.title
    };
    
  } catch (error) {
    // Error extracting Spotify info
    return {
      trackName: '',
      artistName: '',
      isPlaying: false,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      title: document.title,
      error: error.message
    };
  }
}

// Detect if current content is an ad based on extracted info
function detectAdFromDOM(spotifyInfo) {
  const { trackName, artistName, title } = spotifyInfo;
  
  // Common ad patterns in artist/track names
  const adPatterns = [
    /^advertisement$/i,
    /^spotify$/i,
    /^audio ad$/i,
    /^spotify ad$/i,
    /^ad$/i,
    /^commercial$/i,
    /^promo$/i,
    /^sponsored$/i
  ];
  
  // Check artist name
  if (artistName) {
    for (const pattern of adPatterns) {
      if (pattern.test(artistName)) {
        return {
          isAd: true,
          reason: `Artist name matches ad pattern: "${artistName}"`,
          source: 'dom-artist',
          pattern: pattern.source
        };
      }
    }
  }
  
  // Check track name
  if (trackName) {
    for (const pattern of adPatterns) {
      if (pattern.test(trackName)) {
        return {
          isAd: true,
          reason: `Track name matches ad pattern: "${trackName}"`,
          source: 'dom-track',
          pattern: pattern.source
        };
      }
    }
  }
  
  // Check for generic ad indicators
  const lowerArtist = artistName.toLowerCase();
  const lowerTrack = trackName.toLowerCase();
  
  if (lowerArtist.includes('advertisement') || 
      lowerTrack.includes('advertisement') ||
      lowerArtist.includes('commercial') ||
      lowerTrack.includes('commercial')) {
    return {
      isAd: true,
      reason: `Contains ad keywords: artist="${artistName}", track="${trackName}"`,
      source: 'dom-keywords'
    };
  }
  
  // Check if no artist/track info (common for ads)
  if (!artistName && !trackName && title.includes('Spotify')) {
    return {
      isAd: true,
      reason: 'No artist/track info and generic Spotify title',
      source: 'dom-missing-info'
    };
  }
  
  return {
    isAd: false,
    reason: `Normal track: "${artistName} - ${trackName}"`,
    source: 'dom-analysis'
  };
}

// Send current Spotify info to background script
function sendSpotifyInfoToBackground() {
  try {
    // Check if extension context is still valid
    if (!chrome.runtime || !chrome.runtime.sendMessage) {
      stopDOMMonitoring();
      return;
    }
    
    const spotifyInfo = extractSpotifyInfo();
    const adDetection = detectAdFromDOM(spotifyInfo);
    
    const payload = {
      action: 'spotifyDOMInfo',
      spotifyInfo: spotifyInfo,
      adDetection: adDetection
    };
    
    chrome.runtime.sendMessage(payload, (response) => {
      if (chrome.runtime.lastError) {
        // Extension context invalidated, stop monitoring
        stopDOMMonitoring();
      }
    });
  } catch (error) {
    // Extension context invalidated, stop monitoring
    stopDOMMonitoring();
  }
}

// Start monitoring DOM changes and send info periodically
let domMonitorInterval = null;

function startDOMMonitoring() {
  // Clear existing interval
  if (domMonitorInterval) {
    clearInterval(domMonitorInterval);
  }
  
  // Send info every 2 seconds
  domMonitorInterval = setInterval(sendSpotifyInfoToBackground, 2000);
  
  // Send immediately
  sendSpotifyInfoToBackground();
}

function stopDOMMonitoring() {
  if (domMonitorInterval) {
    clearInterval(domMonitorInterval);
    domMonitorInterval = null;
  }
}

// Listen for messages from background script
try {
  if (chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      try {
        switch (request.action) {
          case 'playMusic':
            playMusic();
            sendResponse({ success: true });
            break;
            
          case 'stopMusic':
            stopMusic();
            sendResponse({ success: true });
            break;
            
          case 'startDOMMonitoring':
            startDOMMonitoring();
            sendResponse({ success: true });
            break;
            
          case 'stopDOMMonitoring':
            stopDOMMonitoring();
            sendResponse({ success: true });
            break;
            
          case 'getSpotifyInfo':
            const spotifyInfo = extractSpotifyInfo();
            const adDetection = detectAdFromDOM(spotifyInfo);
            sendResponse({ 
              spotifyInfo: spotifyInfo,
              adDetection: adDetection,
              success: true 
            });
            break;
            
          case 'checkTabMuted':
            // This would need to be handled by background script
            sendResponse({ muted: document.hidden || document.title.includes('Advertisement') });
            break;
        }
      } catch (error) {
        // Extension context may be invalidated
        stopDOMMonitoring();
      }
    });
  }
} catch (error) {
  // Extension context invalidated
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  // Start DOM monitoring immediately
  setTimeout(startDOMMonitoring, 1000); // Wait 1 second for Spotify to load
});

// Also initialize immediately in case DOM is already loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(startDOMMonitoring, 1000);
  });
} else {
  // Start monitoring after a short delay
  setTimeout(startDOMMonitoring, 2000);
} 