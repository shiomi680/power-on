/**
 * Power On Web UI - Frontend Application Logic
 */

// Configuration
const API_BASE_URL = window.location.origin;
const STATUS_POLL_INTERVAL = 2000; // 2 seconds

// DOM Elements
const powerOnBtn = document.getElementById('powerOnBtn');
const powerOffBtn = document.getElementById('powerOffBtn');
const messageBox = document.getElementById('messageBox');
const loadingSpinner = document.getElementById('loadingSpinner');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.querySelector('.status-text');
const statusTimestamp = document.getElementById('statusTimestamp');

// State
let statusPollTimer = null;
let isLoading = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    startStatusPolling();
    showMessage('システムが起動しました', 'info');
});

/**
 * Setup event listeners for buttons
 */
function setupEventListeners() {
    powerOnBtn.addEventListener('click', () => handlePowerOn());
    powerOffBtn.addEventListener('click', () => handlePowerOff());
}

/**
 * Handle Power ON button click
 */
async function handlePowerOn() {
    if (isLoading) return;

    try {
        isLoading = true;
        showLoading(true);
        clearMessage();

        // Send power on request to API
        const response = await fetch(`${API_BASE_URL}/api/power/on`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_mac: getTargetMac()
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'パケット送信に失敗しました');
        }

        const data = await response.json();
        showMessage('WOL パケットを送信しました。PC をお待ちください...', 'success');

        // Update status after a delay
        setTimeout(() => pollStatus(), 2000);

    } catch (error) {
        console.error('Power ON error:', error);
        showMessage(`エラー: ${error.message}`, 'error');
    } finally {
        isLoading = false;
        showLoading(false);
    }
}

/**
 * Handle Power OFF button click
 */
async function handlePowerOff() {
    if (isLoading) return;

    try {
        isLoading = true;
        showLoading(true);
        clearMessage();

        // Send shutdown request to API
        const response = await fetch(`${API_BASE_URL}/api/power/shutdown`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pc_address: getPcAddress(),
                timeout: 60
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'シャットダウンコマンド送信に失敗しました');
        }

        const data = await response.json();
        showMessage('シャットダウンコマンドを送信しました', 'success');

        // Update status after a delay
        setTimeout(() => pollStatus(), 2000);

    } catch (error) {
        console.error('Power OFF error:', error);
        showMessage(`エラー: ${error.message}`, 'error');
    } finally {
        isLoading = false;
        showLoading(false);
    }
}

/**
 * Start polling PC status at regular intervals
 */
function startStatusPolling() {
    // Initial poll
    pollStatus();

    // Set up interval polling
    statusPollTimer = setInterval(pollStatus, STATUS_POLL_INTERVAL);
}

/**
 * Poll PC status from API
 */
async function pollStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status`, {
            method: 'GET'
        });

        if (!response.ok) {
            updateStatusDisplay('unknown');
            return;
        }

        const data = await response.json();
        updateStatusDisplay(data.status, data.timestamp);

    } catch (error) {
        console.error('Status poll error:', error);
        updateStatusDisplay('unknown');
    }
}

/**
 * Update status display UI
 */
function updateStatusDisplay(status, timestamp = null) {
    const statusClass = status;
    const statusLabel = {
        'online': 'オンライン',
        'offline': 'オフライン',
        'unknown': '不明'
    }[status] || '不明';

    // Update indicator
    statusIndicator.className = `status-indicator`;
    const statusIcon = statusIndicator.querySelector('.status-icon');
    statusIcon.className = `status-icon ${statusClass}`;

    // Update status text
    statusText.textContent = statusLabel;

    // Update timestamp
    if (timestamp) {
        const date = new Date(timestamp);
        statusTimestamp.textContent = date.toLocaleTimeString('ja-JP');
    }

    // Enable/disable buttons based on status
    powerOnBtn.disabled = (status === 'online');
    powerOffBtn.disabled = (status !== 'online');
}

/**
 * Show message to user
 */
function showMessage(text, type = 'info') {
    messageBox.textContent = text;
    messageBox.className = `message-box show ${type}`;
}

/**
 * Clear message display
 */
function clearMessage() {
    messageBox.className = 'message-box';
    messageBox.textContent = '';
}

/**
 * Show/hide loading spinner
 */
function showLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('hidden');
    } else {
        loadingSpinner.classList.add('hidden');
    }
}

/**
 * Get target PC MAC address
 * Can be configured via environment or stored in localStorage
 */
function getTargetMac() {
    // Try to get from localStorage first
    const stored = localStorage.getItem('targetMac');
    if (stored) return stored;

    // Default fallback - should be configured
    return 'aa:bb:cc:dd:ee:ff';
}

/**
 * Get PC IP address
 * Can be configured via environment or stored in localStorage
 */
function getPcAddress() {
    // Try to get from localStorage first
    const stored = localStorage.getItem('pcAddress');
    if (stored) return stored;

    // Default fallback - should be configured
    return '192.168.1.100';
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (statusPollTimer) {
        clearInterval(statusPollTimer);
    }
});
