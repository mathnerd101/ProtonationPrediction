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
  const step2Result = document.getElementById('step2-result'); // Added reference to step 2 container

  try {
    // Clear previous results and set loading states
    finalOutput.innerHTML = '<div class="loading-spinner"></div><p>Processing data...</p>';
    step2Result.innerHTML = '<div class="status-loading">Starting pipeline analysis...</div>';
    processBtn.disabled = true;
    processBtn.textContent = 'Processing...';

    // Make the API call with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

    const response = await fetch('/run-pipeline', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId); // Clear timeout if request completes

    // Handle HTTP errors
    if (!response.ok) {
      let errorDetails = '';
      try {
        const errorData = await response.json();
        errorDetails = errorData.error || errorData.message || 'Unknown error';
      } catch {
        errorDetails = await response.text();
      }
      throw new Error(`Server responded with ${response.status}: ${errorDetails.slice(0, 200)}`);
    }

    // Process successful response
    const data = await response.json();
    
    // Validate response structure
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid server response format');
    }

    // Update UI based on response type
    if (data.error) {
      step2Result.innerHTML = `
        <div class="status-error">
          <h4>Pipeline Error</h4>
          <p>${data.error}</p>
          ${data.details ? `<pre class="error-details">${data.details}</pre>` : ''}
        </div>
      `;
      finalOutput.textContent = 'Processing failed - see step 2 for details';
    } 
    else if (data.result) {
      // Successful processing - update both step 2 and final output
      step2Result.innerHTML = `
        <div class="status-success">
          <h4>Analysis Complete</h4>
          <p>Successfully processed ${data.rowCount || 'all'} rows</p>
          <p class="timestamp">Completed at ${new Date().toLocaleTimeString()}</p>
        </div>
      `;

      // Enhanced table display with export options
      finalOutput.innerHTML = `
        <div class="output-controls">
          <button class="export-btn" onclick="exportToCSV(this)">
            <i class="fas fa-file-csv"></i> Export CSV
          </button>
          <button class="export-btn" onclick="exportToExcel(this)">
            <i class="fas fa-file-excel"></i> Export Excel
          </button>
        </div>
        <div class="table-container scrollable-table">
          ${data.result}
        </div>
        <div class="df-stats">
          ${data.stats ? `<pre>${JSON.stringify(data.stats, null, 2)}</pre>` : ''}
        </div>
      `;
    }
    else {
      throw new Error('Response missing expected data fields');
    }

  } catch (error) {
    console.error('Pipeline error:', error);
    
    // User-friendly error display
    const errorMessage = error.name === 'AbortError' 
      ? 'Request timed out (30s) - try with smaller dataset'
      : error.message;

    step2Result.innerHTML = `
      <div class="status-error">
        <h4>Pipeline Failed</h4>
        <p>${errorMessage}</p>
        <button class="retry-btn" onclick="runPipeline()">Retry</button>
      </div>
    `;
    
    finalOutput.innerHTML = `
      <div class="error-display">
        <i class="fas fa-exclamation-triangle"></i>
        <p>${errorMessage}</p>
        ${error.stack ? `<details><summary>Technical details</summary><pre>${error.stack}</pre></details>` : ''}
      </div>
    `;
    
  } finally {
    processBtn.disabled = false;
    processBtn.textContent = 'Run Pipeline Again';
    // Add visual completion indicator
    processBtn.classList.add('completed');
    setTimeout(() => processBtn.classList.remove('completed'), 2000);
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











