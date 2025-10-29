
// search messages
const date_regex = /(\d{2}):\d{2}:\d{2}\.\d+\s(\d{4}\/\d{2}\/\d{2})/;

let recentFilters = [];
let filteredMessages = [];
let unfilteredMessages = [];
let isFiltering = false;
let stoppedFiltering = false;
let filterTimeout;

function reset_background_color() {

   document.getElementById("loadingOverlay").style.display = "flex";
   document.getElementById("loadingOverlay").innerHTML = "Reseting colors...";

   // Loop through each child element and remove the background color
   filteredMessages.forEach(element => {
      element.style.backgroundColor = "";
   });
   filteredMessages = [];

   unfilteredMessages.forEach(element => {
      element.style.display = "";
   });
   unfilteredMessages = [];
   document.getElementById("loadingOverlay").style.display = "none";
   document.getElementById("loadingOverlay").innerHTML = "Searching messages... Mouse Click to stop.";

}

function reset() {
   // reset to default
   isFiltering = false;
   document.getElementById("loadingOverlay").style.display = "none";
}

// Initialize messagesByDay as a map of messages grouped by date
const messagesByDay = Array.from(document.querySelectorAll('#messageFrame p')).reduce((acc, message) => {
   const messageText = message.innerText;
   const dateMatch = date_regex.exec(messageText);

   if (dateMatch) {
      // Construct the date key in the format YYYY-MM-DD
      const dateKey = `${dateMatch[1]}`;

      // Initialize the array if it doesn't exist, then add the message
      if (!acc[dateKey]) {
         acc[dateKey] = [];
      }
      acc[dateKey].push(message);
   }

   return acc;
}, {});

// Update function for messagesByDay while new messages are coming in
function updateMessagesArray(mutationsList) {
   mutationsList.forEach(mutation => {
      if (mutation.type === 'childList') {
         // Process added nodes
         mutation.addedNodes.forEach(node => {
               if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'P') {
                  const messageText = node.innerText;
                  const dateMatch = date_regex.exec(messageText);

                  if (dateMatch) {
                     const dateKey = `${dateMatch[2]}` + "-" + `${dateMatch[1]}`; // Format: YYYY/MM/DD-h
                     // console.log(dateKey);
                     if (!messagesByDay[dateKey]) {
                           messagesByDay[dateKey] = [];
                     }
                     messagesByDay[dateKey].push(node);
                  }
               }
         });

         // Process removed nodes
         mutation.removedNodes.forEach(node => {
               if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'P') {
                  const messageText = node.innerText;
                  const dateMatch = date_regex.exec(messageText);

                  if (dateMatch) {
                     const dateKey = `${dateMatch[1]}`;
                     if (messagesByDay[dateKey]) {
                           messagesByDay[dateKey] = messagesByDay[dateKey].filter(msg => msg !== node);

                           // Clean up the date entry if no messages are left
                           if (messagesByDay[dateKey].length === 0) {
                              delete messagesByDay[dateKey];
                           }
                     }
                  }
               }
         });
      }
   });
}

// Set up the observer
const observer = new MutationObserver(updateMessagesArray);

// Target the message container
const messageFrame = document.getElementById('messageFrame');
if (messageFrame) {
   observer.observe(messageFrame, { childList: true, subtree: true });
}

// wrapper to reset the stoppedFiltering variable when we had an input
function applyFilter_input() {
   document.getElementById("messageFrame").className = "mmessagebox mfont";
   stoppedFiltering = false;
   reset();
   reset_background_color();
   applyFilter();
}

// Function to apply filters and manage the dynamic loading of new messages
function applyFilter() {

   const nameFilter = document.getElementById('nameFilter').value.trim();
   const typeFilter = document.getElementById('typeFilter').value.trim();
   const timeFilter = document.getElementById('timeFilter').value.trim();
   const textFilter = document.getElementById('textFilter').value.trim();
   const timeRangeFilter = document.getElementById('timeRangeFilter').value.trim();

   let counter = 0;

   // Check if any filter field has input
   const anyFilterActive = Boolean(nameFilter || typeFilter || timeFilter || textFilter);

   // console.log("LOG", anyFilterActive, !isFiltering, !stoppedFiltering);
   // stop if we have no filter or the filtering was stopped
   if ( stoppedFiltering ) {
      // console.log("Stopped filtering on start", stoppedFiltering, !anyFilterActive);
      reset();
      clearTimeout(filterTimeout);
      return;
   }

   if ( !anyFilterActive ) {
      reset();
      return;
   }

   // start the filtering if we are not filtering and no stop was triggered
   if (anyFilterActive && !isFiltering && !stoppedFiltering) {
      // console.log("Trigger turn on overlay start", !stoppedFiltering, anyFilterActive, !isFiltering);
      isFiltering = true;
      document.getElementById("loadingOverlay").style.display = "flex";
   }

   // Get the day of the earlist entries
   var keys = Object.keys(messagesByDay);
   const earlistDay = keys.sort()[keys.length-1];
   // revert keys to start with the earlist
   keys = keys.map((e, i, a)=> a[(a.length - 1) - i]);

   // console.log(keys.length);
   var filtered_keys = 0;
   for ( let i = 0; i < keys.length; i++ ) {
      if (
         (timeRangeFilter === "24 h" && i >= 24) ||
         (timeRangeFilter === "48 h" && i >= 48) ||
         (timeRangeFilter === "72 h" && i >= 72) ||
         (timeRangeFilter === "7 d" && i >= 7*24) ||
         (timeRangeFilter === "30 d" && i >= 30*24)
      ) {
         // console.log(i, keys.length);
         reset();
         break;
      }
      filtered_keys++;

      // cast to text to be faster with the matching later
      const messagesTextArray = messagesByDay[keys[i]].map(msg => msg.innerText || '');

      for ( let j = 0; j < messagesTextArray.length; j++) {
         counter++;

         const message = messagesByDay[keys[i]][j];
         if (!message) {
               // console.log("Empty message continue.");
               continue;
         }

         const messageText = messagesTextArray[j];
         if (!messageText) {
               // console.log("Empty string continue.");
               continue;
         }
         const dateMatch = messageText.match(date_regex);

         if (!dateMatch) {
               // console.log("Date not found in message.");
               continue;
         }

         // Regex to match the structure
         const regex = /(\d{2}:\d{2}:\d{2}\.\d{3}) (\d{4}\/\d{2}\/\d{2}) \[(.+?),(.+?)\] (.+)/;
         const match = messageText.match(regex);

         if (match) {
               const [fullMatch, time, date, name, state, text] = match;

               // Filters check
               const nameMatch = nameFilter ? name.includes(nameFilter) : true;
               const typeMatch = typeFilter ? state.includes(typeFilter) : true;
               const timeMatch = timeFilter ? time.startsWith(timeFilter) : true;
               const textMatch = textFilter ? text.toLowerCase().includes(textFilter.toLowerCase()) : true;

               // Display or hide the message based on filters
               if (nameMatch && typeMatch && timeMatch && textMatch) {
                  // for new messages we have to reset the transition and remove the age property
                  message.style.transition = "none";
                  message.style.webkitTransition = "none";
                  delete message.age;

                  if (!(message.style.display === "var(--mgreen)"))
                     filteredMessages.push(message);
                  message.style.backgroundColor = "var(--mgreen)";

               } else {
                  if (!(message.style.display === "none"))
                     unfilteredMessages.push(message);
                  message.style.display = "none";
               }
         }
      }
   }
   // console.log("Counters: ", counter, n_messages, keys.length, stoppedFiltering);

   // Store the current filter in the recent filters array
   const currentFilter = {
      name: nameFilter,
      type: typeFilter,
      time: timeFilter,
      text: textFilter,
      timeRange: timeRangeFilter
   };

   // Check if the current filter already exists in the recentFilters array
   const filterExists = recentFilters.some(filter =>
      filter.name === currentFilter.name &&
      filter.type === currentFilter.type &&
      filter.time === currentFilter.time &&
      filter.text === currentFilter.text &&
      filter.timeRange === currentFilter.timeRange
   );

   // Add the current filter only if it doesn't already exist
   if (!filterExists && Object.values(currentFilter).some(value => value !== "")) {
      recentFilters.push(currentFilter);
      updateRecentsDropdown();
   }

   if (
      (timeRangeFilter === "24 h" && filtered_keys >= 24) ||
      (timeRangeFilter === "48 h" && filtered_keys >= 48) ||
      (timeRangeFilter === "72 h" && filtered_keys >= 72) ||
      (timeRangeFilter === "7 d" && filtered_keys >= 7*24) ||
      (timeRangeFilter === "30 d" && filtered_keys >= 30*24) ||
      stoppedFiltering
   ) {
      // console.log(keys.length, filtered_keys, keys);
      reset();
      return;
   } else {
      // console.log("Trigger turn on overlay");
      document.getElementById("loadingOverlay").style.display = "flex";
      filterTimeout = setTimeout(applyFilter, 1000); // Retry after 1 second
   }

}

// Function to stop filtering and reset
function stopFiltering() {
   clearTimeout(filterTimeout);
   isFiltering = false;
   stoppedFiltering = true;
   // console.log("Trigger stop");
   document.getElementById("loadingOverlay").style.display = "none";
}

function updateRecentsDropdown() {
   const dropdown = document.getElementById('recentsDropdown');
   dropdown.innerHTML = '<option value="">Select a recent filter</option>';

   recentFilters.forEach((filter, index) => {
      const option = document.createElement('option');
      option.value = index;
      option.text = `Name: ${filter.name || 'N/A'}, Type: ${filter.type || 'N/A'}, Time: ${filter.time || 'N/A'}, Text: ${filter.text || 'N/A'}, TimeRange: ${filter.timeRange || 'N/A'}`;
      dropdown.appendChild(option);
   });
}

function add_filter() {
   const selectedFilterIndex = this.value;

   if (selectedFilterIndex !== "") {
      const selectedFilter = recentFilters[selectedFilterIndex];
      document.getElementById('nameFilter').value = selectedFilter.name;
      document.getElementById('typeFilter').value = selectedFilter.type;
      document.getElementById('timeFilter').value = selectedFilter.time;
      document.getElementById('textFilter').value = selectedFilter.text;
      document.getElementById('timeRangeFilter').value = selectedFilter.timeRange;
      applyFilter();
   }
}

function grey_table() {
   document.getElementById("messageFrame").className = "mmessagebox mfont grayout";

   // if there is no filter active we just show all messages
   const nameFilter = document.getElementById('nameFilter').value.trim();
   const typeFilter = document.getElementById('typeFilter').value.trim();
   const timeFilter = document.getElementById('timeFilter').value.trim();
   const textFilter = document.getElementById('textFilter').value.trim();
   const anyFilterActive = Boolean(nameFilter || typeFilter || timeFilter || textFilter);

   if (!anyFilterActive) {
      // console.log("We are clear again");
      // reset filtered messages
      filteredMessages.forEach(element => {
         element.style.backgroundColor = "";
      });
      filteredMessages = [];

      unfilteredMessages.forEach(element => {
         element.style.display = "";
      });
      unfilteredMessages = [];

      // no grey background
      document.getElementById("messageFrame").className = "mmessagebox mfont";
   }
}

// Set event listeners
document.getElementById("loadingOverlay").addEventListener("click", stopFiltering);
document.addEventListener("keypress", function (e) {
   if (e.key === 'Enter') {
      applyFilter_input();
   }
});
document.getElementById('filterBtn').addEventListener("click", applyFilter_input);
document.getElementById('nameFilter').addEventListener('input', grey_table);
document.getElementById('typeFilter').addEventListener('input', grey_table);
document.getElementById('timeFilter').addEventListener('input', grey_table);
document.getElementById('textFilter').addEventListener('input', grey_table);
document.getElementById('timeRangeFilter').addEventListener('input', grey_table);
document.getElementById('recentsDropdown').addEventListener('change', add_filter);


// reload messages
let facility;
let first_tstamp;
let last_tstamp;
let n_messages;
let end_of_messages;
let timer_front;
let timer_tail;

function show_facilities() {
   if (localStorage.mNavigationButtons !== undefined) {
      document.getElementById("navigationFacilitiesButtons").innerHTML = localStorage.mFacilitiesButtons;
   }

   mjsonrpc_call("cm_msg_facilities").then(function (rpc) {
      var f = rpc.result.facilities;
      var html = "";
      for (var i = 0; i < f.length; i++) {
         var c = "mnav navButton";
         if (f[i] === facility) {
            c = "mnav mnavsel navButtonSel";
         }
         html += "<input type=button name=cmd value=\"" + f[i] + "\" class=\"" + c + "\" onclick=\"msg_load(\'" + f[i] + "\');return false;\">\n";
      }
      document.getElementById("navigationFacilitiesButtons").innerHTML = html;

      // cache navigation buttons in browser local storage
      localStorage.setItem("mFacilitiesButtons", html);

   }).catch(function (error) {
      document.getElementById("dlgErrorText").innerHTML = mjsonrpc_decode_error(error);
      dlgShow('dlgError');
      //mjsonrpc_error_alert(error);
   });
}

function resize_message_box() {
   // set message window height to fit browser window
   var h = window.innerHeight;
   var mf = document.getElementById('messageTable');
   h -= findPos(mf)[1];
   h -= 10; // top and bottom margin of .messagebox
   mf.style.maxHeight = h + "px";
}

function getUrlVars() {
   let vars = {};
   window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
      vars[key] = value;
   });
   return vars;
}

function msg_load(f) {
   // if facility comes from the button, use it
   if (f !== undefined)
      facility = f;
   else {
      // if facility is in URL, use it
      let urlfacility = decodeURI(getUrlVars()["facility"]);
      if (urlfacility !== "undefined")
         facility = urlfacility;
      // if facility is in local storage, use it
      else if (mhttpdConfig().mFacility !== undefined)
         facility = mhttpdConfig().mFacility;
      else
         // use 'midas' if no other source
         facility = 'midas';
   }

   // put facility in URL
   let url = window.location.href;
   if (url.search("&facility=") !== -1)
      url = url.slice(0, url.search("&facility="));
   url += "&facility=" + facility;
   if (url !== window.location.href)
      window.history.replaceState({}, "Midas History", url);

   mhttpdConfigSet("mFacility", f);
   first_tstamp = 0;
   last_tstamp = 0;
   n_messages = 0;
   end_of_messages = false;

   if (timer_front !== undefined)
      window.clearTimeout(timer_front);
   if (timer_tail !== undefined)
      window.clearTimeout(timer_tail);

   // manage selection of facility button
   let button = document.getElementById("navigationFacilitiesButtons").children;
   for (let i = 0; i < button.length; i++)
      if (button[i].value === facility)
         button[i].className = "mnav mnavsel navButtonSel";
      else
         button[i].className = "mnav navButton";

   // remove old messages
   var mf = document.getElementById('messageFrame');
   for (var i = mf.childNodes.length - 1; i > 0; i--)
      mf.removeChild(mf.childNodes[i]);

   mjsonrpc_call("cm_msg_retrieve", { "facility": facility, "time" : 0, "min_messages" : 100 }).then(function(rpc) {
      if(rpc.result.messages){
         var msg = rpc.result.messages.split("\n");
         msg_append(msg);
      }
      // check for new messages
      timer_front = window.setTimeout(msg_extend_front, 1000);
      // extend messages on scrolling down
      timer_tail = window.setTimeout(msg_extend_tail, 1000);
      resize_message_box();
   }).catch(function(error) {
      document.getElementById("dlgErrorText").innerHTML = mjsonrpc_decode_error(error);
      dlgShow('dlgError');
   });
   window.onresize = resize_message_box;
}

function msg_filter(msg) {
   let c = mhttpdConfig();
   for (let i = 0; i < msg.length; i++) {

      let skip = false;
      if (!c.pageTalk && msg[i].search(",TALK]") > 0)
         skip = true;
      if (!c.pageError && msg[i].search(",ERROR]") > 0)
         skip = true;
      if (!c.pageInfo && msg[i].search(",INFO]") > 0)
         skip = true;
      if (!c.pageLog && msg[i].search(",LOG]") > 0)
         skip = true;

      if (skip) {
         let t = parseInt(msg[i]);

         // skip messages in the future
         if (t < Math.floor(Date.now() / 1000)) {

            if (t > first_tstamp)
               first_tstamp = t;

            msg.splice(i, 1);
            i--;
         }
      }
   }
}

function msg_prepend(msg) {
   var mf = document.getElementById('messageFrame');
   if (mf.childNodes.length < 2) {
      msg_append(msg);
      return;
   }

   msg_filter(msg);

   for (var i = 0; i < msg.length; i++) {
      var line = msg[i];
      var t = parseInt(line);

      // skip messages in the future
      if (t > Math.floor(Date.now() / 1000))
         continue;

      if (line.indexOf(" ") && (t > 0 || t === -1))
         line = line.substr(line.indexOf(" ") + 1);
      var e = document.createElement("p");
      e.className = "mmessageline";
      e.appendChild(document.createTextNode(line));

      if (e.innerHTML === mf.childNodes[1 + i].innerHTML)
         break;
      mf.insertBefore(e, mf.childNodes[1 + i]);
      if (t > first_tstamp)
         first_tstamp = t;
      n_messages++;

      if (line.search("ERROR]") > 0) {
         e.style.backgroundColor = "var(--mred)";
      } else {
         e.style.backgroundColor = "var(--myellow)";
         e.age = new Date() / 1000;
         e.style.setProperty("-webkit-transition", "background-color 3s", "");
         e.style.setProperty("transition", "background-color 3s", "");
      }

   }
}

function msg_append(msg) {

   msg_filter(msg);

   if (msg[0] === "")
      end_of_messages = true;
   if (end_of_messages)
      return;
   var mf = document.getElementById('messageFrame');
   for (var i = 0; i < msg.length; i++) {
      var line;
      line = msg[i];
      var t = parseInt(line);

      // skip messages in the future
      if (t > Math.floor(Date.now() / 1000))
         continue;

      if (!(t <= -1) && t > first_tstamp)
         first_tstamp = t;
      if (!(t <= -1) && (last_tstamp === 0 || t < last_tstamp))
         last_tstamp = t;
      if (line.indexOf(" ") && (t > 0 || t === -1))
         line = line.substr(line.indexOf(" ") + 1);
      var e = document.createElement("p");
      e.className = "mmessageline";
      e.appendChild(document.createTextNode(line));
      if (line.search("ERROR]") > 0) {
         e.style.backgroundColor = "var(--mred)";
      }

      mf.appendChild(e);
      n_messages++;
   }
}

function findPos(obj) {
   var cursorleft = 0;
   var cursortop = 0;
   if (obj.offsetParent) {
      do {
         cursorleft += obj.offsetLeft;
         cursortop += obj.offsetTop;
         obj = obj.offsetParent;
      } while (obj);
      return [cursorleft, cursortop];
   }
}

function msg_extend_tail() {
   // if scroll bar is close to end, append messages
   var mf = document.getElementById('messageFrame');
   if (mf.scrollHeight - mf.scrollTop - mf.clientHeight < 2000) {
      if (!end_of_messages) {
         if (last_tstamp > 0) {
            mjsonrpc_call("cm_msg_retrieve", { "facility": facility, "time" : last_tstamp-1, "min_messages" : 100 }).then(function(rpc) {                
               var msg = [""]; // empty first element; will indicate last lines if call failed.
               if(rpc.result.messages){
                  msg = rpc.result.messages.split("\n");
               }
               msg_append(msg);
               timer_tail = window.setTimeout(msg_extend_tail, 1000);
            }).catch(function(error) {
               document.getElementById("dlgErrorText").innerHTML = mjsonrpc_decode_error(error);
               dlgShow('dlgError');
            });
         } else {
            // in non-timestamped mode, simply load full message list
            mjsonrpc_call("cm_msg_retrieve", { "facility": facility, "time" : 0, "min_messages" : n_messages+100 }).then(function(rpc) {
               var msg = []; // empty first element; will indicate last lines if call failed.
               if(rpc.result.messages){
                  msg = rpc.result.messages.split("\n");
               }
               n_messages = 0;
               var mf = document.getElementById('messageFrame');
               for (var i = mf.childNodes.length - 1; i > 0; i--)
                  mf.removeChild(mf.childNodes[i]);
               msg_append(msg);
               timer_tail = window.setTimeout(msg_extend_tail, 1000);
            }).catch(function(error) {
               document.getElementById("dlgErrorText").innerHTML = mjsonrpc_decode_error(error);
               dlgShow('dlgError');
            });
         }
      }
   } else
   timer_tail = window.setTimeout(msg_extend_tail, 1000);
}

function msg_extend_front() {

   if (timer_front !== undefined)
      window.clearTimeout(timer_front);

   // remove color of new elements after a while
   var mf = document.getElementById('messageFrame');
   for (i = 1; i < mf.childNodes.length; i++) {
      if (mf.childNodes[i].age !== undefined) {
         var t = new Date() / 1000;
         if (t > mf.childNodes[i].age + 5)
            mf.childNodes[i].style.backgroundColor = "";
      }
   }

   // check for new message if time stamping is on
   if (first_tstamp) {

      mjsonrpc_call("cm_msg_retrieve", { "facility": facility, "time" : first_tstamp, "min_messages" : 0 }).then(function(rpc) {
         if (rpc.result.messages !== undefined) {
            var msg = rpc.result.messages.split("\n");
            msg_prepend(msg);
         }
         timer_front = window.setTimeout(msg_extend_front, 1000);
      }).catch(function(error) {

         if (error.xhr && error.xhr.readyState === 4 && error.xhr.status === 0) {
            // don't display error, since this one is shown on the header automatically

            // retry communication
            timer_front = window.setTimeout(msg_extend_front, 1000);
         } else {
            document.getElementById("dlgErrorText").innerHTML = mjsonrpc_decode_error(error);
            dlgShow('dlgError');
         }
      });
   }else{
      timer_front = window.setTimeout(msg_extend_front, 1000);
   }
}
