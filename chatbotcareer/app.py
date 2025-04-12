from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from flask import send_from_directory
import os

# -------------------------------
# Setup Gemini
# -------------------------------
GEMINI_API_KEY = "AIzaSyADleIxGjqLePvyk6NFNMDQK480WpUiQt0"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# -------------------------------
# Initialize Flask
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Load About File
# -------------------------------
def load_about_info():
    try:
        with open("docs/about.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading about.txt: {e}")
        return "Platform documentation is currently unavailable."

ABOUT_TEXT = load_about_info()

# -------------------------------
# Career Coach Prompt
# -------------------------------
SYSTEM_PROMPT = """
You are a professional career coach AI assistant. Your purpose is to help users with career-related questions only.
Focus exclusively on:
- Career switching advice
- Resume and CV optimization
- Job search strategies
- Interview preparation
- Professional skill development
- Remote work guidance
- Industry-specific career advice

If a user asks about topics unrelated to careers, politely redirect them to ask career-related questions only.
Provide practical, actionable advice tailored to the user's specific situation when possible.
"""

# -------------------------------
# Keyword Match Logic for Website Info
# -------------------------------
def is_about_query(message: str) -> bool:
    about_phrases = [
        'how does your website work', 
        'how it works', 
        'what is intera', 
        'platform features',
        'platform facilities', 
        'website features', 
        'services', 
        'offerings', 
        'mock interview',
        'salary estimator', 
        'genesis', 
        'explorer', 
        'resume builder', 
        'career switch help',
        'intera platform', 
        'about your platform', 
        'about intera', 
        'what is genesis',
        'what is explorer', 
        'interview preparation tool', 
        'ai salary tool',
        'ai negotiation', 
        'intera features', 
        'platform support', 
        'platform overview',
        'how does this work',
        'what can you do',
        'what do you offer'
    ]
    msg = message.lower()
    return any(phrase in msg for phrase in about_phrases)

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/docs/<path:filename>')
def serve_docs(filename):
    return send_from_directory('docs', filename)

@app.route('/chat', methods=['POST'])
def chat():
    if not request.json or 'message' not in request.json:
        return jsonify({'error': 'No message provided'}), 400

    user_message = request.json['message']
    is_about_platform = is_about_query(user_message)

    try:
        if is_about_platform:
            # Return the about.txt content directly with platform info formatting
            return jsonify({
                'response': f"Here's information about our platform:\n\n{ABOUT_TEXT}",
                'is_platform_info': True
            })
        else:
            # Use career coaching system prompt
            chat = model.start_chat(history=[
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "model", "parts": [
                    "I'm a career coach assistant. I'm here to help with career-related questions only."
                ]},
                {"role": "user", "parts": [user_message]}
            ])

            response = chat.send_message(user_message)
            return jsonify({
                'response': response.text,
                'is_platform_info': False
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------
# Run the app
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)