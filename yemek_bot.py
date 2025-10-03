import schedule
import time
from datetime import datetime, timezone, timedelta
import requests
import os
import openpyxl

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
        
        # Türkiye saati
        tr_timezone = timezone(timedelta(hours=3))
        bugun = datetime.now(tr_timezone)
        
        print(f"Bugünün tarihi: {bugun.strftime('%d.%m.%Y')}")
        
        # Excel'de bugünün satırını bul
        for row in sheet.iter_rows(min_row=2, values_only=False):
            tarih_cell = row[0].value
            
            # Tarih formatını kontrol et
            if isinstance(tarih_cell, datetime):
                tarih_str = tarih_cell.strftime("%d.%m.%Y")
            else:
                # String ise direkt kullan
                tarih_str = str(tarih_cell).strip() if tarih_cell else ""
            
            bugun_str = bugun.strftime("%d.%m.%Y")
            
            print(f"Kontrol ediliyor: {tarih_str} == {bugun_str}")
            
            if tarih_str == bugun_str:
                oglen = row[1].value or "Bilgi yok"
                aksam = row[2].value or "Bilgi yok"
                
                print(f"✅ Bugünün menüsü bulundu!")
                
                return {
                    "oglen": str(oglen).strip(),
                    "aksam": str(aksam).strip()
                }
        
        print(f"❌ {bugun_str} tarihi Excel'de bulunamadı")
        return None
        
    except Exception as e:
        print(f"❌ Excel okuma hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

def oglen_yemegi():
    """Öğlen 12:00'de öğle yemeği menüsünü gönderir"""
    print("🔍 oglen_yemegi fonksiyonu çağrıldı")
    
    # Tarihi hazırla
    tr_timezone = timezone(timedelta(hours=3))
    bugun = datetime.now(tr_timezone)
    gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    gun_adi = gun_adlari[bugun.weekday()]
    ay_adi = ay_adlari[bugun.month]
    tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
    
    menu = excel_oku()
    if menu:
        mesaj = f"🌞 <b>{tarih_str} - Öğle Vakti!</b>\n\n🍽️ <b>Bugünün Öğle Yemeği:</b>\n{menu['oglen']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder(f"❌ {tarih_str} için öğle yemeği menüsü bulunamadı.")

def aksam_yemegi():
    """Akşam 17:30'da akşam yemeği menüsünü gönderir"""
    # Tarihi hazırla
    tr_timezone = timezone(timedelta(hours=3))
    bugun = datetime.now(tr_timezone)
    gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    gun_adi = gun_adlari[bugun.weekday()]
    ay_adi = ay_adlari[bugun.month]
    tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
    
    menu = excel_oku()
    if menu:
        mesaj = f"🌆 <b>{tarih_str} - Akşam Yemeği Zamanı!</b>\n\n🍲 <b>Bugünün Akşam Yemeği:</b>\n{menu['aksam']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder(f"❌ {tarih_str} için akşam yemeği menüsü bulunamadı.")

# Zamanlamaları ayarla (Türkiye saati için UTC'ye çevir)
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