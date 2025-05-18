from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import csv
import io

app = Flask(__name__)
app.secret_key = 'supersecretkey'

class KnowledgeBase:
    def __init__(self, db_name='knowledge_base.db'):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS qa_pairs
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          question TEXT NOT NULL UNIQUE,
                          answer TEXT NOT NULL)''')

    def add_pair(self, question, answer):
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.execute('INSERT INTO qa_pairs (question, answer) VALUES (?, ?)', 
                           (question, answer))
            return True, None
        except sqlite3.IntegrityError as e:
            return False, str(e)

    def get_all(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute('SELECT id, question, answer FROM qa_pairs')
            return cursor.fetchall()

    def get_pair(self, pair_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute('SELECT id, question, answer FROM qa_pairs WHERE id = ?', (pair_id,))
            return cursor.fetchone()

    def edit_pair(self, pair_id, new_question, new_answer):
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.execute('''UPDATE qa_pairs 
                             SET question = ?, answer = ?
                             WHERE id = ?''',
                          (new_question, new_answer, pair_id))
            return True, None
        except sqlite3.IntegrityError as e:
            return False, str(e)

    def export_csv(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute('SELECT question, answer FROM qa_pairs')
            data = cursor.fetchall()
        
        output = io.BytesIO()
        writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8'))
        writer.writerow(['question', 'answer'])
        writer.writerows(data)
        output.seek(0)
        return output

    def import_csv(self, file_stream):
        reader = csv.DictReader(io.TextIOWrapper(file_stream))
        for row in reader:
            status, error = self.add_pair(row['question'], row['answer'])
            if not status:
                return False, error
        return True, None

kb = KnowledgeBase()

@app.route('/')
def index():
    qa_pairs = kb.get_all()
    return render_template('index.html', qa_pairs=qa_pairs)

@app.route('/add', methods=['GET', 'POST'])
def add_pair():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        status, error = kb.add_pair(question, answer)
        if status:
            flash('Запись успешно добавлена', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Ошибка: {error}', 'danger')
    return render_template('add.html')

@app.route('/edit/<int:pair_id>', methods=['GET', 'POST'])
def edit_pair(pair_id):
    pair = kb.get_pair(pair_id)
    if not pair:
        flash('Запись не найдена', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_question = request.form['question']
        new_answer = request.form['answer']
        status, error = kb.edit_pair(pair_id, new_question, new_answer)
        if status:
            flash('Запись успешно обновлена', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Ошибка: {error}', 'danger')
    
    return render_template('edit.html', pair=pair)

@app.route('/export/csv')
def export_csv():
    csv_data = kb.export_csv()
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name='knowledge_base.csv'
    )

@app.route('/import/csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            status, error = kb.import_csv(file.stream)
            if status:
                flash('Данные успешно импортированы', 'success')
            else:
                flash(f'Ошибка импорта: {error}', 'danger')
            return redirect(url_for('index'))
    
    return render_template('import.html')

if __name__ == '__main__':
    app.run(debug=True)
