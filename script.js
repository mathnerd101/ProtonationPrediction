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

// Pipeline processing functionality
const processBtn = document.getElementById('process-btn');
const finalOutput = document.getElementById('final-output');
const ctFileInput = document.getElementById('ct-file');
const dotFileInput = document.getElementById('dot-file');
const ctStatus = document.getElementById('ct-status');
const dotStatus = document.getElementById('dot-status');

// File upload handlers
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

  if (!statusElement) return;

  if (!file) {
    statusElement.textContent = '';
    statusElement.className = 'upload-status';
    return;
  }

  const expectedExtension = isCtFile ? '.ct' : '.dot';
  if (!file.name.toLowerCase().endsWith(expectedExtension)) {
    statusElement.textContent = `Invalid file type. Expected ${expectedExtension}`;
    statusElement.className = 'upload-status error';
    event.target.value = '';
    return;
  }

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
  processBtn.disabled = true;
  processBtn.textContent = 'Processing...';
  finalOutput.textContent = '';

  try {
    const response = await fetch('/run-pipeline', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });

    // First check if response is JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text();
      throw new Error(`Server returned ${response.status}: ${text.slice(0, 100)}`);
    }

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || `Pipeline failed (${response.status})`);
    }

    // Update UI
    document.getElementById('step3-result').textContent = data.step3 || 'Step 3 completed';
    await sleep(500);
    document.getElementById('step4-result').textContent = data.step4 || 'Step 4 completed';
    await sleep(500);
    finalOutput.textContent = data.result || 'No result returned';

  } catch (error) {
    console.error('Pipeline error:', error);
    finalOutput.textContent = `Error: ${error.message}`;
    
    // Additional error logging
    if (error.response) {
      error.response.text().then(text => console.error('Full error:', text));
    }
  } finally {
    processBtn.disabled = false;
    processBtn.textContent = 'Process Through Pipeline';
  }
}

function clearResults(data) {
  document.getElementById('step3-result').textContent = data.step3 || 'Processing...';
  document.getElementById('step4-result').textContent = data.step4 || 'Processing...';
  finalOutput.textContent = data.result;
  finalOutput.textContent = '';
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

if (processBtn) {
  processBtn.addEventListener('click', runPipeline);
}







