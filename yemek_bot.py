import schedule
import time
from datetime import datetime
import requests
import os
import PyPDF2
import re

# Ortam değişkenlerinden al (Render'da ayarlayacağız)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
PDF_DOSYASI = "yemek_listesi.pdf"

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

def pdf_oku():
    """PDF'den bugünün menüsünü okur"""
    try:
        with open(PDF_DOSYASI, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Bugünün tarihini formatla (örn: "1 Eylül 2025 Pazartesi")
            bugun = datetime.now()
            gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            
            gun_adi = gun_adlari[bugun.weekday()]
            ay_adi = ay_adlari[bugun.month]
            tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
            
            print(f"Aranan tarih: {tarih_str}")
            
            # Tüm sayfaları tara
            for page in pdf_reader.pages:
                text = page.extract_text()
                
                # Bugünün tarihini bul
                if tarih_str in text:
                    # Tarihin bulunduğu satırdan sonraki içeriği al
                    lines = text.split('\n')
                    tarih_index = -1
                    
                    for i, line in enumerate(lines):
                        if tarih_str in line:
                            tarih_index = i
                            break
                    
                    if tarih_index != -1:
                        # Öğle yemeği ve akşam yemeği metinlerini bul
                        ogle_yemegi = []
                        aksam_yemegi = []
                        
                        # Basit parsing - tarihten sonraki satırları oku
                        collecting_ogle = False
                        collecting_aksam = False
                        
                        for i in range(tarih_index + 1, min(tarih_index + 30, len(lines))):
                            line = lines[i].strip()
                            
                            if 'ÖĞLE YEMEĞİ' in line or 'İLİM YAYMA' in line:
                                collecting_ogle = True
                                collecting_aksam = False
                                continue
                            elif 'AKŞAM YEMEĞİ' in line:
                                collecting_ogle = False
                                collecting_aksam = True
                                continue
                            elif any(gun in line for gun in gun_adlari):
                                # Yeni tarih başladı, dur
                                break
                            
                            if line and collecting_ogle:
                                ogle_yemegi.append(line)
                            elif line and collecting_aksam:
                                aksam_yemegi.append(line)
                        
                        # İlk 5-6 satırı al (genellikle menü bu kadar)
                        ogle_menu = '\n'.join(ogle_yemegi[:6]) if ogle_yemegi else "Bilgi yok"
                        aksam_menu = '\n'.join(aksam_yemegi[:6]) if aksam_yemegi else "Bilgi yok"
                        
                        return {
                            "oglen": ogle_menu,
                            "aksam": aksam_menu
                        }
            
            return None
            
    except Exception as e:
        print(f"❌ PDF okuma hatası: {e}")
        return None

def oglen_yemegi():
    """Öğlen 12:00'de öğle yemeği menüsünü gönderir"""
    menu = pdf_oku()
    if menu:
        mesaj = f"🌞 <b>Öğle Vakti!</b>\n\n🍽️ <b>Bugünün Öğle Yemeği:</b>\n{menu['oglen']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder("❌ Bugün için öğle yemeği menüsü bulunamadı.")

def aksam_yemegi():
    """Akşam 17:30'da akşam yemeği menüsünü gönderir"""
    menu = pdf_oku()
    if menu:
        mesaj = f"🌆 <b>Akşam Yemeği Zamanı!</b>\n\n🍲 <b>Bugünün Akşam Yemeği:</b>\n{menu['aksam']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder("❌ Bugün için akşam yemeği menüsü bulunamadı.")

# Zamanlamaları ayarla (Türkiye saati için UTC+3 -> UTC'ye çevir)
schedule.every().day.at("09:00").do(oglen_yemegi)   # 12:00 TR = 09:00 UTC
schedule.every().day.at("14:30").do(aksam_yemegi)   # 17:30 TR = 14:30 UTC

print("🤖 Bot başlatıldı!")
print("⏰ Zamanlanmış görevler:")
print("   - Öğlen 12:00 TR: Öğle yemeği menüsü")
print("   - Akşam 17:30 TR: Akşam yemeği menüsü")
print("\n🔄 Bot çalışıyor...")

while True:
    schedule.run_pending()
    time.sleep(60)