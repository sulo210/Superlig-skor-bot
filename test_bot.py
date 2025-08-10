import os
from telegram import Bot
from dotenv import load_dotenv

# .env dosyasını oku
load_dotenv()

TOKEN = os.getenv("8303788629:AAEgokHsoca098m2lBZQKF_jQzsHXp7PRKg")
CHAT_ID = os.getenv("-1002664199588")

if not TOKEN or not CHAT_ID:
    print("❌ TOKEN veya CHAT_ID bulunamadı. .env dosyasını kontrol et.")
    exit()

bot = Bot(token=TOKEN)
bot.send_message(chat_id=CHAT_ID, text="Bot başarıyla çalışıyor! 🎉")
print("✅ Test mesajı gönderildi.")
