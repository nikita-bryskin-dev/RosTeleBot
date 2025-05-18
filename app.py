from flask import Flask, request, jsonify, render_template
from nlp import get_bot_response
from AI_bot.ai_bot import end_dialog

import atexit
import signal
import sys
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = get_bot_response(user_message)
    return jsonify({'response': response})

def on_shutdown(*args):
    print("[INFO] Завершение работы сервера")
    end_dialog()
    sys.exit(0)

atexit.register(on_shutdown)
signal.signal(signal.SIGINT, on_shutdown)
signal.signal(signal.SIGTERM, on_shutdown)

if __name__ == '__main__':
    app.run(debug=True)