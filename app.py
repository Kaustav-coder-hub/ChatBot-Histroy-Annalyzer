from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from search import search_with_gemini, is_browser_history_query, fetch_brave_history, search_duckduckgo, chat_memory
import logging



load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Global variable for history access
history_access_enabled = False

# routes

@app.route("/")
def main():
    return render_template("index.html")

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '').strip()
    history_access= data.get('historyAccess', False)  # Check if history access is enabled

    # Update session with the history access status
    session['history_access_enabled'] = history_access_enabled
    logging.debug(f"Request JSON: {data}")
    logging.debug(f"History access enabled: {session.get('history_access_enabled')}")

    # Check if the query is related to browser history
    if is_browser_history_query(query):
        if not session.get('history_access_enabled', False):
            # Prompt the user to enable history access or proceed with a normal response
            return jsonify({
                "response": "History access is disabled. Would you like to enable it or proceed with a normal response?",
                "options": ["Enable history access", "Proceed with normal response"]
            })

        # If history access is enabled, fetch the browser history
        history_response = fetch_brave_history()
        return jsonify({"response": history_response})

    # Handle normal queries
    response = search_with_gemini(query, chat_memory)
    return jsonify({"response": response})

@app.route('/privacy', methods=['POST'])
def privacy():
    data = request.get_json()
    option = data.get('option')

    if option == "Enable history access":
        session['history_access_enabled'] = True
        logging.info("History access enabled.")
        return jsonify({"response": "History access has been enabled. You can now ask history-related questions."})
    elif option == "Proceed with normal response":
        logging.info("Proceeding without history access.")
        return jsonify({"response": "Okay, proceeding with a normal response."})
    else:
        logging.warning("Invalid option selected.")
        return jsonify({"response": "Invalid option selected."})

@app.route('/enable-history', methods=['POST'])
def enable_history():
    session['history_access_enabled'] = True  # Enable history access for the session
    return jsonify({"response": "History access has been enabled."})

if __name__ == "__main__":
    app.run(debug=True)