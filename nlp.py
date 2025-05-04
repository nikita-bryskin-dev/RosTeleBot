import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Загрузка NLTK-ресурсов (необходимо выполнить один раз)
# nltk.download('punkt_tab')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

# Предобработка текста
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = word_tokenize(text.lower())
    lemmatized = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(lemmatized)

# Загрузка базы вопросов
df = pd.read_csv('support_chatbot.csv')
df['processed'] = df['question'].apply(preprocess)

# Построение TF-IDF модели
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['processed'])

def get_bot_response(user_message):
    user_processed = preprocess(user_message)
    user_vector = vectorizer.transform([user_processed])

    similarities = cosine_similarity(user_vector, tfidf_matrix)
    best_match_idx = similarities.argmax()
    best_score = similarities[0][best_match_idx]

    if best_score > 0.4:  # порог уверенности
        return df['answer'][best_match_idx]
    else:
        return "Извините, я не совсем понял. Можете уточнить вопрос или связаться с оператором?"