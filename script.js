async function loadResults() {
  try {
    const res = await fetch('/get_predictions');
    if (!res.ok) {
      console.error('Failed to fetch predictions:', res.status);
      return;
    }
    
    const data = await res.json();
    
    // Check if data is valid
    if (!data || data.error || !Array.isArray(data)) {
      console.error('Invalid data format:', data);
      return;
    }

    // Build table
    const container = document.getElementById('table-container');
    container.innerHTML = '';
    
    if (data.length === 0) {
      container.textContent = 'No predictions available';
      return;
    }

    const table = document.createElement('table');

    // Create header row
    const headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(col => {
      const th = document.createElement('th');
      th.textContent = col;
      headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Create data rows
    data.forEach(row => {
      const tr = document.createElement('tr');
      Object.values(row).forEach(val => {
        const td = document.createElement('td');
        td.textContent = val !== null && val !== undefined ? val : '';
        tr.appendChild(td);
      });
      table.appendChild(tr);
    });

    container.appendChild(table);

    // Refresh histogram with cache buster
    const histogram = document.getElementById('histogram');
    if (histogram) {
      histogram.src = `/static/histogram.png?cachebuster=${Date.now()}`;
      histogram.onerror = function() {
        this.style.display = 'none';
      };
    }

  } catch (error) {
    console.error('Error loading results:', error);
  }
}
