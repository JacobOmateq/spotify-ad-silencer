// Spotify Ad Silencer - Background Service Worker with Enhanced Debugging
let isMonitoring = false;
let adCount = 0;
let sessionStart = new Date();
let detectionAttempts = 0;
let spotifyDOMInfo = {}; // Store DOM info from content scripts

// Ad detection patterns (same as Python app)
const adPatterns = [
  // English
  /^Advertisement$/i, /^Spotify$/i, /^Audio Ad$/i, /^Spotify Ad$/i,
  /^Spotify - .*Advertisement/i,
  /^Spotify – Advertisement$/i, /^Spotify - Advertisement$/i,
  
  // Common Spotify generic ad titles
  /^Spotify - Web Player: Music for everyone$/i,
  /^Spotify Web Player$/i,
  /^Web Player: Music for everyone$/i,
  /^Music for everyone$/i,
  
  // Spanish
  /^Anuncio$/i, /^Publicidad$/i,
  /^Spotify – Anuncio$/i, /^Spotify - Anuncio$/i,
  /^Spotify – Publicidad$/i, /^Spotify - Publicidad$/i,
  
  // French
  /^Publicité$/i, /^Annonce$/i,
  /^Spotify – Publicité$/i, /^Spotify - Publicité$/i,
  /^Spotify – Annonce$/i, /^Spotify - Annonce$/i,
  
  // German
  /^Werbung$/i, /^Anzeige$/i,
  /^Spotify – Werbung$/i, /^Spotify - Werbung$/i,
  /^Spotify – Anzeige$/i, /^Spotify - Anzeige$/i,
  
  // Portuguese
  /^Anúncio$/i, /^Propaganda$/i,
  /^Spotify – Anúncio$/i, /^Spotify - Anúncio$/i,
  /^Spotify – Propaganda$/i, /^Spotify - Propaganda$/i,
  
  // Italian
  /^Pubblicità$/i, /^Annuncio$/i,
  /^Spotify – Pubblicità$/i, /^Spotify - Pubblicità$/i,
  /^Spotify – Annuncio$/i, /^Spotify - Annuncio$/i,
  
  // Dutch
  /^Advertentie$/i, /^Reclame$/i,
  /^Spotify – Advertentie$/i, /^Spotify - Advertentie$/i,
  /^Spotify – Reclame$/i, /^Spotify - Reclame$/i,
  
  // Swedish
  /^Annons$/i, /^Reklam$/i,
  /^Spotify – Reklam$/i, /^Spotify - Reklam$/i,
  /^Spotify – Annons$/i, /^Spotify - Annons$/i,
  
  // Norwegian
  /^Annonse$/i,
  /^Spotify – Annonse$/i, /^Spotify - Annonse$/i,
  
  // Danish
  /^Annonce$/i,
  /^Spotify – Annonce$/i, /^Spotify - Annonce$/i,
  
  // Finnish
  /^Mainos$/i,
  /^Spotify – Mainos$/i, /^Spotify - Mainos$/i,
  
  // Polish
  /^Reklama$/i,
  /^Spotify – Reklama$/i, /^Spotify - Reklama$/i,
  
  // Russian
  /^Реклама$/i,
  /^Spotify – Реклама$/i, /^Spotify - Реклама$/i,
  
  // Japanese
  /^広告$/i,
  /^Spotify – 広告$/i, /^Spotify - 広告$/i,
  
  // Korean
  /^광고$/i,
  /^Spotify – 광고$/i, /^Spotify - 광고$/i,
  
  // Chinese
  /^广告$/i, /^廣告$/i,
  /^Spotify – 广告$/i, /^Spotify - 广告$/i,
  /^Spotify – 廣告$/i, /^Spotify - 廣告$/i
];

// Enhanced ad detection with detailed logging
function isAdPlaying(title) {
  if (!title) {
    return { isAd: false, reason: 'No title provided', pattern: null };
  }
  
  const titleLength = title.length;
  
  // Check against ad patterns
  for (let i = 0; i < adPatterns.length; i++) {
    const pattern = adPatterns[i];
    if (pattern.test(title)) {
      return { 
        isAd: true, 
        reason: `Matched pattern ${i + 1}: ${pattern.source}`,
        pattern: pattern.source,
        titleLength
      };
    }
  }
  
  // Additional heuristics
  const lowerTitle = title.toLowerCase();
  
  // Short titles that contain ad-related words
  if (titleLength <= 15 && (
    lowerTitle.includes('ad') ||
    lowerTitle.includes('spot') ||
    lowerTitle === 'spotify'
  )) {
    return { 
      isAd: true, 
      reason: `Heuristic match: length=${titleLength}, contains ad/spot/spotify`,
      pattern: 'heuristic',
      titleLength
    };
  }
  
  // Generic Spotify titles that are likely ads
  if (lowerTitle.includes('music for everyone') ||
      (lowerTitle.includes('web player') && !lowerTitle.includes(' - ')) ||
      (lowerTitle.startsWith('spotify') && titleLength < 50 && !lowerTitle.includes(' - '))) {
    return { 
      isAd: true, 
      reason: `Heuristic match: generic Spotify ad title`,
      pattern: 'heuristic-generic',
      titleLength
    };
  }
  
  return { 
    isAd: false, 
    reason: `No match: length=${titleLength}, checked ${adPatterns.length} patterns`,
    pattern: null,
    titleLength
  };
}

// Enhanced ad detection using both title and DOM information
function isAdPlayingEnhanced(tab) {
  const tabId = tab.id;
  const title = tab.title;
  
  // First check DOM information if available
  const domInfo = spotifyDOMInfo[tabId];
  if (domInfo && domInfo.adDetection) {
    const timeDiff = new Date() - new Date(domInfo.timestamp);
    
    // Use DOM info if it's fresh (less than 10 seconds old)
    if (timeDiff < 10000) {
      if (domInfo.adDetection.isAd) {
        return {
          isAd: true,
          reason: `DOM Detection: ${domInfo.adDetection.reason}`,
          source: 'dom',
          domInfo: {
            artist: domInfo.artistName,
            track: domInfo.trackName,
            isPlaying: domInfo.isPlaying
          },
          titleLength: title.length
        };
      } else {
        return {
          isAd: false,
          reason: `DOM Detection: ${domInfo.adDetection.reason}`,
          source: 'dom',
          domInfo: {
            artist: domInfo.artistName,
            track: domInfo.trackName,
            isPlaying: domInfo.isPlaying
          },
          titleLength: title.length
        };
      }
    }
  }
  
  // Fallback to title-based detection
  const titleResult = isAdPlaying(title);
  return {
    ...titleResult,
    source: 'title',
    domInfo: domInfo ? {
      artist: domInfo.artistName,
      track: domInfo.trackName,
      isPlaying: domInfo.isPlaying,
      age: domInfo.timestamp ? Math.floor((new Date() - new Date(domInfo.timestamp)) / 1000) : null
    } : null
  };
}

// Get all Spotify tabs with enhanced logging
async function getSpotifyTabs() {
  try {
    const tabs = await chrome.tabs.query({
      url: ["*://*.spotify.com/*", "*://open.spotify.com/*"]
    });
    
    return tabs;
  } catch (error) {
    return [];
  }
}

// Monitor Spotify tabs for ads with enhanced logging
async function monitorTabs() {
  if (!isMonitoring) return;
  
  try {
    const spotifyTabs = await getSpotifyTabs();
    
    if (spotifyTabs.length === 0) {
      return;
    }
    
    for (const tab of spotifyTabs) {
      detectionAttempts++;
      
      const detectionResult = isAdPlayingEnhanced(tab);
      
      if (detectionResult.isAd && !tab.mutedInfo?.muted) {
        // Ad detected and tab not muted!
        const domInfo = detectionResult.domInfo;
        
        // Mute the tab
        await chrome.tabs.update(tab.id, { muted: true });
        
        // Show notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon48.png',
          title: '🔇 Spotify Ad Blocked!',
          message: `Ad detected: "${tab.title}" - Tab muted`
        });
        
        // Send message to content script to play music
        chrome.tabs.sendMessage(tab.id, {
          action: 'playMusic',
          adTitle: tab.title
        }).catch(error => {
        });
        
        adCount++;
        
        // Update popup if open
        chrome.runtime.sendMessage({
          action: 'adDetected',
          adCount: adCount,
          adTitle: tab.title,
          detectionResult: detectionResult
        }).catch(() => {}); // Ignore if popup not open
        
      } else if (!detectionResult.isAd && tab.mutedInfo?.muted) {
        // Music resumed (ad ended)
        
        // Unmute the tab
        await chrome.tabs.update(tab.id, { muted: false });
        
        // Show notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon48.png',
          title: '🎵 Music Resumed!',
          message: `Now playing: "${tab.title}"`
        });
        
        // Send message to content script to stop music
        chrome.tabs.sendMessage(tab.id, {
          action: 'stopMusic'
        }).catch(error => {
        });
        
        // Update popup if open
        chrome.runtime.sendMessage({
          action: 'adEnded',
          currentTrack: tab.title,
          detectionResult: detectionResult
        }).catch(() => {}); // Ignore if popup not open
      } else {
        // Log regular detection attempts (less verbose)
        if (detectionAttempts % 10 === 0) { // Log every 10th attempt
        }
      }
    }
  } catch (error) {
  }
}

// Start monitoring
async function startMonitoring() {
  isMonitoring = true;
  sessionStart = new Date();
  adCount = 0;
  detectionAttempts = 0;
  spotifyDOMInfo = {}; // Clear DOM info

  
  // Start DOM monitoring in all Spotify tabs
  try {
    const spotifyTabs = await getSpotifyTabs();
    for (const tab of spotifyTabs) {
      chrome.tabs.sendMessage(tab.id, { action: 'startDOMMonitoring' }).catch(error => {
      });
    }
  } catch (error) {
  }
  
  // Monitor every second
  setInterval(monitorTabs, 1000);
  
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon48.png',
    title: '🎵 Spotify Ad Silencer Active',
    message: 'Enhanced monitoring with DOM analysis active'
  });
}

// Stop monitoring
async function stopMonitoring() {
  isMonitoring = false;
  
  // Stop DOM monitoring in all Spotify tabs
  try {
    const spotifyTabs = await getSpotifyTabs();
    for (const tab of spotifyTabs) {
      chrome.tabs.sendMessage(tab.id, { action: 'stopDOMMonitoring' }).catch(error => {
        // Ignore errors - tab might be closed
      });
    }
  } catch (error) {
  }
}

// Handle messages from popup with enhanced responses
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'startMonitoring':
      startMonitoring();
      sendResponse({ success: true });
      break;
      
    case 'stopMonitoring':
      stopMonitoring();
      sendResponse({ success: true });
      break;
      
    case 'getStatus':
      try {
        sendResponse({
          isMonitoring: isMonitoring || false,
          adCount: adCount || 0,
          sessionStart: sessionStart ? sessionStart.toISOString() : null,
          detectionAttempts: detectionAttempts || 0
        });
      } catch (error) {
        sendResponse({
          isMonitoring: false,
          adCount: 0,
          sessionStart: null,
          detectionAttempts: 0
        });
      }
      break;
      
    case 'getSpotifyTabs':
      getSpotifyTabs().then(tabs => {
        sendResponse({ tabs: Array.isArray(tabs) ? tabs : [] });
      }).catch(error => {
        sendResponse({ tabs: [] });
      });
      return true; // Keep message channel open for async response
      

      
    case 'spotifyDOMInfo':
      // Receive DOM information from content script
      if (request.spotifyInfo && request.adDetection) {
        const tabId = sender.tab?.id;
        if (tabId) {
          spotifyDOMInfo[tabId] = {
            ...request.spotifyInfo,
            adDetection: request.adDetection,
            timestamp: new Date().toISOString()
          };
          
          // Log DOM-based ad detection
          if (request.adDetection.isAd) {
          }
        }
      }
      sendResponse({ success: true });
      break;
  }
});

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
  // Extension started
});

chrome.runtime.onInstalled.addListener(() => {
  // Show welcome notification
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon48.png',
    title: '🎵 Spotify Ad Silencer Installed!',
    message: 'Click the extension icon to start blocking ads'
  });
}); 