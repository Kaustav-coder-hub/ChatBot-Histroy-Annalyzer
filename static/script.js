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

function scrollToBottom() {
  const chatBox = document.getElementById("chat-box");
  chatBox.scrollTo({
    top: chatBox.scrollHeight,
    behavior: "smooth"
  });
}

document.getElementById("search-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const userInputElem = document.getElementById("user_input");
  const userInput = userInputElem.value.trim();
  if (!userInput) return;

  const chatBox = document.getElementById("chat-box");

  chatBox.insertAdjacentHTML("beforeend", `
    <div class="message user">
      <div class="bubble"><strong>You:</strong> ${userInput}</div>
    </div>
  `);
  scrollToBottom();
  userInputElem.value = "";

  const botMessage = document.createElement("div");
  botMessage.className = "message bot";
  const botBubble = document.createElement("div");
  botBubble.className = "bubble typing";
  botBubble.innerHTML = `<em>Thinking<span class="dots"></span></em>`;
  botMessage.appendChild(botBubble);
  chatBox.appendChild(botMessage);
  scrollToBottom();

  try {
    const res = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: userInput }),
    });

    const data = await res.json();
    const parsedText = parseMarkdownToHTML(data.response || "Sorry, I couldn't respond.");
    botBubble.classList.remove("typing");

    typeEffect(botBubble, parsedText, 20); // live typing
  } catch (err) {
    botBubble.innerHTML = `<div class="bubble error"><strong>Error:</strong> Server issue or timeout.</div>`;
    botBubble.classList.remove("typing");
    console.error("Fetch error:", err);
  }

  scrollToBottom();
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
    const selectedOption = document.querySelector('input[name="privacy-option"]:checked').value;

    // Send the selected option to the backend
    handlePrivacyOption(selectedOption);

    // Hide the popup
    document.getElementById("privacy-popup").style.display = "none";
});

// Example function to send data to the backend
function sendToBackend(userInput, historyAccessToggle) {
    fetch("/search", {  // Correct endpoint
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput, history_access_toggle: historyAccessToggle }) // Match backend keys
    }).then(response => response.json())
      .then(data => {
          if (data.showPrivacyPopup) {
              showPrivacyPopup();
          } else {
              displayChatbotResponse(data.response);
          }
      });
}

// Example function to handle privacy option
function handlePrivacyOption(option) {
    fetch("/privacy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ option })
    }).then(response => response.json())
      .then(data => {
          displayChatbotResponse(data.response);
      });
}

// Example function to display chatbot response
function displayChatbotResponse(response) {
    const chatWindow = document.getElementById("chat-window");
    const message = document.createElement("div");
    message.textContent = response;
    chatWindow.appendChild(message);
}