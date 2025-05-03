def get_bot_response(user_message):
    message = user_message.lower()
    
    if "привет" in message:
        return "Здравствуйте! Чем могу помочь?"
    elif "цена" in message:
        return "Цены зависят от конкретного товара. Уточните, пожалуйста."
    elif "оператор" in message or "связаться" in message:
        return "Секунду, сейчас подключу оператора."
    else:
        return "Извините, я не совсем понял. Можете переформулировать?"