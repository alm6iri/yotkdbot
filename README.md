# Telegram Video/Audio Downloader Bot

يدعم اللغات: العربية 🇸🇦، English 🇬🇧، Русский 🇷🇺

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/alm6iri/yotkdbot)# yotkdbot

## Usage
1. Click **Deploy to Heroku**.
2. Set Config Vars:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
3. Enable the **worker** dyno under **Resources**.

## Local Run
```bash
# install dependencies
git clone https://github.com/alm6iri/yotkdbot.git
cd yotkdbot
pip install -r requirements.txt
# set env vars and run
export API_ID=...
export API_HASH=...
export BOT_TOKEN=...
<<<<<<< HEAD
python bot.py
=======
python bot.py
>>>>>>> 5d2cd7cc1abec18f4b2fe97b3fb7b0c20b626930
