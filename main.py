import requests
import time
import os
import json
from telegram import Bot

# === AYARLAR ===
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = 30  # saniye
STATE_FILE = "state.json"

bot = Bot(token=TOKEN)

# === DURUM KAYDI ===
sent_events = set()
sent_status = set()

def load_state():
    global sent_events, sent_status
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            sent_events = set(data.get("events", []))
            sent_status = set(data.get("status", []))
    except FileNotFoundError:
        pass

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({"events": list(sent_events), "status": list(sent_status)}, f)

# === BAŞLANGIÇ MESAJI ===
bot.send_message(chat_id=CHAT_ID, text="Bot başarıyla çalışıyor! 🎉")
load_state()

# === MAÇ KONTROL FONKSİYONU ===
def check_matches():
    try:
        live_matches = requests.get(
            "https://api.sofascore.com/api/v1/sport/football/events/live",
            timeout=5
        ).json()

        for match in live_matches.get("events", []):
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            match_id = match["id"]
            status = match["status"]["type"]
            score_home = match["homeScore"]["current"]
            score_away = match["awayScore"]["current"]

            # --- Maç durumu bildirimleri ---
            if status == "inprogress" and f"{match_id}-start" not in sent_status:
                bot.send_message(chat_id=CHAT_ID, text=f"🏁 {home} vs {away} maçı başladı!")
                sent_status.add(f"{match_id}-start")

            elif status == "halftime" and f"{match_id}-ht" not in sent_status:
                bot.send_message(chat_id=CHAT_ID, text=f"⏸ İlk yarı bitti. Skor: {home} {score_home} - {score_away} {away}")
                sent_status.add(f"{match_id}-ht")

            elif status == "finished" and f"{match_id}-ft" not in sent_status:
                bot.send_message(chat_id=CHAT_ID, text=f"✅ Maç bitti! Skor: {home} {score_home} - {score_away} {away}")
                sent_status.add(f"{match_id}-ft")

            # --- Olayları çek ---
            incidents_url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
            incidents = requests.get(incidents_url, timeout=5).json()

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

                # --- Güncel skor kontrolü ---
                h_score = inc.get("homeScore", {}).get("current", score_home)
                a_score = inc.get("awayScore", {}).get("current", score_away)

                # --- Olay türüne göre mesaj ---
                if type_ == "goal":
                    text = f"⚽ {minute}' | {player} gol attı! ({home} {h_score} - {a_score} {away})"
                elif type_ == "card":
                    emoji = "🟥" if detail == "red" else "🟨"
                    text = f"{emoji} {minute}' | {player} kart gördü!"
                elif type_ == "substitution":
                    text = f"🔄 {minute}' | Oyuncu değişikliği: {player}"
                else:
                    continue

                bot.send_message(chat_id=CHAT_ID, text=text)
                sent_events.add(event_id)
                save_state()

        save_state()

    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"⚠ Hata: {e}")

# === ANA DÖNGÜ ===
while True:
    check_matches()
    time.sleep(CHECK_INTERVAL)
