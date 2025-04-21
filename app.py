from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from search import search_with_gemini, is_browser_history_query
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
    history_access_enabled = session.get('history_access_enabled', False)  # Check if history access is enabled

    logging.debug(f"Request JSON: {data}")
    logging.debug(f"History access enabled: {history_access_enabled}")

    if not history_access_enabled:
        # Prompt the user to enable history access or proceed with a normal response
        return jsonify({
            "response": "History access is disabled. Would you like to enable it or proceed with a normal response?",
            "options": ["Enable history access", "Proceed with normal response"]
        })

    # If history access is enabled, handle the query normally
    if is_browser_history_query(query):
        history_response = fetch_brave_history()
        return jsonify({"response": history_response})

    # Handle general queries
    general_response = search_duckduckgo(query)
    return jsonify({"response": general_response})

@app.route('/privacy', methods=['POST'])
def privacy():
    data = request.get_json()
    option = data.get('option')

    if option == "Enable history access":
        session['history_access_enabled'] = True
        return jsonify({"response": "History access has been enabled. You can now ask history-related questions."})
    elif option == "Proceed with normal response":
        return jsonify({"response": "Okay, proceeding with a normal response."})
    else:
        return jsonify({"response": "Invalid option selected."})

@app.route('/enable-history', methods=['POST'])
def enable_history():
    session['history_access_enabled'] = True  # Enable history access for the session
    return jsonify({"response": "History access has been enabled."})

if __name__ == "__main__":
    app.run(debug=True)