import telebot
import random
import json
import os

# ============================================
#  PEGA TU NUEVO TOKEN AQUÍ
# ============================================
TOKEN = "8284166238:AAHP18lV3q7u-dQJ7bAJ5LZvI2pEOdyBVDQ"

DB_FILE = "videos.json"

bot = telebot.TeleBot(TOKEN)

# --- Cargar videos ---
def load_videos():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# --- Guardar video ---
def save_video(file_id):
    videos = load_videos()
    if file_id not in videos:
        videos.append(file_id)
        with open(DB_FILE, "w") as f:
            json.dump(videos, f)
        print(f"Video guardado: {file_id}")

# --- Obtener video aleatorio ---
def get_random_video():
    videos = load_videos()
    if not videos:
        return None
    return random.choice(videos)

# --- Leer historial ---
def fetch_history(chat_id):
    try:
        count = 0
        for msg in bot.get_chat_history(chat_id, limit=100):
            if msg.video:
                save_video(msg.video.file_id)
                count += 1
        print(f"Se encontraron {count} videos")
        return count
    except Exception as e:
        print(f"Error: {e}")
        return 0

# --- Detectar videos nuevos ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.type in ['group', 'supergroup']:
        try:
            save_video(message.video.file_id)
        except:
            pass

# --- Comando /video y /videos ---
@bot.message_handler(commands=['video', 'videos'])
def send_random_video(message):
    video_id = get_random_video()
    if video_id:
        bot.send_video(message.chat.id, video_id)
    else:
        bot.reply_to(message, "❌ No hay videos. Envía uno al grupo!")

# --- Comando /historial ---
@bot.message_handler(commands=['historial'])
def cmd_historial(message):
    try:
        count = fetch_history(message.chat.id)
        bot.reply_to(message, f"✅ Se encontraron {count} videos!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# --- Comando /start ---
@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, "🎬 Bot listo! /video para ver un video aleatorio.")

# --- Iniciar ---
print("Bot iniciado...")
bot.infinity_polling()
