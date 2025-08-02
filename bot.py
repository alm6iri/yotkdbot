import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
import ffmpeg

# إضافة مجلد bin إلى PATH ليجد ffmpeg وffprobe
os.environ["PATH"] += os.pathsep + os.path.abspath("bin")

# تحميل المتغيرات من البيئة
try:
    API_ID    = int(os.environ["API_ID"])
    API_HASH  = os.environ["API_HASH"]
    BOT_TOKEN = os.environ["BOT_TOKEN"]
except KeyError:
    raise RuntimeError("❌ تأكد من ضبط API_ID, API_HASH, BOT_TOKEN كمتغيرات بيئية")

# تهيئة بوت Pyrogram
app = Client("yotkdbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# مجلد التنزيلات
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# تخزين تفضيلات اللغة
user_languages = {}

# تحميل الرسائل متعددة اللغات
def load_messages():
    return {
        "choose_language": {
            "ar": "🌐 اختر اللغة:",
            "en": "🌐 Choose your language:",
            "ru": "🌐 Выберите язык:"
        },
        "send_link": {
            "ar": "📥 أرسل رابط فيديو من YouTube أو TikTok أو Twitter.",
            "en": "📥 Send me a video link from YouTube, TikTok, or Twitter.",
            "ru": "📥 Отправьте мне ссылку на видео с YouTube, TikTok или Twitter."
        },
        "select_download_type": {
            "ar": "📂 اختر نوع التحميل:",
            "en": "📂 Select download type:",
            "ru": "📂 Выберите тип загрузки:"
        },
        "downloading": {
            "ar": "🚀 جاري التحميل...",
            "en": "🚀 Downloading...",
            "ru": "🚀 Загрузка..."
        },
        "converting_audio": {
            "ar": "🎵 جاري تحويل الفيديو إلى صوت...",
            "en": "🎵 Converting video to audio...",
            "ru": "🎵 Конвертация видео в аудио..."
        },
        "done": {
            "ar": "✅ تم الإرسال!",
            "en": "✅ Sent successfully!",
            "ru": "✅ Отправлено!"
        },
        "error": {
            "ar": "❌ حدث خطأ: ",
            "en": "❌ An error occurred: ",
            "ru": "❌ Произошла ошибка: "
        }
    }

MESSAGES = load_messages()

# إعدادات yt-dlp مع دعم الكوكيز وهيدرات المتصفح
YDL_OPTS = {
    'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
    'format': 'best',
    'http_headers': {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36'
        ),
        'Referer': 'https://www.youtube.com/'
    },
    'cookiefile': 'cookies.txt',      # احفظ هنا كوكيز المتصفح بعد تصديرها
    'retries': 3,
    'socket_timeout': 15,
    'nocheckcertificate': True,
    'extractor_retries': 3,
    # 'proxy': os.environ.get('PROXY')  # فعّل إذا كنت بحاجة لبروكسي
}

def download_video(url):
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def convert_to_audio(video_path):
    audio_path = video_path.rsplit('.', 1)[0] + ".mp3"
    ffmpeg.input(video_path).output(audio_path).run()
    return audio_path

@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ])
    await message.reply(MESSAGES["choose_language"]["en"], reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^lang_"))
async def set_language(client, cq: CallbackQuery):
    lang = cq.data.split("_")[1]
    user_languages[cq.from_user.id] = lang
    await cq.message.edit_text(MESSAGES["send_link"][lang])

@app.on_message(filters.regex(r"(https?://\S+)"))
async def link_handler(client, message):
    lang = user_languages.get(message.from_user.id, "en")
    url = message.matches[0].group(1)
    texts = {
        'video': {'ar': 'تحميل فيديو', 'en': 'Download Video', 'ru': 'Скачать видео'},
        'audio': {'ar': 'تحميل صوت',  'en': 'Download Audio',  'ru': 'Скачать аудио'}
    }
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📹 {texts['video'][lang]}", callback_data=f"video|{url}")],
        [InlineKeyboardButton(f"🎵 {texts['audio'][lang]}", callback_data=f"audio|{url}")]
    ])
    await message.reply(MESSAGES["select_download_type"][lang], reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^(video|audio)\|"))
async def button_handler(client, cq: CallbackQuery):
    lang = user_languages.get(cq.from_user.id, "en")
    action, url = cq.data.split("|")
    msg = await cq.message.edit_text(MESSAGES["downloading"][lang])
    try:
        video_path = download_video(url)
        if action == "audio":
            await msg.edit_text(MESSAGES["converting_audio"][lang])
            audio_path = convert_to_audio(video_path)
            await client.send_audio(cq.message.chat.id, audio=audio_path)
        else:
            await client.send_video(cq.message.chat.id, video=video_path)
        await msg.edit_text(MESSAGES["done"][lang])
    except Exception as e:
        await msg.edit_text(MESSAGES["error"][lang] + str(e))
<<<<<<< HEAD
=======

>>>>>>> 5d2cd7cc1abec18f4b2fe97b3fb7b0c20b626930
app.run()
