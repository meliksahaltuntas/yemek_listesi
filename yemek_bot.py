# ===== yemek_bot.py =====
import schedule
import time
import openpyxl
from datetime import datetime
import requests
import os

# Ortam değişkenlerinden al (Render'da ayarlayacağız)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
EXCEL_DOSYASI = "yemek_listesi.xlsx"

def mesaj_gonder(mesaj):
    """Telegram'a mesaj gönderen fonksiyon"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Mesaj gönderildi: {mesaj[:50]}...")
        else:
            print(f"❌ Hata: {response.text}")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

def excel_oku():
    """Excel'den bugünün menüsünü okur"""
    try:
        wb = openpyxl.load_workbook(EXCEL_DOSYASI)
        sheet = wb.active
        
        bugun = datetime.now().strftime("%d.%m.%Y")
        
        for row in sheet.iter_rows(min_row=2, values_only=False):
            tarih_cell = row[0].value
            
            if isinstance(tarih_cell, datetime):
                tarih_str = tarih_cell.strftime("%d.%m.%Y")
            else:
                tarih_str = str(tarih_cell)
            
            if tarih_str == bugun:
                sabah = row[1].value or "Bilgi yok"
                oglen = row[2].value or "Bilgi yok"
                aksam = row[3].value or "Bilgi yok"
                
                return {
                    "sabah": sabah,
                    "oglen": oglen,
                    "aksam": aksam
                }
        
        return None
        
    except Exception as e:
        print(f"❌ Excel okuma hatası: {e}")
        return None

def sabah_kahvaltisi():
    """Sabah 8:00'de kahvaltı menüsünü gönderir"""
    menu = excel_oku()
    if menu:
        mesaj = f"🌅 <b>Günaydın!</b>\n\n☕ <b>Bugünün Kahvaltısı:</b>\n{menu['sabah']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder("❌ Bugün için kahvaltı menüsü bulunamadı.")

def oglen_yemegi():
    """Öğlen 12:00'de öğle yemeği menüsünü gönderir"""
    menu = excel_oku()
    if menu:
        mesaj = f"🌞 <b>Öğle Vakti!</b>\n\n🍽️ <b>Bugünün Öğle Yemeği:</b>\n{menu['oglen']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder("❌ Bugün için öğle yemeği menüsü bulunamadı.")

def aksam_yemegi():
    """Akşam 17:30'da akşam yemeği menüsünü gönderir"""
    menu = excel_oku()
    if menu:
        mesaj = f"🌆 <b>Akşam Yemeği Zamanı!</b>\n\n🍲 <b>Bugünün Akşam Yemeği:</b>\n{menu['aksam']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder("❌ Bugün için akşam yemeği menüsü bulunamadı.")

# Zamanlamaları ayarla (Türkiye saati UTC+3)
schedule.every().day.at("05:00").do(sabah_kahvaltisi)   # UTC için 08:00 -> 05:00
schedule.every().day.at("09:00").do(oglen_yemegi)       # UTC için 12:00 -> 09:00
schedule.every().day.at("14:30").do(aksam_yemegi)       # UTC için 17:30 -> 14:30

print("🤖 Bot başlatıldı!")
print("⏰ Zamanlanmış görevler:")
print("   - Sabah 08:00 TR: Kahvaltı menüsü")
print("   - Öğlen 12:00 TR: Öğle yemeği menüsü")
print("   - Akşam 17:30 TR: Akşam yemeği menüsü")
print("\n🔄 Bot çalışıyor...")

while True:
    schedule.run_pending()
    time.sleep(60)

