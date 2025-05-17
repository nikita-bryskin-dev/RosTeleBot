import sqlite3
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from AI_bot.ai_bot import handle_user_message

# Инициализация NLTK
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = word_tokenize(text.lower())
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens]
    return " ".join(lemmatized)

# Подключение к SQLite и загрузка данных
def load_qa_from_db():
    conn = sqlite3.connect('DB/WebAppDB.db')
    df = pd.read_sql_query("SELECT question, answer FROM support_chatbot", conn)
    conn.close()
    return df

# Предобработка и обучение TF-IDF
df = load_qa_from_db()
df['processed'] = df['question'].apply(preprocess)
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['processed'])

# Основная функция обработки запроса
def get_bot_response(user_message):
    user_processed = preprocess(user_message)
    user_vector = vectorizer.transform([user_processed])

    similarities = cosine_similarity(user_vector, tfidf_matrix)
    best_match_idx = similarities.argmax()
    best_score = similarities[0][best_match_idx]

    if best_score > 0.4:
        return df['answer'][best_match_idx]
    else:
        return handle_user_message(user_message)