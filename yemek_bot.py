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
            
            from datetime import timezone, timedelta
            tr_timezone = timezone(timedelta(hours=3))
            bugun = datetime.now(tr_timezone)
            
            gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            
            gun_adi = gun_adlari[bugun.weekday()]
            ay_adi = ay_adlari[bugun.month]
            tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
            
            print(f"Aranan tarih: {tarih_str}")
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                
                if tarih_str in text:
                    # Tarihin yanındaki tüm metni al
                    tarih_index = text.find(tarih_str)
                    remaining_text = text[tarih_index + len(tarih_str):]
                    
                    # Bir sonraki tarihe kadar olan kısmı al
                    next_date_index = len(remaining_text)
                    for gun in gun_adlari:
                        for ay in ay_adlari[1:]:
                            pattern = f"{ay} 2025 {gun}"
                            idx = remaining_text.find(pattern)
                            if idx > 0 and idx < next_date_index:
                                next_date_index = idx
                    
                    menu_text = remaining_text[:next_date_index].strip()
                    
                    # Satırlara böl ve temizle
                    lines = [line.strip() for line in menu_text.split('\n') if line.strip()]
                    
                    # Satırları yaklaşık yarıya böl
                    mid = len(lines) // 2
                    ogle_menu = '\n'.join(lines[:mid])
                    aksam_menu = '\n'.join(lines[mid:])
                    
                    return {
                        "oglen": ogle_menu,
                        "aksam": aksam_menu
                    }
            
            print(f"❌ {tarih_str} tarihi PDF'de bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ PDF okuma hatası: {e}")
        return None
    """PDF'den bugünün menüsünü okur"""
    try:
        with open(PDF_DOSYASI, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            from datetime import timezone, timedelta
            tr_timezone = timezone(timedelta(hours=3))
            bugun = datetime.now(tr_timezone)
            
            gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
            
            gun_adi = gun_adlari[bugun.weekday()]
            ay_adi = ay_adlari[bugun.month]
            tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
            
            print(f"Aranan tarih: {tarih_str}")
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                
                if tarih_str in text:
                    lines = text.split('\n')
                    
                    for i, line in enumerate(lines):
                        if tarih_str in line:
                            # Tarih satırından sonraki satırları topla
                            # PDF'de format: Tarih | Öğle yemekleri | Akşam yemekleri
                            menu_lines = []
                            for j in range(i+1, min(i+20, len(lines))):
                                next_line = lines[j].strip()
                                # Yeni tarih başladıysa dur
                                if any(gun in next_line for gun in gun_adlari) and any(ay in next_line for ay in ay_adlari):
                                    break
                                if next_line:
                                    menu_lines.append(next_line)
                            
                            # Satırları ikiye böl - ilk yarısı öğle, ikinci yarısı akşam
                            mid = len(menu_lines) // 2
                            ogle_menu = '\n'.join(menu_lines[:mid]) if menu_lines[:mid] else "Bilgi yok"
                            aksam_menu = '\n'.join(menu_lines[mid:]) if menu_lines[mid:] else "Bilgi yok"
                            
                            print(f"Bulunan menü - Öğle: {ogle_menu[:50]}...")
                            
                            return {
                                "oglen": ogle_menu,
                                "aksam": aksam_menu
                            }
            
            print(f"❌ {tarih_str} tarihi PDF'de bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ PDF okuma hatası: {e}")
        return None
    """PDF'den bugünün menüsünü okur"""
    try:
        with open(PDF_DOSYASI, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
             # İlk sayfayı yazdır - DEBUG
            first_page_text = pdf_reader.pages[0].extract_text()
            print("📄 PDF İlk Sayfa İçeriği:")
            print(first_page_text[:500])  # İlk 500 karakter
            print("---")

            # Türkiye saati için timezone-aware datetime (UTC+3)
            from datetime import timezone, timedelta
            tr_timezone = timezone(timedelta(hours=3))
            bugun = datetime.now(tr_timezone)
            
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
                    lines = text.split('\n')
                    tarih_index = -1
                    
                    for i, line in enumerate(lines):
                        if tarih_str in line:
                            tarih_index = i
                            break
                    
                    if tarih_index != -1:
                        ogle_yemegi = []
                        aksam_yemegi = []
                        
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
                                break
                            
                            if line and collecting_ogle:
                                ogle_yemegi.append(line)
                            elif line and collecting_aksam:
                                aksam_yemegi.append(line)
                        
                        ogle_menu = '\n'.join(ogle_yemegi[:6]) if ogle_yemegi else "Bilgi yok"
                        aksam_menu = '\n'.join(aksam_yemegi[:6]) if aksam_yemegi else "Bilgi yok"
                        
                        return {
                            "oglen": ogle_menu,
                            "aksam": aksam_menu
                        }
            
            print(f"❌ {tarih_str} tarihi PDF'de bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ PDF okuma hatası: {e}")
        return None

def oglen_yemegi():
    """Öğlen 12:00'de öğle yemeği menüsünü gönderir"""
    print("🔍 oglen_yemegi fonksiyonu çağrıldı")
    
    # Tarihi hazırla
    from datetime import timezone, timedelta
    tr_timezone = timezone(timedelta(hours=3))
    bugun = datetime.now(tr_timezone)
    gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    gun_adi = gun_adlari[bugun.weekday()]
    ay_adi = ay_adlari[bugun.month]
    tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
    
    menu = pdf_oku()
    print(f"🔍 pdf_oku sonucu: {menu}")
    if menu:
        mesaj = f"🌞 <b>{tarih_str} - Öğle Vakti!</b>\n\n🍽️ <b>Bugünün Öğle Yemeği:</b>\n{menu['oglen']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder(f"❌ {tarih_str} için öğle yemeği menüsü bulunamadı.")

def aksam_yemegi():
    """Akşam 17:30'da akşam yemeği menüsünü gönderir"""
    # Tarihi hazırla
    from datetime import timezone, timedelta
    tr_timezone = timezone(timedelta(hours=3))
    bugun = datetime.now(tr_timezone)
    gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    ay_adlari = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    gun_adi = gun_adlari[bugun.weekday()]
    ay_adi = ay_adlari[bugun.month]
    tarih_str = f"{bugun.day} {ay_adi} {bugun.year} {gun_adi}"
    
    menu = pdf_oku()
    if menu:
        mesaj = f"🌆 <b>{tarih_str} - Akşam Yemeği Zamanı!</b>\n\n🍲 <b>Bugünün Akşam Yemeği:</b>\n{menu['aksam']}"
        mesaj_gonder(mesaj)
    else:
        mesaj_gonder(f"❌ {tarih_str} için akşam yemeği menüsü bulunamadı.")

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