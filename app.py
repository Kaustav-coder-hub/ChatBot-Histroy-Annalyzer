from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from search import search_with_gemini
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# routes

@app.route("/")
def main():
    return render_template("index.html")
@app.route('/search', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        chat_memory = session.get("chat_memory", [])
        response = search_with_gemini(user_input, chat_memory)
        chat_memory.append({"user_input": user_input, "bot_response": response})
        chat_memory = chat_memory[-20:]
        session["chat_memory"] = chat_memory
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Error during /search: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)