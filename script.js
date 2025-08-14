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
function displayResult(data) {
    const output = document.getElementById('final-output');
    
    if (data.type === 'dataframe') {
        // For HTML tables
        output.innerHTML = `
            <div class="table-container">
                ${data.result}
            </div>
            <div class="df-info">
                Showing all ${data.result.split('<tr>').length - 2} rows
            </div>
        `;
    } else {
        // For regular text output
        output.textContent = data.result;
    }
}
async function runPipeline() {
  const processBtn = document.getElementById('process-btn');
  const finalOutput = document.getElementById('final-output');
  const step2Result = document.getElementById('step2-result');

  try {
    // Set loading states
    finalOutput.innerHTML = '<div class="loading">Processing data...</div>';
    step2Result.innerHTML = '<div class="status-loading">Starting analysis...</div>';
    processBtn.disabled = true;
    processBtn.textContent = 'Processing...';

    // API call with timeout protection
    const response = await fetch('/run-pipeline', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Handle HTTP errors
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error: ${response.status} - ${errorText.slice(0, 500)}`);
    }

    // Process successful response
    const data = await response.json();
    
    if (!data) {
      throw new Error('No data received from server');
    }

    // Error case
    if (data.error) {
      step2Result.innerHTML = `
        <div class="status-error">
          <p>Error: ${data.error}</p>
        </div>
      `;
      finalOutput.textContent = 'Processing failed';
    } 
    // Success case
    else if (data.result) {
      step2Result.innerHTML = `
        <div class="status-success">
          <p>Analysis completed successfully</p>
        </div>
      `;
      
      finalOutput.innerHTML = `
        <div class="table-container">
          ${data.result}
        </div>
        <div class="df-info">
          Showing all data rows
        </div>
      `;
    }
    // Unexpected format
    else {
      throw new Error('Unexpected response format');
    }

  } catch (error) {
    console.error('Pipeline error:', error);
    step2Result.innerHTML = `
      <div class="status-error">
        <p>Error: ${error.message}</p>
      </div>
    `;
    finalOutput.textContent = `Error: ${error.message}`;
  } finally {
    processBtn.disabled = false;
    processBtn.textContent = 'Run Pipeline Again';
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












