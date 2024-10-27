import telebot
import openai
from gtts import gTTS
from pydub import AudioSegment
import os

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

# Функция для озвучивания текста с помощью gTTS и изменения голоса
def text_to_speech(text, lang='ru'):
    filename = "ded_speech.mp3"
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        
        # Постобработка с использованием pydub для изменения голоса
        sound = AudioSegment.from_file(filename)
        # Понижаем высоту тона (pitch) путем изменения частоты дискретизации
        new_sample_rate = int(sound.frame_rate * 0.7)
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        sound = sound.set_frame_rate(44100)
        sound.export(filename, format="mp3")
        
        return filename
    except Exception as e:
        print(f"Ошибка при создании аудио файла: {e}")
        return None

# Функция для отправки голосового сообщения
def send_voice_message(chat_id, text):
    speech_file = text_to_speech(text)
    if speech_file and os.path.exists(speech_file):
        with open(speech_file, 'rb') as audio:
            bot.send_voice(chat_id, audio)
        os.remove(speech_file)
    else:
        bot.send_message(chat_id, "Не удалось создать голосовое сообщение.")

# Функция для общения с нейросетью OpenAI с вредным ответом
def ask_openai(text):
    try:
        chat_completion = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Ты старый и вредный дед, который отвечает на вопросы с ворчливым и грубым тоном. Но всё же отвечай на вопросы и помогай людям, хоть и через свои ворчания."},
                {"role": "user", "content": text}
            ]
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
    response_text = (
        "Привет, внучек! Я Дед, я буду тебя воспитывать и помогать тебе, шко-лоло! "
        "Отправь мне сообщение, и я его повторю. "
        "Используй команду /deda, чтобы задать мне вопрос. "
        "Для домашки используй команду /perevorot, чтобы перевернуть текст, "
        "команду /caps, чтобы преобразовать текст в заглавные буквы, и команду /cut, чтобы удалить все гласные буквы из текста."
    )
    bot.reply_to(message, response_text)
    send_voice_message(message.chat.id, response_text)

# Обработка команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "Вот что я могу делать, внучек:\n"
        "/start - Приветственное сообщение от деда.\n"
        "/help - Показать это сообщение.\n"
        "/deda <текст> - Задать вопрос вредному деду.\n"
        "/perevorot <текст> - Перевернуть текст задом наперед.\n"
        "/caps <текст> - Преобразовать текст в заглавные буквы.\n"
        "/cut <текст> - Удалить все гласные из текста.\n"
        "/mymessages - Показать все ваши сообщения.\n"
        "/allmessages - Показать все сообщения (только для администратора)."
    )
    bot.reply_to(message, help_text)

# Обработка команды /perevorot
@bot.message_handler(commands=['perevorot'])
def handle_perevorot(message):
    text = message.text.split(' ', 1)[-1].strip()
    if text:
        reversed_text = reverse_text(text)
        add_user_message(message.from_user.id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, reversed_text)
        send_voice_message(message.chat.id, reversed_text)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для переворачивания.")

# Обработка команды /caps
@bot.message_handler(commands=['caps'])
def handle_caps(message):
    text = message.text.split(' ', 1)[-1].strip()
    if text:
        uppercase_text = to_uppercase(text)
        add_user_message(message.from_user.id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, uppercase_text)
        send_voice_message(message.chat.id, uppercase_text)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для преобразования.")

# Обработка команды /cut
@bot.message_handler(commands=['cut'])
def handle_cut(message):
    text = message.text.split(' ', 1)[-1].strip()
    if text:
        text_without_vowels = remove_vowels(text)
        add_user_message(message.from_user.id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, text_without_vowels)
        send_voice_message(message.chat.id, text_without_vowels)
    else:
        bot.reply_to(message, "Ошибка: не указан текст для обработки.")

# Обработка команды /deda
@bot.message_handler(commands=['deda'])
def handle_deda(message):
    text = message.text.split(' ', 1)[-1].strip()
    if text:
        ai_response = ask_openai(text)
        add_user_message(message.from_user.id, text)  # Сохраняем сообщение пользователя
        bot.reply_to(message, ai_response)
        send_voice_message(message.chat.id, ai_response)
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
    add_user_message(message.from_user.id, message.text)  # Сохраняем сообщение пользователя
    bot.reply_to(message, message.text)
    send_voice_message(message.chat.id, message.text)

# Запуск бота
if __name__ == "__main__":
    print("Эхо-бот запущен...")
    bot.polling()
