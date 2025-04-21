let typingInterval;

// --- Utility Functions ---
function parseMarkdownToHTML(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/^### (.*$)/gim, "<h3>$1</h3>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/^# (.*$)/gim, "<h1>$1</h1>")
    .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/gim, "<em>$1</em>")
    .replace(/`([^`]+)`/gim, "<code>$1</code>")
    .replace(/\n/g, "<br />");
}

function scrollToBottom() {
  const chatBox = document.getElementById("chat-box");
  chatBox.scrollTo({
    top: chatBox.scrollHeight,
    behavior: "smooth"
  });
}

// --- Typing Effect ---
function typeEffect(element, text, speed = 20, callback) {
  let i = 0;
  const cursor = '<span class="cursor">|</span>';
  element.innerHTML = "";

  function typeChar() {
    if (i < text.length) {
      element.innerHTML = text.slice(0, i + 1) + cursor;
      i++;
      scrollToBottom(); // Scroll during typing
      setTimeout(typeChar, speed);
    } else {
      element.innerHTML = text; // Final text without cursor
      if (callback) callback();
    }
  }

  typeChar();
}

// --- Display Functions ---
function displayUserMessage(message) {
  const chatBox = document.getElementById("chat-box");

  // Create a new message element for the user
  const userMessage = document.createElement("div");
  userMessage.className = "user-message"; // Add a class for styling
  userMessage.innerHTML = message;

  // Append the user's message to the chat box
  chatBox.appendChild(userMessage);

  // Scroll to the bottom of the chat box
  scrollToBottom();

  // Clear the input field
  document.getElementById("user_input").value = "";
}

function displayChatbotResponse(response) {
  const chatBox = document.getElementById("chat-box");

  // Clear any existing typing interval
  if (typingInterval) {
    clearInterval(typingInterval);
  }

  // Create a new message element for the bot
  const botMessage = document.createElement("div");
  botMessage.className = "bot-message"; // Add a class for styling
  chatBox.appendChild(botMessage);

  // Scroll to the bottom of the chat box
  scrollToBottom();

  // Display the response letter by letter
  let index = 0;
  typingInterval = setInterval(() => {
    if (index < response.length) {
      botMessage.innerHTML += response[index];
      index++;
      scrollToBottom();
    } else {
      clearInterval(typingInterval); // Stop the interval when all letters are displayed
    }
  }, 50); // Adjust the delay (in milliseconds) for the typing speed
}

function displayOptions(options) {
  const chatBox = document.getElementById("chat-box");
  const optionsHTML = options.map(option => `<button onclick="handleOption('${option}')">${option}</button>`).join('');
  chatBox.innerHTML += `<div class="message bot-message">${optionsHTML}</div>`;
  scrollToBottom();

  // Disable buttons after one is clicked
  document.querySelectorAll(".option-button").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".option-button").forEach(btn => btn.disabled = true);
    });
  });
}

// --- Backend Communication ---
function sendToBackend(userInput, historyAccessToggle = false) {
  displayUserMessage(userInput);

  const thinkingIndicator = document.getElementById("thinking-indicator");
  thinkingIndicator.style.display = "block";

  fetch('/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: userInput, historyAccess: historyAccessToggle })
  })
    .then(response => response.json())
    .then(data => {
      thinkingIndicator.style.display = "none";

      if (data.options) {
        // If the backend provides options, display them to the user
        displayChatbotResponse(data.response);
        displayOptions(data.options);
      } else {
        // Otherwise, display the chatbot's response
        displayChatbotResponse(data.response);
      }
    })
    .catch(error => {
      thinkingIndicator.style.display = "none";
      displayChatbotResponse(`Error: ${error.message}`);
    });
}

// --- Query Handling ---
function isBrowserHistoryQuery(query) {
  const historyKeywords = ["browser history", "visited sites", "recent tabs", "history", "my history", "what did I visit"];
  return historyKeywords.some(keyword => query.toLowerCase().includes(keyword));
}

// --- Event Listeners ---
document.getElementById("search-form").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent the form from reloading the page

  const userInput = document.getElementById("user_input").value.trim();
  const historyAccessToggle = document.querySelector('input[name="privacy_option"]').checked; // Check if the radio button is enabled

  if (!userInput) {
    alert("Please enter a query before submitting.");
    return; // Stop further execution if input is empty
  }

  // Check if the query is related to browser history
  if (isBrowserHistoryQuery(userInput)) {
    if (!historyAccessToggle) {
      alert("History access is disabled. Please enable it to ask history-related questions.");
      return; // Stop further execution if history access is not enabled
    }
  }

  // Send the user input and history access status to the backend
  sendToBackend(userInput, historyAccessToggle);
});

// Handle the radio button below the text box
document.getElementById("send-button").addEventListener("click", () => {
    const userInput = document.getElementById("user-input").value;
    const historyAccessToggle = document.getElementById("history-access-toggle").checked;

    // Send the user input and history access status to the backend
    sendToBackend(userInput, historyAccessToggle);
});

// Show the privacy popup when needed
function showPrivacyPopup() {
    document.getElementById("privacy-popup").style.display = "block";
}

// Handle the privacy popup submission
document.getElementById("privacy-submit").addEventListener("click", () => {
  const selectedOption = document.querySelector('input[name="privacy-option"]:checked');
  if (!selectedOption) {
    alert("Please select an option before submitting.");
    return;
  }

  // Send the selected option to the backend
  handleOption(selectedOption.value);

  // Hide the popup
  document.getElementById("privacy-popup").style.display = "none";
});

// --- Handle Options ---
window.handleOption = function(option) {
  console.log(`Selected option: ${option}`); // Debugging log
  // Send the selected option to the backend
  fetch('/privacy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ option })
  })
    .then(response => response.json())
    .then(data => {
      // Display the response from the backend
      displayChatbotResponse(data.response);
    })
    .catch(error => {
      displayChatbotResponse(`Error: ${error.message}`);
    });
};