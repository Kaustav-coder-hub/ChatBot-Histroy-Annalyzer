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
def ask():
    global history_access_enabled
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        history_access_toggle = data.get('history_access_toggle', False)  # Get toggle status from frontend

        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        # Enable history access for this session if the toggle is checked
        if history_access_toggle:
            history_access_enabled = True

        # Check if the query is history-based and history access is disabled
        if is_browser_history_query(user_input) and not history_access_enabled:
            return jsonify({"showPrivacyPopup": True})

        # Process the query
        chat_memory = session.get("chat_memory", [])
        response = search_with_gemini(user_input, chat_memory)
        chat_memory.append({"user_input": user_input, "bot_response": response})
        chat_memory = chat_memory[-20:]
        session["chat_memory"] = chat_memory
        return jsonify({"response": response})

    except Exception as e:
        print(f"Error during /search: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

@app.route('/privacy', methods=['POST'])
def privacy():
    global history_access_enabled
    try:
        data = request.get_json()
        option = data.get('option')

        if option == "1":
            history_access_enabled = True  # Enable for this session
            response = "History access enabled for this session."
        elif option == "2":
            history_access_enabled = True  # Enable permanently
            response = "History access enabled permanently."
        elif option == "3":
            response = "History-based query ignored."
        else:
            response = "Invalid option."

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error during /privacy: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)