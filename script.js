// Theme toggle functionality
const body = document.body;
const toggleBtn = document.getElementById('theme-toggle-btn');

function updateToggleIcon(theme) {
  toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Set initial theme (removed localStorage usage for Claude.ai compatibility)
let currentTheme = 'light';
body.setAttribute('data-theme', currentTheme);
updateToggleIcon(currentTheme);

// Toggle theme function
function toggleTheme() {
  currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
  body.setAttribute('data-theme', currentTheme);
  updateToggleIcon(currentTheme);
}

// Add click event listener to toggle button
if (toggleBtn) {
  toggleBtn.addEventListener('click', toggleTheme);
}

// Optional: Listen for system theme changes
if (window.matchMedia) {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  // Set initial theme based on system preference
  const systemTheme = mediaQuery.matches ? 'dark' : 'light';
  currentTheme = systemTheme;
  body.setAttribute('data-theme', currentTheme);
  updateToggleIcon(currentTheme);
}

// Pipeline processing functionality
const processBtn = document.getElementById('process-btn');
const finalOutput = document.getElementById('final-output');
const ctFileInput = document.getElementById('ct-file');
const dotFileInput = document.getElementById('dot-file');
const ctStatus = document.getElementById('ct-status');
const dotStatus = document.getElementById('dot-status');

// Track upload status
let filesUploaded = {
  ct: false,
  dot: false
};

// File upload handlers with null checks
if (ctFileInput) {
  ctFileInput.addEventListener('change', handleFileUpload);
}
if (dotFileInput) {
  dotFileInput.addEventListener('change', handleFileUpload);
}

async function handleFileUpload(event) {
  const file = event.target.files[0];
  const isCtFile = event.target.id === 'ct-file';
  const fileType = isCtFile ? 'ct' : 'dot';
  const statusElement = isCtFile ? ctStatus : dotStatus;

  if (!statusElement) {
    console.error('Status element not found');
    return;
  }

  if (!file) {
    statusElement.textContent = '';
    statusElement.className = 'upload-status';
    filesUploaded[fileType] = false;
    updateProcessButtonState();
    return;
  }

  // Validate file extension
  const expectedExtension = `.${fileType}`;
  if (!file.name.toLowerCase().endsWith
