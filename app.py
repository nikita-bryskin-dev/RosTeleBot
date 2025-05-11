from flask import Flask, request, jsonify, render_template
from nlp import get_bot_response
import sqlite3
import datetime
import uuid

app = Flask(__name__)

DB_PATH = 'DB/WebAppDB.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = get_bot_response(user_message)

    # Добавляем в таблицу stat новый запрос со статусом "открыто"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    request_id = str(uuid.uuid4())
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO stat (ID, Status, Date) VALUES (?, ?, ?)",
                   (request_id, 'открыто', now))
    conn.commit()
    conn.close()

    return jsonify({'response': response, 'request_id': request_id})

@app.route('/analytics')
def analytics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Status, Date FROM stat ORDER BY Date DESC")
    stats = cursor.fetchall()
    conn.close()
    return render_template('analytics.html', stats=stats)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    request_id = data.get('id')
    new_status = data.get('status', 'закрыто')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE stat SET Status = ? WHERE ID = ?", (new_status, request_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Статус обновлён'})

if __name__ == '__main__':
    app.run(debug=True)