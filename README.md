# DDC Chatbot - Browser History and General Query Solver

This project is a chatbot designed to handle both **general queries** and **browser history-related queries**. It uses a combination of search engine APIs and browser history data to provide accurate and helpful responses to user queries.

---

## Features

### 1. **General Query Solving**
- The chatbot can answer general questions using search engine APIs like DuckDuckGo or other integrated models.
- It provides concise, accurate, and user-friendly responses.

### 2. **Browser History Query Handling**
- The chatbot can fetch and display the user's **recent browser history** (e.g., last accessed websites).
- It supports Brave browser history retrieval and formats the results for easy readability.

---

## How It Works

1. **General Queries**:
   - The chatbot uses search engine APIs to fetch answers for general questions.
   - Example:
     ```
     You: What is the capital of France?
     AI: The capital of France is **Paris**.
     ```

2. **Browser History Queries**:
   - The chatbot detects queries related to browser history (e.g., "Show me my browser history").
   - It fetches the last accessed websites from the Brave browser's history database.
   - Example:
     ```
     You: Tell me about my last accessed browser history.
     AI: **Browser History:**
         - Example Title (https://example.com) - Last visited: 2025-04-15 10:30:00
         - Another Title (https://another.com) - Last visited: 2025-04-15 09:45:00
     ```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Brave browser installed (if using the browser history feature)

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DDC-Chatbot
   ```
2. Create a virtual environment:
   ```bash
   python -m venv DDC-Chatbot-Search-Engine-env
   source DDC-Chatbot-Search-Engine-env/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the .env file
   - Create a .env file in the root directory.
   - Add your Gemini API key:
    ```bash
   GEMINI_API_KEY=your_api_key_here
   ```
## Usage
1. Run the chatbot
   ```bash
   python app.py

   ```
2. Start chatting
   1. Ask general questions like:
   ```bash
   What is Python?

   ```
   2. Or browser-based questions like:
   ```bash
   Show me my browser history.

   ```

## Credits
* General Query Solving Features: Developed by [Poushali Bhattacharyya](https://github.com/Poushali-02)

* Browser History Query Handling: Added by [Kaustav](https://github.com/Kaustav-coder-hub)

