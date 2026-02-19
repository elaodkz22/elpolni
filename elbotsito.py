import telebot
import random
import json
import os

TOKEN = "8284166238:AAHP18lV3q7u-dQJ7bAJ5LZvI2pEOdyBVDQ"

DB_FILE = "videos.json"
USED_FILE = "used_videos.json"

bot = telebot.TeleBot(TOKEN)

# =========================
# DB HELPERS
# =========================
def load_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# LOAD DATA
# =========================
def load_videos():
    return load_json(DB_FILE)

def load_used():
    return load_json(USED_FILE)

# =========================
# SAVE VIDEO (30s - 60s)
# =========================
def save_video(file_id, duration):

    # SOLO ENTRE 30 Y 60 SEG
    if duration < 30 or duration > 60:
        print("⛔ Video ignorado por duración:", duration)
        return

    videos = load_videos()

    if file_id not in videos:
        videos.append(file_id)
        save_json(DB_FILE, videos)
        print("✅ Video guardado:", file_id)

# =========================
# RANDOM SIN REPETIR
# =========================
def get_random_video():

    videos = load_videos()
    used = load_used()

    # Si no hay videos
    if len(videos) == 0:
        return None

    # Reset si ya se usaron todos
    if len(used) >= len(videos):
        print("🔄 Reiniciando lista random")
        used = []
        save_json(USED_FILE, used)

    # Videos disponibles
    available = list(set(videos) - set(used))

    if not available:
        return None

    selected = random.choice(available)

    used.append(selected)
    save_json(USED_FILE, used)

    return selected

# =========================
# GUARDAR VIDEOS NUEVOS
# =========================
@bot.message_handler(content_types=['video'])
def handle_video(message):

    if message.chat.type in ['group', 'supergroup']:

        try:
            file_id = message.video.file_id
            duration = message.video.duration

            save_video(file_id, duration)

        except Exception as e:
            print("Error guardando video:", e)

# =========================
# COMANDO RANDOM
# =========================
@bot.message_handler(commands=['video'])
def send_random_video(message):

    video_id = get_random_video()

    if video_id is None:
        bot.reply_to(message, "❌ No hay videos válidos aún (30s - 60s)")
        return

    try:
        bot.send_video(message.chat.id, video_id)
    except Exception as e:
        print(e)
        bot.reply_to(message, "❌ Error enviando video")

# =========================
# STATS
# =========================
@bot.message_handler(commands=['stats'])
def stats(message):

    total = len(load_videos())
    used = len(load_used())

    bot.reply_to(message,
f"""
📊 ESTADÍSTICAS

🎬 Videos totales: {total}
♻️ Ya usados ciclo actual: {used}
🎯 Restantes sin repetir: {total - used}
""")

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
"""
🎬 BOT VIDEO RANDOM PRO

✅ Solo guarda videos 30s - 60s
🔁 Random sin repetir
🔄 Auto reinicio cuando termina lista

Comandos:
/video → Video random
/stats → Estadísticas
""")

print("🚀 BOT ONLINE")
bot.infinity_polling()
