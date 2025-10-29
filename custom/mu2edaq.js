//-----------------------------------------------------------------------------
// common javascript functions
// DAQ colors. Each element has 'Enabled' and 'Status' field
//-----------------------------------------------------------------------------
function set_colors(path, statusCell) {
  // Fetch values for Enabled and Status
  const path_enabled = path+`/Enabled`;
  const path_status  = path+`/Status`;
  mjsonrpc_db_get_values([path_enabled, path_status]).then(function (rpc) {
    let enabled = rpc.result.data[0];
    let status = rpc.result.data[1];
    
    // Apply color styles
    if (enabled === 0) {
      statusCell.style.backgroundColor = "gray";
      statusCell.style.color = "white";
    } else if (enabled === 1) {
      if (status === 0) {
        statusCell.style.backgroundColor = "green";
        statusCell.style.color = "white";
      } else if (status < 0) {
        statusCell.style.backgroundColor = "red";
        statusCell.style.color = "white";
      } else if (status > 0) {
        statusCell.style.backgroundColor = "yellow";
        statusCell.style.color = "black";
      }
    } else {
      statusCell.style.backgroundColor = "gray";
      statusCell.style.color = "white";
    }
  }).catch(function (error) {
    console.error("Error fetching values:", error);
  });
}

//-----------------------------------------------------------------------------
// clear output window
//-----------------------------------------------------------------------------
function clear_window(element_id) {
  const el = document.getElementById(element_id);
  el.innerHTML = '';
  el.classList.toggle('force-redraw');
}

//-----------------------------------------------------------------------------
function displayFile_old(filePath, elementId) {
//  // const fs = require('fs');
//  try {
//    const response = await fetch(filePath);
//    if (!response.ok) {
//      throw new Error(`HTTP error! status: ${response.status}`);
//    }
//    const text = await response.text();
//    document.getElementById(elementId).textContent = text;
//  } catch (error) {
//    document.getElementById(elementId).textContent = 'Error: ' + error.message;
  //  }

  var result = null;
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET", filePath, false);
  xmlhttp.send();
  if (xmlhttp.status==200) {
    document.getElementById(elementId).textContent = xmlhttp.responseText;
  }
  return result;
}

//-----------------------------------------------------------------------------
function displayFile(filePath, elementId) {

  var result = null;
  fetch(filePath)
    .then(response => response.text())
    .then(text => {
      document.getElementById(elementId).textContent = text;
    })
    .catch(err => {
      console.error("Error loading file:", err);
    });
  
  return result;
}

//-----------------------------------------------------------------------------
// redirects browser to the DTC control page
// may need to decide which particular DTC type
//-----------------------------------------------------------------------------
function dtc_control(hostname,pcie) {
  window.location.href = `dtc_control.html?hostname=${hostname}&pcie=${pcie}`;
}

//-----------------------------------------------------------------------------
// redirects browser to the ARTDAQ process control page
//-----------------------------------------------------------------------------
function artdaq_process_control(hostname,process) {
  window.location.href = `artdaq_process_control.html?hostname=${hostname}&process=${process}`;
}

//-----------------------------------------------------------------------------
// redirects to the node page
//-----------------------------------------------------------------------------
function node_control(hostname) {
  window.location.href = `node_control.html?hostname=${hostname}`;
}

//-----------------------------------------------------------------------------
// redirects to the TFM page
//-----------------------------------------------------------------------------
function tfm_control(hostname) {
  window.location.href = `tfm_control.html?hostname=${hostname}&facility=tfm`;
}

//-----------------------------------------------------------------------------
// redirects to the CFO page
//-----------------------------------------------------------------------------
function cfo_status(hostname) {
  window.location.href = `cfo_status.html`;
}

//-----------------------------------------------------------------------------
async function fetch_url(url, divId) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const html = await response.text();
    document.getElementById(divId).innerHTML = html;
  } catch (error) {
    console.error("Failed to load page:", error);
    document.getElementById(divId).innerHTML = "<p>Failed to load content.</p>";
  }
}

//-----------------------------------------------------------------------------
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// emacs
// Local Variables:
// mode: web
// End:
