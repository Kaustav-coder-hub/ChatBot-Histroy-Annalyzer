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