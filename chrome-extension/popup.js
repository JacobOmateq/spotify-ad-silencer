// Popup JavaScript for Spotify Ad Silencer Extension
let isMonitoring = false;
let adCount = 0;
let sessionStart = null;

// DOM elements
const toggleBtn = document.getElementById('toggle-btn');
const statusCircle = document.getElementById('status-circle');
const statusTitle = document.getElementById('status-title');
const currentTrack = document.getElementById('current-track');
const statusBadge = document.getElementById('status-badge');
const adsBlocked = document.getElementById('ads-blocked');
const uptime = document.getElementById('uptime');
const detectionAttempts = document.getElementById('detection-attempts');
const spotifyTabs = document.getElementById('spotify-tabs');
const tabsList = document.getElementById('tabs-list');



// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  // Wait a bit for background script to initialize
  await new Promise(resolve => setTimeout(resolve, 100));
  
  await updateStatus();
  setupEventListeners();
  
  // Update every 2 seconds
  setInterval(updateStatus, 2000);
});

// Setup event listeners
function setupEventListeners() {
  // Main toggle button
  if (toggleBtn) {
    toggleBtn.addEventListener('click', async () => {
      if (isMonitoring) {
        await chrome.runtime.sendMessage({ action: 'stopMonitoring' });
      } else {
        await chrome.runtime.sendMessage({ action: 'startMonitoring' });
      }
      await updateStatus();
    });
  }
  

}



// Update main status
async function updateStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
    const tabsResponse = await chrome.runtime.sendMessage({ action: 'getSpotifyTabs' });
    
    if (!response || typeof response !== 'object') {
      updateErrorState();
      return;
    }
    
    isMonitoring = response.isMonitoring || false;
    adCount = response.adCount || 0;
    sessionStart = response.sessionStart ? new Date(response.sessionStart) : null;
    
    // Update UI elements
    updateToggleButton();
    updateStatusDisplay((tabsResponse && tabsResponse.tabs) ? tabsResponse.tabs : []);
    updateStats(response);
    updateSpotifyTabs((tabsResponse && tabsResponse.tabs) ? tabsResponse.tabs : []);
    
  } catch (error) {
    console.error('Error updating status:', error);
    updateErrorState();
  }
}

// Update toggle button
function updateToggleButton() {
  if (!toggleBtn || !statusCircle || !statusTitle || !statusBadge || !currentTrack || !adsBlocked || !uptime) return; // Null checks
  
  if (isMonitoring) {
    toggleBtn.textContent = '⏹️ Stop Monitoring';
    toggleBtn.classList.add('monitoring');
    statusCircle.textContent = '🎵';
    statusCircle.classList.add('connected', 'monitoring');
    statusTitle.textContent = 'Monitoring Active';
    statusBadge.textContent = '🔍 Watching for ads';
    statusBadge.className = 'status-badge monitoring';
  } else {
    toggleBtn.textContent = '▶️ Start Monitoring';
    toggleBtn.classList.remove('monitoring');
    statusCircle.textContent = '⚫';
    statusCircle.classList.remove('connected', 'monitoring');
    statusTitle.textContent = 'Not Monitoring';
    statusBadge.textContent = '🎵 Ready';
    statusBadge.className = 'status-badge ready';
    currentTrack.textContent = 'Click start to begin';
  }
  
  // Update stats
  adsBlocked.textContent = `${adCount} ads blocked`;
  
  if (sessionStart) {
    const uptimeSeconds = Math.floor((new Date() - new Date(sessionStart)) / 1000);
    uptime.textContent = formatUptime(uptimeSeconds);
  } else {
    uptime.textContent = '0s uptime';
  }
}

// Format uptime display
function formatUptime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m uptime`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s uptime`;
  } else {
    return `${secs}s uptime`;
  }
}

// Update status display
function updateStatusDisplay(tabs) {
  if (!statusCircle || !statusTitle || !currentTrack || !statusBadge) return; // Null checks
  
  const hasSpotifyTabs = tabs.length > 0;
  const currentTab = tabs.find(tab => !tab.mutedInfo?.muted) || tabs[0];
  
  if (isMonitoring) {
    statusCircle.textContent = '🎵';
    statusCircle.classList.add('monitoring');
    statusTitle.textContent = 'Monitoring Active';
    
    if (hasSpotifyTabs) {
      const mutedTabs = tabs.filter(tab => tab.mutedInfo?.muted);
      if (mutedTabs.length > 0) {
        currentTrack.textContent = `${mutedTabs.length} ad(s) blocked`;
        statusBadge.textContent = '🔇 Blocking Ads';
        statusBadge.className = 'status-badge ad';
      } else if (currentTab) {
        currentTrack.textContent = currentTab.title.replace(/^Spotify\s*-\s*/, '') || 'Playing music';
        statusBadge.textContent = '🎵 Music Playing';
        statusBadge.className = 'status-badge ready';
      }
    } else {
      currentTrack.textContent = 'No Spotify tabs found';
      statusBadge.textContent = '⚠️ No Spotify';
      statusBadge.className = 'status-badge monitoring';
    }
  } else {
    statusCircle.textContent = hasSpotifyTabs ? '🎵' : '⚫';
    statusCircle.classList.remove('monitoring');
    statusCircle.classList.toggle('connected', hasSpotifyTabs);
    
    statusTitle.textContent = hasSpotifyTabs ? 'Spotify Connected' : 'Not Monitoring';
    currentTrack.textContent = hasSpotifyTabs ? 
      (currentTab?.title.replace(/^Spotify\s*-\s*/, '') || 'Ready to monitor') : 
      'Open Spotify to begin';
    
    statusBadge.textContent = '🎵 Ready';
    statusBadge.className = 'status-badge ready';
  }
}

// Update stats
function updateStats(response) {
  if (!adsBlocked || !detectionAttempts || !uptime) return; // Null checks
  
  adsBlocked.textContent = `${response.adCount || 0} ads blocked`;
  detectionAttempts.textContent = `${response.detectionAttempts || 0} attempts`;
  
  if (sessionStart) {
    const now = new Date();
    const uptimeSeconds = Math.floor((now - sessionStart) / 1000);
    const minutes = Math.floor(uptimeSeconds / 60);
    const seconds = uptimeSeconds % 60;
    uptime.textContent = minutes > 0 ? `${minutes}m ${seconds}s uptime` : `${seconds}s uptime`;
  } else {
    uptime.textContent = '0s uptime';
  }
}

// Update Spotify tabs list
function updateSpotifyTabs(tabs) {
  if (!spotifyTabs || !tabsList) return; // Null checks
  
  if (tabs.length > 0) {
    spotifyTabs.style.display = 'block';
    tabsList.innerHTML = tabs.map(tab => `
      <div class="tab-item">
        <div class="tab-title">
          ${tab.mutedInfo?.muted ? '🔇' : '🎵'} ${tab.title || 'Untitled Tab'}
        </div>
      </div>
    `).join('');
  } else {
    spotifyTabs.style.display = 'none';
  }
}





// Update error state
function updateErrorState() {
  if (!statusTitle || !currentTrack || !statusBadge) return; // Null checks
  
  statusTitle.textContent = 'Extension Error';
  currentTrack.textContent = 'Please reload the extension';
  statusBadge.textContent = '❌ Error';
  statusBadge.className = 'status-badge ad';
}



// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'adDetected':
      updateStatus();
      break;
    case 'adEnded':
      updateStatus();
      break;
  }
}); 