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

# --- Leer historial del grupo ---
def fetch_history(chat_id, limit=200):
    try:
        count = 0
        print(f"Buscando videos en el historial...")
        
        # Iterar sobre los mensajes
        for msg in bot.get_chat_history(chat_id, limit=limit):
            if msg.video:
                save_video(msg.video.file_id)
                count += 1
        
        print(f"Se encontraron {count} videos en el historial")
        return count
    except Exception as e:
        print(f"Error al leer historial: {e}")
        return 0

# --- Detectar videos nuevos ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.type in ['group', 'supergroup']:
        try:
            save_video(message.video.file_id)
            print("Nuevo video guardado")
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
            bot.reply_to(message, f"❌ Error al enviar video. Prueba /historial primero.")
            print(f"Error: {e}")
    else:
        bot.reply_to(message, "❌ No hay videos. Usa /historial para buscarlos.")

# --- Comando /historial ---
@bot.message_handler(commands=['historial'])
def cmd_historial(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ Este comando solo funciona en grupos.")
        return
    
    bot.reply_to(message, "🔍 Buscando videos en el historial...")
    try:
        count = fetch_history(message.chat.id, limit=200)
        if count > 0:
            bot.reply_to(message, f"✅ Se encontraron {count} videos! Ahora usa /video")
        else:
            bot.reply_to(message, "❌ No se encontraron videos en el historial.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# --- Comando /changelog ---
@bot.message_handler(commands=['changelog'])
def cmd_changelog(message):
    changelog = """
📋 CHANGELOG - Bot de Videos
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 20/01/2025

🆕 Novedades:
- Comando /historial para cargar videos antiguos
- Comando /changelog agregado
- El bot ahora guarda videos automáticamente

🐛 Arreglos:
- Mejora en la lectura del historial

⚙️ Mejoras:
- Optimizado para grupos grandes

📌 Nota: Usa /historial la primera vez para cargar videos
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, changelog)

# --- Comando /start ---
@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, "🎬 Bot listo!\n\n📌 Usa /historial para cargar videos del grupo\n🎥 Usa /video para ver uno aleatorio")

# --- Iniciar ---
print("Bot iniciado...")

bot.infinity_polling()
