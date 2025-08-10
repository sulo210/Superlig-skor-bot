import requests
import time
import os
from telegram import Bot
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

TOKEN = os.getenv("8303788629:AAEgokHsoca098m2lBZQKF_jQzsHXp7PRKg")
CHAT_ID = os.getenv("-1002664199588")
CHECK_INTERVAL = 30

bot = Bot(token=TOKEN)

# MANUEL TEST MESAJI
bot.send_message(chat_id=CHAT_ID, text="Bot başarıyla çalışıyor! 🎉")

sent_events = set()
sent_status = set()

def check_matches():
    try:
        live_matches = requests.get(
            "https://api.sofascore.com/api/v1/sport/football/events/live"
        ).json()

        for match in live_matches.get("events", []):
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            match_id = match["id"]
            status = match["status"]["type"]
            score_home = match["homeScore"]["current"]
            score_away = match["awayScore"]["current"]

            if status == "inprogress" and f"{match_id}-start" not in sent_status:
                bot.send_message(chat_id=CHAT_ID, text=f"🏁 {home} vs {away} maçı başladı!")
                sent_status.add(f"{match_id}-start")

            elif status == "halftime" and f"{match_id}-ht" not in sent_status:
                bot.send_message(chat_id=CHAT_ID, text=f"⏸ İlk yarı bitti. Skor: {home} {score_home} - {score_away} {away}")
                sent_status.add(f"{match_id}-ht")

            elif status == "finished" and f"{match_id}-ft" not in sent_status:
                bot.send_message(chat_id=CHAT_ID, text=f"✅ Maç bitti! Skor: {home} {score_home} - {score_away} {away}")
                sent_status.add(f"{match_id}-ft")

            incidents_url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
            incidents = requests.get(incidents_url).json()

            for inc in incidents.get("incidents", []):
                if not isinstance(inc, dict):
                    continue

                minute = inc.get("time", "")
                player = inc.get("player", {}).get("name", "Bilinmiyor")
                type_ = inc.get("incidentType", "")
                detail = inc.get("incidentClass", "")

                event_id = f"{match_id}-{minute}-{player}-{type_}-{detail}"
                if event_id in sent_events:
                    continue

                if type_ == "goal":
                    text = f"⚽ {minute}' | {player} gol attı! ({home} {score_home} - {score_away} {away})"
                elif type_ == "card":
                    emoji = "🟥" if detail == "red" else "🟨"
                    text = f"{emoji} {minute}' | {player} kart gördü!"
                elif type_ == "substitution":
                    text = f"🔄 {minute}' | Oyuncu değişikliği: {player}"
                else:
                    continue

                bot.send_message(chat_id=CHAT_ID, text=text)
                sent_events.add(event_id)

    except Exception as e:
        print("Hata:", e)

while True:
    check_matches()
    time.sleep(CHECK_INTERVAL)
