// Theme toggle functionality
const body = document.body;
const toggleBtn = document.getElementById('theme-toggle-btn');

function updateToggleIcon(theme) {
  toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Set initial theme
const savedTheme = localStorage.getItem('theme') || 'light';
body.setAttribute('data-theme', savedTheme);
updateToggleIcon(savedTheme);

// Toggle theme function
function toggleTheme() {
  const currentTheme = body.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  body.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateToggleIcon(newTheme);
}

// Add click event listener to toggle button
if (toggleBtn) {
  toggleBtn.addEventListener('click', toggleTheme);
}

// Optional: Listen for system theme changes
if (window.matchMedia) {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  // Set initial theme based on system preference if no saved preference
  if (!localStorage.getItem('theme')) {
    const systemTheme = mediaQuery.matches ? 'dark' : 'light';
    body.setAttribute('data-theme', systemTheme);
    updateToggleIcon(systemTheme);
  }
}

// Pipeline processing functionality
const processBtn = document.getElementById('process-btn');
const finalOutput = document.getElementById('final-output');
const ctFileInput = document.getElementById('ct-file');
const dotFileInput = document.getElementById('dot-file');
const ctStatus = document.getElementById('ct-status');
const dotStatus = document.getElementById('dot-status');

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
  const statusElement = isCtFile ? ctStatus : dotStatus;

  if (!statusElement) {
    console.error('Status element not found');
    return;
  }

  if (!file) {
    statusElement.textContent = '';
    statusElement.className = 'upload-status';
    return;
  }

  // Validate file extension
  const expectedExtension = isCtFile ? '.ct' : '.dot';
  if (!file.name.toLowerCase().endsWith(expectedExtension)) {
    statusElement.textContent = `Invalid file type. Expected ${expectedExtension}`;
    statusElement.className = 'upload-status error';
    event.target.value = '';
    return;
  }

  // Upload file
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', isCtFile ? 'ct' : 'dot');

  try {
    statusElement.textContent = 'Uploading...';
    statusElement.className = 'upload-status';

    const response = await fetch('/upload-file', {
      method: 'POST',
      body: formData
    });

    if (response.ok) {
      statusElement.textContent = 'Uploaded successfully';
      statusElement.className = 'upload-status success';
    } else {
      const error = await response.text();
      statusElement.textContent = `Upload failed: ${error}`;
      statusElement.className = 'upload-status error';
    }
  } catch (error) {
    statusElement.textContent = `Upload error: ${error.message}`;
    statusElement.className = 'upload-status error';
  }
}

async function runPipeline() {

  // Disable button and show loading
  processBtn.disabled = true;
  processBtn.textContent = 'Processing...';

  // Clear previous results
  clearResults();

  try {
    // Call the Python pipeline
    const response = await fetch('/run-pipeline', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Update step results (only showing steps 3 and 4, renumbered as 1 and 2)
    document.getElementById('step3-result').textContent = data.step3 || 'Processing...';
    await sleep(300);

    document.getElementById('step4-result').textContent = data.step4 || 'Processing...';

    // Display final result
    if (data.result) {
      finalOutput.textContent = data.result;
    } else if (data.error) {
      finalOutput.textContent = `Error: ${data.error}`;
    }

  } catch (error) {
    console.error('Pipeline error:', error);
    finalOutput.textContent = `Error: ${error.message}`;
  } finally {
    // Re-enable button
    processBtn.disabled = false;
    processBtn.textContent = 'Process Through Pipeline';
  }
}

function clearResults() {
  document.getElementById('step3-result').textContent = '';
  document.getElementById('step4-result').textContent = '';
  finalOutput.textContent = '';
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Add event listener to process button with null check
if (processBtn) {
  processBtn.addEventListener('click', runPipeline);
}
