import os
import google.generativeai as genai
from dotenv import load_dotenv
import random
import requests
import sqlite3
from datetime import datetime, timedelta
import logging
import shutil
import tempfile
from flask import session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

model = genai.GenerativeModel("gemini-1.5-pro-latest")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY not found in environment variables.")
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
logging.info("Generative AI model configured successfully.")

# Add a global toggle for history-based answers
history_access_enabled = False  # Default is OFF
logging.debug(f"History access enabled? {history_access_enabled}")

# --- Sentiment & Tone Detection ---
def detect_sentiment(text: str) -> str:
    logging.debug(f"Detecting sentiment for text: {text}")
    lowered = text.lower()
    if any(word in lowered for word in ["sad", "depressed", "tired", "stressed", "lonely"]):
        return "sad"
    elif any(word in lowered for word in ["happy", "excited", "great", "fun", "love"]):
        return "happy"
    elif any(word in lowered for word in ["angry", "frustrated", "annoyed", "upset"]):
        return "angry"
    return "neutral"

def get_tone(sentiment: str) -> str:
    logging.debug(f"Getting tone for sentiment: {sentiment}")
    return {
        "sad": "empathetic and kind",
        "happy": "excited and cheerful",
        "angry": "calm and understanding",
        "neutral": "friendly and informative"
    }.get(sentiment, "friendly")

# --- Greeting & Side Notes ---
GREETING_VARIANTS = [
    "Hey there! 😊",
    "Hi! What’s on your mind today?",
    "Hello! Ready to explore something new?",
    "Yo! Got a question for me?",
    "Hey! Curious about something?",
    "Hi there! What can I help you with?",
    "Welcome! What’s up?",
]

SIDE_NOTES = [
    "By the way, you asked a great question!",
    "Fun fact: this comes up a lot in interesting discussions!",
    "You're diving into a pretty cool topic.",
    "People don’t ask this enough — well done.",
    "This is one of those questions I love getting!",
    "I genuinely appreciate your quriosity!"
]

FOLLOW_UP_QUESTIONS = {
    "explore": [
        "Would you like to explore this further?",
        "Want me to break it down more?",
        "Should I expand on that?",
        "Would a detailed explanation help here?",
        "Curious about the 'why' behind this?",
        "Would a deeper dive into this topic help?",
        "Shall I walk you through this step-by-step?",
    ],
    "examples": [
        "Need an example to make it clearer?",
        "Shall I walk you through a sample scenario?",
        "Would a real-world analogy help here?",
        "Would you like a visual or analogy to understand it better?",
        "Want to hear how this works in real life?",
        "Should I explain this like you're five?",
    ],
    "connections": [
        "Want to know how this connects to something bigger?",
        "Would you like the advanced version of this?",
        "Want me to show how this works with real data?",
        "Want a nerdy detail? I’ve got one.",
        "Feeling curious? I can go on!",
        "Want to geek out on this a bit more?"
    ],
    "decisions": [
        "Would it help if I listed pros and cons?",
        "Need help choosing between similar options?",
        "Want help choosing between options?",
        "Should I compare a few approaches?",
        "Shall I summarize the key takeaways?",
    ],
    "style_variation": [
        "Want to hear the quick version and then the in-depth one?",
        "Would you prefer a comparison to something familiar?",
        "Want me to explain it like a story?",
        "Would you like a more casual or formal explanation?",
    ],
    "friendly": [
        "Want to keep chatting about this?",
        "Would you like a fun fact connected to this?",
        "Having fun? Want more of this?",
        "This is exciting right? Want to know more?",
        "Are you loving the conversation so far?"
    ]
}

# Expanded trigger keywords
trigger_keywords = [
    "explain", "how", "why", "step", "details", "example", "in-depth", "deep", "more info", "what is",
    "can you elaborate", "could you explain", "please elaborate", "elaborate", "tell me more", 
    "go deeper", "walk me through", "full explanation", "detailed", "clarify", "clarification", 
    "expand on", "break it down", "overview", "introduction to", "help me understand", 
    "simplify", "demystify", "teach me", "layman", "easy explanation", "basic", "fundamentals of", 
    "I don’t understand", "I’m confused", "I’m curious", "need context", "context", 
    "what does it mean", "meaning of", "beginner", "from scratch", "starting from", "what do you mean",
    "deeper", "technical", "can you describe", "what happens when", "how does it work"
]
FOLLOW_UP_RESPONSES = [
            "yes", "please explain", "go deeper", "elaborate", "sure", "of course", "continue",
            "more info", "keep going", "i’m interested", "yes, please", "want to learn",
            "do explain", "want to know more", "tell me more", "please do", "what else"
        ]
def needs_deep_answer(user_input: str) -> bool:
    return any(word in user_input.lower() for word in trigger_keywords)

def detect_intent(user_input: str) -> str:
    lowered = user_input.lower()
    if any(kw in lowered for kw in ["compare", "vs", "difference between", "pros and cons"]):
        return "compare"
    elif any(kw in lowered for kw in ["example", "analogy", "illustrate"]):
        return "examples"
    elif any(kw in lowered for kw in ["connect", "relation", "linked", "association"]):
        return "connections"
    elif any(kw in lowered for kw in trigger_keywords):
        return "explore"
    else:
        return "friendly"

def search_duckduckgo(query: str) -> str:
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]
        return "I couldn't find a good answer on that. Want me to dig deeper?"
    except Exception as e:
        return f"Error accessing DuckDuckGo: {str(e)}"


# --- Browser History Query Detection ---
def is_browser_history_query(query: str) -> bool:
    logging.debug(f"Checking if query is related to browser history: {query}")
    if not session.get('history_access_enabled', False):
        logging.debug("History access is disabled.")
        return False
    history_keywords = ["browser history", "visited sites", "recent tabs", "history", "my history", "what did I visit"]
    is_query_history_related = any(keyword in query.lower() for keyword in history_keywords)
    logging.debug(f"Is query history-related? {is_query_history_related}")
    return is_query_history_related


# Function to fetch Chrome browser history
def fetch_brave_history(keyword=None, date=None):
    logging.debug(f"Fetching Brave browser history with keyword: {keyword}, date: {date}")
    history_db = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/History")
    temp_db = tempfile.NamedTemporaryFile(delete=False).name

    try:
        shutil.copy2(history_db, temp_db)
        logging.debug(f"Copied Brave history database to temporary file: {temp_db}")
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        query = "SELECT url, title, last_visit_time FROM urls"
        conditions = []
        params = []

        if keyword:
            conditions.append("(title LIKE ? OR url LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if date:
            start_time = datetime.strptime(date, "%Y-%m-%d")
            start_timestamp = int((start_time - datetime(1601, 1, 1)).total_seconds() * 1e6)
            conditions.append("last_visit_time >= ?")
            params.append(start_timestamp)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY last_visit_time DESC"
        logging.debug(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        history = []
        for url, title, last_visit_time in results:
            timestamp = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time)
            history.append(f"{title} ({url}) - Last visited: {timestamp}")

        logging.debug(f"Fetched {len(history)} history entries.")
        return "\n".join(history) if history else "No matching history found."
    except Exception as e:
        logging.error(f"Error fetching browser history: {e}")
        return f"Error fetching browser history: {e}"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)
        logging.info("Temporary history data cleared securely.")

# filepath: d:\ChatBot-Histroy-Annalyzer\search.py
def fetch_edge_history():
    """
    Fetches the browsing history from Microsoft Edge's history database.
    """
    # Get the path to Edge's history database from environment variables
    history_db = os.environ.get("EDGE_HISTORY_PATH")
    if not history_db:
        logging.error("EDGE_HISTORY_PATH is not set in environment variables.")
        return "Error: Edge history path is not configured."

    temp_db = tempfile.NamedTemporaryFile(delete=False).name  # Temporary copy of the database

    try:
        # Make a copy of the database to avoid locking issues
        shutil.copy2(history_db, temp_db)

        # Connect to the copied database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Query to fetch the last 10 visited URLs
        cursor.execute("""
            SELECT url, title, last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT 10
        """)

        results = cursor.fetchall()
        conn.close()

        # Format the results
        history = []
        for url, title, last_visit_time in results:
            # Convert Edge's timestamp to a readable format
            timestamp = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time)
            history.append(f"{title} ({url}) - Last visited: {timestamp}")

        return "\n".join(history)
    except Exception as e:
        logging.error(f"Error fetching browser history: {e}")
        return f"Error fetching browser history: {e}"
    finally:
        # Clean up the temporary database copy
        if os.path.exists(temp_db):
            os.remove(temp_db)
        logging.info("Temporary history data cleared securely.")

# --- Handle Privacy Checkpoint ---
def handle_privacy_checkpoint(user_input: str) -> str:
    logging.debug(f"Handling privacy checkpoint for input: {user_input}")
    if not session.get('history_access_enabled', False):
        if "enable just for this session" in user_input.lower():
            session['history_access_enabled'] = True
            logging.info("History access enabled for this session.")
            return "History access enabled for this session. Please try your query again."
        elif "enable permanently" in user_input.lower():
            session['history_access_enabled'] = True
            logging.info("History access enabled permanently.")
            return "History access enabled permanently. Please try your query again."
        elif "ignore this query" in user_input.lower():
            logging.info("Ignoring the query related to browser history.")
            return "Okay, ignoring the query related to browser history."
        else:
            logging.debug("Prompting user to enable history access.")
            return (
                "History access is disabled. Would you like to enable it?\n"
                "Options:\n"
                "1. Enable just for this session\n"
                "2. Enable permanently\n"
                "3. Ignore this query"
            )
    return None

chat_memory = []

MAX_MEMORY = 20

# --- Main Search Function ---
def search_with_gemini(user_input: str, chat_memory: list) -> str:
    logging.debug(f"Processing user input: {user_input}")

    # Handle general queries
    if not user_input.strip():
        logging.warning("Empty user input detected.")
        return "Please enter a valid question."

    try:
        # Safety settings for the generative model
        safety_settings = {
            "HARASSMENT": "BLOCK_NONE",
            "HATE_SPEECH": "BLOCK_NONE",
            "SEXUAL": "BLOCK_NONE",
            "DANGEROUS": "BLOCK_NONE"
        }

        # Try DuckDuckGo for quick answers
        logging.debug("Querying DuckDuckGo for a quick answer.")
        ddg_response = search_duckduckgo(user_input)

        if ddg_response and not ddg_response.lower().startswith("i couldn't find a good answer"):
            chat_memory.append({
                "user_input": user_input,
                "bot_response": ddg_response
            })
            if len(chat_memory) > MAX_MEMORY:
                chat_memory.pop(0)
            logging.debug("Returning DuckDuckGo response.")
            return ddg_response

        # Handle deep answers using the generative model
        logging.debug("Generating a deep answer using the generative model.")
        is_follow_up = needs_deep_answer(user_input)
        intent = detect_intent(user_input)
        sentiment = detect_sentiment(user_input)
        tone = get_tone(sentiment)

        # Context logic for generative model
        context = "\n".join(
            f"User: {msg['user_input']}\nAssistant: {msg['bot_response']}"
            for msg in chat_memory[-MAX_MEMORY:]
        )

        # Prompt for the generative model
        prompt = f"""
You are a friendly and knowledgeable assistant who acts like a smart, human-powered search engine. Think of yourself as a helpful guide — someone who explains concepts clearly, provides useful information quickly, and makes learning feel effortless.

Your job is to:
- Provide trustworthy, accurate, and digestible information (like an informative book).
- Sound approachable, curious, and slightly warm (not robotic).
- Use Markdown formatting (*bold, *italics, bullet points, etc.) to improve clarity.
- Anticipate what the user might want next, and gently offer follow-up help or suggestions.

*Conversation Context*:
{context}

*Current User Question*:
{user_input}

*Tone to use*: {tone}

---

Now generate a response using the following style:

{f'''
Start with a friendly greeting like: "{greeting}" (or something equally warm and welcoming).

Give a brief, clear summary of the topic (2–3 sentences). Keep it informative, but easy to digest.

Wrap up with a follow-up suggestion like: "{follow_up}" if it fits naturally into the flow.

Add a light side comment if appropriate: "{side_note}".
''' if not is_follow_up else '''
This is a follow-up question.

Now provide a more in-depth, structured explanation:
- Use examples, analogies, or comparisons.
- Build on prior information without repeating it.
- Keep the tone friendly, expert, and easy to understand.
'''}
"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 400,
            },
            safety_settings=safety_settings
        )

        result = response.text.strip() if response and response.text else "Sorry, I couldn't find a good answer."
        logging.debug(f"Generated response: {result}")

        # Update chat memory
        chat_memory.append({
            "user_input": user_input,
            "bot_response": result
        })
        if len(chat_memory) > MAX_MEMORY:
            chat_memory.pop(0)

        return result

    except Exception as e:
        logging.error(f"Error in search_with_gemini: {e}")
        return f"Error: {str(e)}"