import telebot
import random
import json
import os
import time

# ============================================
#  PEGA TU NUEVO TOKEN AQUÍ (del @BotFather)
# ============================================
TOKEN = "8284166238:AAHUle0r4GpssSe2P67yvwPxkEv5E_4xAcI"  

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

# --- Leer historial del grupo ---
def fetch_history(chat_id, limit=1000):
    print(f"Buscando videos en el historial...")
    try:
        videos_found = 0
        # get_chat_history devuelve un generador, necesitamos iterar
        messages = bot.get_chat_history(chat_id, limit=limit)
        
        for msg in messages:
            if msg.video:
                save_video(msg.video.file_id)
                videos_found += 1
        
        print(f"Se encontraron {videos_found} videos en el historial.")
    except Exception as e:
        print(f"Error al leer historial: {e}")

# --- Detectar videos nuevos ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.type in ['group', 'supergroup']:
        try:
            save_video(message.video.file_id)
            print(f"Nuevo video detectado y guardado")
        except Exception as e:
            print(f"Error: {e}")

# --- Comando /video y /videos ---
@bot.message_handler(commands=['video', 'videos'])
def send_random_video(message):
    video_id = get_random_video()
    if video_id:
        try:
            bot.send_video(message.chat.id, video_id)
        except Exception as e:
            bot.reply_to(message, f"❌ Error al enviar video: {str(e)}")
    else:
        bot.reply_to(message, "❌ No encontré videos aún. Envía algunos videos al grupo!")

# --- Comando /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎬 Bot activo! Escribe /video o /videos para ver un video aleatorio del grupo.")

# --- Comando /actualizar (para recargar historial) ---
@bot.message_handler(commands=['actualizar', 'reload'])
def update_history(message):
    try:
        fetch_history(message.chat.id, limit=500)
        bot.reply_to(message, "✅ Historial actualizado!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# --- Iniciar bot ---
print("Bot iniciado...")

# Este es el ID de tu grupo (debes cambiarlo)
# Para obtenerlo, agrega @userinfobot a tu grupo y te dará el ID
GRUPO_ID = -100XXXXXXXXX  # <-- CAMBIA ESTO

# Cargar historial al iniciar (solo si tienes el ID correcto)
if GRUPO_ID != -100XXXXXXXXX:
    fetch_history(GRUPO_ID, limit=500)

bot.infinity_polling()