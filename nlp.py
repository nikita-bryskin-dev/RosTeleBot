from AI_bot.ai_bot import handle_user_message


def get_bot_response(user_message):
    message = user_message.lower()
    
    if "привет" in message:
        return "Здравствуйте! Чем могу помочь?"
    if "цена" in message:
        return "Цены зависят от конкретного товара. Уточните, пожалуйста."
    elif "оператор" in message or "связаться" in message:
        return "Секунду, сейчас подключу оператора."
    else:
       return handle_user_message(user_message)