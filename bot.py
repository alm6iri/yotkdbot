import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
import ffmpeg

# إعداد PATH لاستخدام FFmpeg من bin/
os.environ["PATH"] += os.pathsep + os.path.abspath("bin")

# متغيرات البيئة
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# لغات المستخدمين (user_id: language_code)
user_languages = {}

# الردود حسب اللغة
MESSAGES = {
    "choose_language": {
        "ar": "🌐 اختر اللغة:",
        "en": "🌐 Choose your language:",
        "ru": "🌐 Выберите язык:",
    },
    "send_link": {
        "ar": "📥 أرسل رابط فيديو من YouTube أو TikTok أو Twitter.",
        "en": "📥 Send me a video link from YouTube, TikTok, or Twitter.",
        "ru": "📥 Отправьте мне ссылку на видео с YouTube, TikTok или Twitter.",
    },
    "select_download_type": {
        "ar": "📂 اختر نوع التحميل:",
        "en": "📂 Select download type:",
        "ru": "📂 Выберите тип загрузки:",
    },
    "downloading": {
        "ar": "🚀 جاري التحميل...",
        "en": "🚀 Downloading...",
        "ru": "🚀 Загрузка...",
    },
    "converting_audio": {
        "ar": "🎵 جاري تحويل الفيديو إلى صوت...",
        "en": "🎵 Converting video to audio...",
        "ru": "🎵 Конвертация видео в аудио...",
    },
    "done": {
        "ar": "✅ تم الإرسال!",
        "en": "✅ Sent successfully!",
        "ru": "✅ Отправлено!",
    },
    "error": {
        "ar": "❌ حدث خطأ: ",
        "en": "❌ An error occurred: ",
        "ru": "❌ Произошла ошибка: ",
    }
}

# تحميل الفيديو
def download_video(url):
    with YoutubeDL({'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s', 'format': 'best'}) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# تحويل الفيديو إلى صوت
def convert_to_audio(video_path):
    audio_path = video_path.rsplit('.', 1)[0] + ".mp3"
    ffmpeg.input(video_path).output(audio_path).run()
    return audio_path

# بدء المحادثة واختيار اللغة
@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
        ]
    )
    await message.reply(MESSAGES["choose_language"]["en"], reply_markup=keyboard)

# حفظ اللغة المختارة
@app.on_callback_query(filters.regex("lang_"))
async def set_language(client, callback_query: CallbackQuery):
    lang_code = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    user_languages[user_id] = lang_code

    await callback_query.message.edit_text(MESSAGES["send_link"][lang_code])

# التعامل مع الروابط المرسلة
@app.on_message(filters.regex(r'(https?://\S+)'))
async def link_handler(client, message):
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "en")
    url = message.matches[0].group(1)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📹 " + ("تحميل فيديو" if lang == "ar" else "Download Video" if lang == "en" else "Скачать видео"), callback_data=f"video|{url}")],
            [InlineKeyboardButton("🎵 " + ("تحميل صوت" if lang == "ar" else "Download Audio" if lang == "en" else "Скачать аудио"), callback_data=f"audio|{url}")]
        ]
    )

    await message.reply(MESSAGES["select_download_type"][lang], reply_markup=keyboard)

# التعامل مع الضغط على أزرار التحميل
@app.on_callback_query(filters.regex(r'(video|audio)\|'))
async def button_handler(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_languages.get(user_id, "en")

    action, url = callback_query.data.split('|')

    msg = await callback_query.message.edit_text(MESSAGES["downloading"][lang])

    try:
        video_path = download_video(url)

        if action == "audio":
            await msg.edit_text(MESSAGES["converting_audio"][lang])
            output_path = convert_to_audio(video_path)
            await client.send_audio(callback_query.message.chat.id, audio=output_path)
        else:
            await client.send_video(callback_query.message.chat.id, video=video_path)

        await msg.edit_text(MESSAGES["done"][lang])

    except Exception as e:
        await msg.edit_text(MESSAGES["error"][lang] + str(e))

app.run()
