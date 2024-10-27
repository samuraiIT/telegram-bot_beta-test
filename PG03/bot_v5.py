import telebot
import openai

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, который вы получили от BotFather
API_TOKEN = '***'
bot = telebot.TeleBot(API_TOKEN)

# Установите свой API-ключ
api_key = "***"
# Установите базовый URL
base_url = "https://api.proxyapi.ru/openai/v1"
# Установите свою языковую модель
model_name = "gpt-3.5-turbo-1106"
# Установите ID администратора
admin_id = 5842551033  # Замените на ваш реальный user_id

# Настройка клиента OpenAI
openai.api_key = api_key
openai.api_base = base_url

# Словарь для хранения сообщений пользователей
user_messages = {}

# Функция для переворачивания текста
def reverse_text(text):
    return text[::-1]

# Функция для преобразования текста в заглавные буквы
def to_uppercase(text):
    return text.upper()

# Функция для удаления гласных из текста
def remove_vowels(text):
    # Гласные буквы для английского и русского языков
    vowels = 'aeiouAEIOUаеёиоуыэюяАЕЁИОУЫЭЮЯ'
    return ''.join(char for char in text if char not in vowels)

# Функция для общения с нейросетью OpenAI
def ask_openai(text):
    try:
        chat_completion = openai.ChatCompletion.create(
            model=model_name,
            # messages=[{"role": "user", "content": text}]
            messages=[{"role": "system", "content": "Отвечай на вопросы в стиле борзого, наглого деда"}]
        )
        ai_response = chat_completion.choices[0].message["content"]
        return ai_response
    except Exception as e:
        return f"Произошла ошибка: {e}"

# Функция для добавления сообщения пользователя в словарь
def add_user_message(user_id, message):
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(message)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Привет внучек! Я Дед, я буду тебя воспитывать и помогать тебе, Шко-лоло! Отправьте мне сообщение, и я его повторю. Используй команду /deda, чтобы задать мне вопрос. Для домашки используй команду /perevorot, чтобы перевернуть текст, команду /caps, чтобы преобразовать текст в заглавные буквы, команду /cut, чтобы удалить все гласные буквы из текста.")

# Обработка команды /perevorot
@bot.message_handler(commands=['perevorot'])
def handle_perevorot(message):
    user_id = message.from_user.id
    text = message.text[len('/perevorot '):].strip()
    if text:
        reversed_text = reverse_text(text)
        add_user_message(user_id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, reversed_text)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для переворачивания.")

# Обработка команды /caps
@bot.message_handler(commands=['caps'])
def handle_caps(message):
    user_id = message.from_user.id
    text = message.text[len('/caps '):].strip()
    if text:
        uppercase_text = to_uppercase(text)
        add_user_message(user_id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, uppercase_text)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для преобразования.")

# Обработка команды /cut
@bot.message_handler(commands=['cut'])
def handle_cut(message):
    user_id = message.from_user.id
    text = message.text[len('/cut '):].strip()
    if text:
        text_without_vowels = remove_vowels(text)
        add_user_message(user_id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, text_without_vowels)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для обработки.")

# Обработка команды /deda
@bot.message_handler(commands=['deda'])
def handle_deda(message):
    user_id = message.from_user.id
    text = message.text[len('/deda '):].strip()
    if text:
        ai_response = ask_openai(text)
        add_user_message(user_id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, ai_response)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для запроса к нейросети.")

# Обработка команды /mymessages для вывода всех сообщений пользователя
@bot.message_handler(commands=['mymessages'])
def handle_mymessages(message):
    user_id = message.from_user.id
    if user_id in user_messages:
        messages = user_messages[user_id]
        if messages:
            bot.reply_to(message, "\n".join(messages))
        else:
            bot.reply_to(message, "У вас нет сохраненных сообщений.")
    else:
        bot.reply_to(message, "У вас нет сохраненных сообщений.")

# Обработка команды /allmessages для вывода всех сообщений (может быть только для администратора)
@bot.message_handler(commands=['allmessages'])
def handle_allmessages(message):
    if message.from_user.id == admin_id:
        all_messages = []
        for user_id, messages in user_messages.items():
            all_messages.append(f"Сообщения от пользователя {user_id}:\n" + "\n".join(messages))
        if all_messages:
            bot.reply_to(message, "\n\n".join(all_messages))
        else:
            bot.reply_to(message, "Нет сохраненных сообщений.")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Обработка всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    add_user_message(user_id, message.text)  # Сохраняем сообщение пользователя
    bot.reply_to(message, message.text)

# Запуск бота
if __name__ == "__main__":
    print("Эхо-бот запущен...")
    bot.polling()
