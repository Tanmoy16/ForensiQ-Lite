// ========================================
// ForensiQ-Lite - Enhanced Script
// ========================================

let filesToUpload = [];
let currentFilter = 'all';

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const fileCount = document.getElementById('fileCount');
const analyzeBtn = document.getElementById('analyzeBtn');

// ========================================
// FILE SELECTION LOGIC
// ========================================

// Click to browse
dropZone.addEventListener('click', () => fileInput.click());

// Drag & Drop Visual Feedback
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

// Manual File Selection
fileInput.addEventListener('change', () => {
    handleFiles(fileInput.files);
    fileInput.value = ''; // Reset for re-selection
});

// Process Selected Files
function handleFiles(files) {
    if (!files || files.length === 0) return;

    Array.from(files).forEach(file => {
        // Prevent duplicates
        if (!filesToUpload.some(f => f.name === file.name && f.size === file.size)) {
            filesToUpload.push(file);
            console.log(`✓ Added: ${file.name} (${formatFileSize(file.size)})`);
        } else {
            console.log(`⚠ Duplicate skipped: ${file.name}`);
        }
    });

    updateUI();
    showNotification('Files added successfully', 'success');
}

// Update UI Elements
function updateUI() {
    // Clear existing list
    fileList.innerHTML = '';
    
    // Render each file
    filesToUpload.forEach((file, index) => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <span>
                <i class="fas fa-file-code"></i>
                <span class="file-name">${file.name}</span>
            </span>
            <i class="fas fa-times remove" onclick="removeFile(${index})" title="Remove file"></i>
        `;
        fileList.appendChild(div);
    });

    // Update file count badge
    fileCount.textContent = `${filesToUpload.length} file${filesToUpload.length !== 1 ? 's' : ''}`;
    
    // Enable/disable analyze button
    analyzeBtn.disabled = filesToUpload.length === 0;
    
    // Update drop zone styling
    if (filesToUpload.length > 0) {
        dropZone.style.borderColor = 'var(--accent-primary)';
    } else {
        dropZone.style.borderColor = 'var(--border-primary)';
    }
}

// Remove File from Queue
window.removeFile = function(index) {
    const removedFile = filesToUpload[index];
    filesToUpload.splice(index, 1);
    updateUI();
    console.log(`✗ Removed: ${removedFile.name}`);
}

// ========================================
// ANALYSIS & UPLOAD LOGIC
// ========================================

analyzeBtn.addEventListener('click', async () => {
    if (filesToUpload.length === 0) {
        showNotification('No files selected for analysis', 'error');
        return;
    }

    console.log(`🔍 Starting analysis of ${filesToUpload.length} file(s)...`);

    // Set loading state
    setLoadingState(true);

    // Build FormData
    const formData = new FormData();
    filesToUpload.forEach(file => {
        formData.append('evidence_files', file);
    });

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || 'Analysis failed');
        }

        console.log('✓ Analysis complete:', data);

        // Render results
        renderReport(data.report || 'No report generated');
        renderTimeline(data.timeline || []);
        
        // Set analysis timestamp
        const timestamp = new Date().toLocaleString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        document.getElementById('analysisTime').textContent = `Completed on ${timestamp}`;
        
        // Switch to results view
        switchView('results');
        showNotification('Analysis completed successfully', 'success');

    } catch (error) {
        console.error('❌ Analysis error:', error);
        showNotification(error.message || 'Analysis failed. Please try again.', 'error');
    } finally {
        setLoadingState(false);
    }
});

// Set Button Loading State
function setLoadingState(isLoading) {
    if (isLoading) {
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';
        analyzeBtn.disabled = true;
    } else {
        analyzeBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i><span>Start Analysis</span>';
        analyzeBtn.disabled = filesToUpload.length === 0;
    }
}

// ========================================
// RENDERING FUNCTIONS
// ========================================

// Render AI Report
function renderReport(text) {
    const reportContent = document.getElementById('reportContent');
    reportContent.innerHTML = '';
    
    // Create formatted report
    const pre = document.createElement('pre');
    pre.style.margin = '0';
    pre.style.whiteSpace = 'pre-wrap';
    pre.style.wordWrap = 'break-word';
    pre.textContent = text;
    
    reportContent.appendChild(pre);
}

// Render Timeline Events
function renderTimeline(events) {
    const feed = document.getElementById('timelineFeed');
    feed.innerHTML = '';

    if (!events || events.length === 0) {
        feed.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">No events to display</p>';
        return;
    }

    events.forEach(event => {
        const div = document.createElement('div');
        div.className = 'event-card';
        div.dataset.source = event.source.toLowerCase();

        // Determine event styling based on source
        const { color, icon } = getEventStyle(event.source);
        
        div.style.borderLeftColor = color;
        
        div.innerHTML = `
            <div class="event-time">${escapeHtml(event.timestamp)}</div>
            <div class="event-desc">
                <span class="tag" style="color:${color}; border-color:${color};">
                    <i class="${icon}"></i> ${escapeHtml(event.source.toUpperCase())}
                </span>
                <span>${escapeHtml(event.description)}</span>
            </div>
        `;
        feed.appendChild(div);
    });

    // Setup filter buttons
    setupTimelineFilters();
}

// Get Event Styling
function getEventStyle(source) {
    const sourceLower = source.toLowerCase();
    
    if (sourceLower.includes('auth')) {
        return { color: '#ef4444', icon: 'fas fa-shield-halved' };
    } else if (sourceLower.includes('browser')) {
        return { color: '#10b981', icon: 'fab fa-chrome' };
    } else if (sourceLower.includes('file')) {
        return { color: '#f59e0b', icon: 'fas fa-folder-open' };
    } else if (sourceLower.includes('network')) {
        return { color: '#3b82f6', icon: 'fas fa-network-wired' };
    } else {
        return { color: '#6366f1', icon: 'fas fa-circle-info' };
    }
}

// Setup Timeline Filters
function setupTimelineFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Apply filter
            const filter = btn.dataset.filter;
            currentFilter = filter;
            applyTimelineFilter(filter);
        });
    });
}

// Apply Timeline Filter
function applyTimelineFilter(filter) {
    const eventCards = document.querySelectorAll('.event-card');
    
    eventCards.forEach(card => {
        if (filter === 'all') {
            card.style.display = 'block';
        } else {
            const source = card.dataset.source || '';
            card.style.display = source.includes(filter) ? 'block' : 'none';
        }
    });
}

// ========================================
// VIEW SWITCHING
// ========================================

// Switch Between Welcome and Results
function switchView(view) {
    const welcomeScreen = document.getElementById('welcomeScreen');
    const resultsScreen = document.getElementById('resultsScreen');
    
    if (view === 'results') {
        welcomeScreen.classList.add('hidden');
        resultsScreen.classList.remove('hidden');
    } else {
        welcomeScreen.classList.remove('hidden');
        resultsScreen.classList.add('hidden');
    }
}

// Switch Tabs (Report/Timeline)
window.switchTab = function(tabName) {
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.remove('active');
    });
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('active');
    });
    
    const buttons = document.querySelectorAll('.tab-btn');
    if (tabName === 'report') {
        buttons[0].classList.add('active');
    } else {
        buttons[1].classList.add('active');
    }
}

// Reset to New Analysis
window.resetAnalysis = function() {
    // Clear files
    filesToUpload = [];
    updateUI();
    
    // Switch back to welcome screen
    switchView('welcome');
    
    // Reset to report tab
    switchTab('report');
    
    showNotification('Ready for new analysis', 'info');
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show Notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: var(--bg-elevated);
        border: 1px solid var(--border-primary);
        border-left: 4px solid var(--accent-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'});
        border-radius: var(--radius-md);
        color: var(--text-primary);
        font-size: 0.875rem;
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        max-width: 320px;
    `;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    notification.innerHTML = `
        <i class="fas ${icons[type]}" style="margin-right: 0.5rem;"></i>
        ${escapeHtml(message)}
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations to document
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ========================================
// INITIALIZATION
// ========================================

console.log('🚀 ForensiQ-Lite initialized');
console.log('📁 Ready to accept evidence files');