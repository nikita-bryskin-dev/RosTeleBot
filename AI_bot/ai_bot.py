import json
import os
import time
import spacy
from g4f.client import Client

client = Client()
nlp = spacy.load("ru_core_news_sm")

DIALOG_FILE = "AI_bot/Dialog_memory.txt"
PROMPT_FILE = "AI_bot/Rules_Bot_Init.txt"
FEEDBACK_FILE = "AI_bot/Feedback.txt"
last_message_time = time.time()

def read_file(path):
    if not os.path.exists(path): return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def write_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def append_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(data)

def load_prompt():
    base = read_file(PROMPT_FILE)
    feedback = read_file(FEEDBACK_FILE)
    return f"{base}\n\n{feedback}".strip()

def load_messages():
    if os.path.exists(DIALOG_FILE):
        with open(DIALOG_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = []
    if not messages:
        messages.append({"role": "system", "content": load_prompt()})
    return messages

def save_messages(messages):
    with open(DIALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def end_dialog():
    save_messages([{"role": "system", "content": load_prompt()}])

def detect_command(user_input):
    doc = nlp(user_input)
    for token in doc:
        if token.lemma_ == "оператор":
            return "Хорошо, перевожу вас на оператора."
    return None

def detect_feedback(user_input):
    doc = nlp(user_input)
    lemmas = [token.lemma_ for token in doc]
    if "спасибо" in lemmas or "благодарить" in lemmas:
        return "positive"
    elif "помочь" in lemmas and any(t.text == "не" for t in doc):
        return "negative"
    elif "плохо" in lemmas or "бесполезный" in lemmas or "неполезный" in lemmas:
        return "negative"
    return None

def collect_feedback(user_input, messages):
    feedback_type = detect_feedback(user_input)
    if feedback_type and len(messages) >= 2:
        question = messages[-2]['content']
        answer = messages[-1]['content']
        if feedback_type == "positive":
            feedback = "Положительный фидбэк: Спасибо за помощь!"
            annotated = f"\nПример твоего хорошего ответа:\nВопрос: {question}\nОтвет: {answer}\n"
        else:
            feedback = "Отрицательный фидбэк: Ответ не был полезен."
            annotated = f"\nПример твоего плохого ответа:\nВопрос: {question}\nОтвет: {answer}\n"

        entry = f"Вопрос: {question}\nОтвет: {answer}\nОценка: {feedback}\n\n"
        append_file(FEEDBACK_FILE, entry)
        append_file(PROMPT_FILE, annotated)
        return "Спасибо за вашу обратную связь! Мы ценим ваше мнение."
    return None

def handle_user_message(user_input):
    global last_message_time
    user_input = user_input.strip()
    last_message_time = time.time()

    messages = load_messages()
    fb_response = collect_feedback(user_input, messages)
    if fb_response:
        return fb_response

    command_response = detect_command(user_input)
    if command_response:
        end_dialog()
        return command_response

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            web_search=False
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при обращении: {e}")
        return "Произошла ошибка при обращении к модели."

    messages.append({"role": "assistant", "content": answer})
    save_messages(messages)
    return answer
