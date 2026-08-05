import os
import json
import uuid
from datetime import datetime, date
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- DOSYA YOLU ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LGS_DATA_FILE = os.path.join(SCRIPT_DIR, "lgs_denemeler.json")

# --- LGS DERS VE PUAN KATSAYILARI ---
LGS_LESSONS = {
    "Türkçe": {
        "soru_sayisi": 20,
        "katsayi": 4.0,
        "puan_kat": 3.67,
        "icon": "📖",
        "color": "#E91E63",
        "bolum": "Sözel"
    },
    "Matematik": {
        "soru_sayisi": 20,
        "katsayi": 4.0,
        "puan_kat": 4.95,
        "icon": "📐",
        "color": "#9C27B0",
        "bolum": "Sayısal"
    },
    "Fen Bilimleri": {
        "soru_sayisi": 20,
        "katsayi": 4.0,
        "puan_kat": 4.07,
        "icon": "🔬",
        "color": "#00BCD4",
        "bolum": "Sayısal"
    },
    "İnkılap Tarihi": {
        "soru_sayisi": 10,
        "katsayi": 1.0,
        "puan_kat": 1.68,
        "icon": "🇹🇷",
        "color": "#FF9800",
        "bolum": "Sözel"
    },
    "Din Kültürü": {
        "soru_sayisi": 10,
        "katsayi": 1.0,
        "puan_kat": 1.63,
        "icon": "🕌",
        "color": "#4CAF50",
        "bolum": "Sözel"
    },
    "İngilizce": {
        "soru_sayisi": 10,
        "katsayi": 1.0,
        "puan_kat": 1.45,
        "icon": "🌍",
        "color": "#3F51B5",
        "bolum": "Sözel"
    }
}

# --- LGS 8. SINIF MEB MÜFREDAT KAZANIMLARI (STANDART KÜTÜPHANE) ---
LGS_CURRICULUM = {
    "Türkçe": [
        "Fiilimsiler: İsim-Fiil (Mastar)",
        "Fiilimsiler: Sıfat-Fiil (Ortaç)",
        "Fiilimsiler: Zarf-Fiil (Bağ-Fiil / Ulaç)",
        "Sözcükte Anlam: Gerçek, Mecaz ve Terim Anlam",
        "Sözcükte Anlam: Eş / Zıt Anlam & Eş Seslilik",
        "Sözcükte Anlam: Deyimler ve Atasözleri",
        "Sözcükte Anlam: Söz Grupları ve İkilemeler",
        "Cümlede Anlam: Neden-Sonuç / Amaç-Sonuç / Koşul-Sonuç",
        "Cümlede Anlam: Öznel ve Nesnel Yargılar",
        "Cümlede Anlam: Örtülü Anlam ve Cümle Vurgusu",
        "Cümlede Anlam: Anlam İlişkileri (Tanım, Karşılaştırma, Olasılık, Varsayım)",
        "Paragrafta Anlam: Ana Düşünce (Ana Fikir) ve Konu",
        "Paragrafta Anlam: Yardımcı Düşünceler (Değinilmemiştir / Çıkarılamaz)",
        "Paragrafta Anlam: Paragrafın Yapısı (Giriş-Gelişme-Sonuç, Akışı Bozan Cümle)",
        "Paragrafta Anlam: Düşünceyi Geliştirme Yolları (Tanımlama, Örnekleme, Tanık Gösterme)",
        "Paragrafta Anlam: Anlatım Biçimleri (Açıklama, Tartışma, Öyküleme, Betimleme)",
        "Cümlenin Ögeleri: Temel Ögeler (Yüklem ve Özne)",
        "Cümlenin Ögeleri: Nesne (Belirtili ve Belirtisiz Nesne)",
        "Cümlenin Ögeleri: Yer Tamlayıcısı (Dolaylı Tümleç)",
        "Cümlenin Ögeleri: Zarf Tamlayıcısı (Zarf Tümleci) & Ara Söz",
        "Fiilde Çatı: Öznesine Göre (Etken ve Edilgen Çatı)",
        "Fiilde Çatı: Nesnesine Göre (Geçişli ve Geçişsiz Çatı)",
        "Cümle Türleri: Yüklemin Türüne Göre (İsim ve Fiil Cümleleri)",
        "Cümle Türleri: Yüklemin Yerine Göre (Kurallı ve Devrik Cümle)",
        "Cümle Türleri: Yapısına Göre (Tek Yüklemli, Fiilimsili, Sıralı, Bağlı Cümle)",
        "Metin Türleri: Olay / Düşünce / Bildirme Yazıları (Makale, Deneme, Fıkra, Hikaye, Biyografi)",
        "Söz Sanatları: Benzetme, Kişileştirme, Konuşturma, Tezat, Abartma",
        "Yazım Kuralları: Büyük Harfler, Kısaltmalar ve Sayıların Yazımı",
        "Yazım Kuralları: 'de', 'ki', 'mi' Ek ve Bağlaçlarının Yazımı",
        "Yazım Kuralları: Birleşik Sözcüklerin ve Ses Olaylı Sözcüklerin Yazımı",
        "Noktalama İşaretleri: Nokta, Virgül, Noktalı Virgül ve İki Nokta",
        "Noktalama İşaretleri: Üç Nokta, Soru, Ünlem, Tırnak ve Kesme İşareti",
        "Sözel Mantık: Akıl Yürütme, Sıralama ve Eşleştirme Muhakemesi",
        "Görsel Okuma: Tablo, Grafik, Karikatür ve İnfografik Yorumlama"
    ],
    "Matematik": [
        "Çarpanlar ve Katlar: Pozitif Tam Sayıların Çarpanları & Asal Çarpanlar",
        "Çarpanlar ve Katlar: EBOB ve EKOK Hesaplama",
        "Çarpanlar ve Katlar: EBOB - EKOK Problemleri",
        "Çarpanlar ve Katlar: Aralarında Asal Sayılar",
        "Üslü İfadeler: Tam Sayıların Tam Sayı Kuvvetleri (Negatif Üs)",
        "Üslü İfadeler: Üslü İfadelerle Çarpma ve Bölme İşlemleri",
        "Üslü İfadeler: Sayıların Ondalık Gösterimlerini Çözümleme",
        "Üslü İfadeler: Çok Büyük ve Çok Küçük Sayılar & Bilimsel Gösterim",
        "Kareköklü İfadeler: Tam Kare Sayılar ve Karekök Değerini Tahmin Etme",
        "Kareköklü İfadeler: a√b Şeklinde Yazma ve Katsayıyı Kök İçine Alma",
        "Kareköklü İfadeler: Kareköklü İfadelerde Çarpma ve Bölme İşlemleri",
        "Kareköklü İfadeler: Kareköklü İfadelerde Toplama ve Çıkarma İşlemleri",
        "Kareköklü İfadeler: Ondalık Gösterimlerin Karekökleri",
        "Kareköklü İfadeler: Gerçek Sayılar (Rasyonel ve İrrasyonel Sayılar)",
        "Veri Analizi: Çizgi, Sütun ve Daire Grafikleri",
        "Veri Analizi: Grafikler Arası Dönüşüm ve Yorumlama",
        "Basit Olayların Olma Olasılığı: Olası Durumlar ve Eşit Şans",
        "Basit Olayların Olma Olasılığı: Bir Olayın Olma Olasılığını Hesaplama",
        "Cebirsel İfadeler: Cebirsel İfadelerde Çarpma ve Modelleme",
        "Cebirsel İfadeler: Özdeşlikler (İki Terim Toplamı/Farkının Karesi, İki Kare Farkı)",
        "Cebirsel İfadeler: Çarpanlara Ayırma (Ortak Çarpan Parantezi ve Özdeşlikler)",
        "Doğrusal Denklemler: Birinci Dereceden Bir Bilinmeyenli Denklemler",
        "Doğrusal Denklemler: Koordinat Sistemi ve Doğrusal İlişkiler",
        "Doğrusal Denklemler: Doğru Grafikleri Çizimi ve Yorumlama",
        "Doğrusal Denklemler: Doğrunun Eğimi ve Eğim Problemleri",
        "Eşitsizlikler: Birinci Dereceden Bir Bilinmeyenli Eşitsizlikler & Sayı Doğrusu",
        "Eşitsizlikler: Eşitsizlik Çözümü ve Günlük Hayat Problemleri",
        "Üçgenler: Üçgende Kenarortay, Açıortay ve Yükseklik",
        "Üçgenler: Üçgen Eşitsizliği (Açı-Kenar Bağıntıları)",
        "Üçgenler: Üçgen Çizimi Kuralları (K-K-K, K-A-K, A-K-A)",
        "Üçgenler: Pisagor Bağıntısı ve Özel Dik Üçgenler",
        "Eşlik ve Benzerlik: Eş Çokgenler ve Benzer Çokgenler",
        "Eşlik ve Benzerlik: Benzerlik Oranı ve Üçgenlerde Benzerlik",
        "Dönüşüm Geometrisi: Nokta ve Şekillerin Ötelenmesi",
        "Dönüşüm Geometrisi: Yansıma ve Simetri Doğrusu",
        "Dönüşüm Geometrisi: Ardışık Öteleme ve Yansıma",
        "Geometrik Cisimler: Dik Prizmaların Özellikleri, Açınımı ve Yüzey Alanı",
        "Geometrik Cisimler: Dik Dairesel Silindirin Açınımı, Yüzey Alanı ve Hacmi",
        "Geometrik Cisimler: Dik Piramidin Özellikleri, Elemanları ve Açınımı",
        "Geometrik Cisimler: Dik Koninin Özellikleri, Elemanları ve Açınımı"
    ],
    "Fen Bilimleri": [
        "Mevsimler ve İklim: Mevsimlerin Oluşumu (Eksen Eğikliği & Dolanma)",
        "Mevsimler ve İklim: İklim ve Hava Hareketleri (Rüzgar, Nem, Yağış Türleri)",
        "Mevsimler ve İklim: Küresel İklim Değişikliği ve Sera Etkisi",
        "DNA ve Genetik Kod: DNA'nın Yapısı, Nükleotidler ve Eşlenmesi",
        "DNA ve Genetik Kod: Kalıtım, Mendel Genetiği ve Çaprazlamalar",
        "DNA ve Genetik Kod: Cinsiyet Belirlenmesi ve Akraba Evlilikleri",
        "DNA ve Genetik Kod: Mutasyon ve Modifikasyon",
        "DNA ve Genetik Kod: Adaptasyon (Uyum) ve Doğal Seçilim",
        "DNA ve Genetik Kod: Biyoteknoloji ve Genetik Mühendisliği",
        "Basınç: Katı Basıncı ve Basınca Etki Eden Faktörler",
        "Basınç: Sıvı Basıncı (Derinlik, Yoğunluk) ve Pascal Prensibi",
        "Basınç: Açık Hava Basıncı (Torricelli) ve Kapalı Kap Basıncı",
        "Madde ve Endüstri: Periyodik Sistemin Tarihçesi ve Yapısı (Grup / Periyot)",
        "Madde ve Endüstri: Elementlerin Sınıflandırılması (Metal, Ametal, Soygaz)",
        "Madde ve Endüstri: Fiziksel ve Kimyasal Değişimler",
        "Madde ve Endüstri: Kimyasal Tepkimeler ve Kütlenin Korunumu",
        "Madde ve Endüstri: Asitler ve Bazlar (pH Cetveli, Belirteçler)",
        "Madde ve Endüstri: Asit Yağmurları ve Çevresel Etkileri",
        "Madde ve Isı: Öz Isı ve Sıcaklık Değişimi İlişkisi",
        "Madde ve Isı: Hal Değişim Isısı (Erime, Donma, Buharlaşma Isısı)",
        "Madde ve Isı: Isınma ve Soğuma Eğrileri (Hal Değişim Grafikleri)",
        "Basit Makineler: Basit Makinelerin Genel Özellikleri ve Kuvvet Kazancı",
        "Basit Makineler: Sabit Makara, Hareketli Makara ve Palangalar",
        "Basit Makineler: Kaldıraç Türleri (Desteğin, Yükün, Kuvvetin Ortada Olması)",
        "Basit Makineler: Eğik Düzlem, Çıkrık, Dişli Çarklar, Kasnaklar ve Vida",
        "Enerji Dönüşümleri: Besin Zinciri, Üretici-Tüketici ve Ekoloji Piramidi",
        "Enerji Dönüşümleri: Fotosentez ve Fotosentez Hızını Etkileyen Faktörler",
        "Enerji Dönüşümleri: Oksijenli / Oksijensiz Solunum ve Fermantasyon",
        "Enerji Dönüşümleri: Madde Döngüleri (Su, Karbon, Oksijen, Azot Döngüsü)",
        "Elektrik Enerjisi: Elektrik Yükleri ve Elektriklenme Türleri (Sürtünme, Dokunma, Etki)",
        "Elektrik Enerjisi: Elektroskop ve Topraklama",
        "Elektrik Enerjisi: Elektrik Enerjisinin Isı, Işık ve Hareket Enerjisine Dönüşümü"
    ],
    "İnkılap Tarihi": [
        "Bir Kahraman Doğuyor: 20. Yüzyıl Başlarında Osmanlı Devleti ve Dünya",
        "Bir Kahraman Doğuyor: Mustafa Kemal'in Öğrenim Hayatı ve Şehirler",
        "Bir Kahraman Doğuyor: Mustafa Kemal'in Askerlik Hayatı ve Görevleri",
        "Bir Kahraman Doğuyor: Mustafa Kemal'in Fikir Hayatını Etkileyen Faktörler",
        "Milli Uyanış: I. Dünya Savaşı'nın Nedenleri ve Osmanlı'nın Savaştığı Cepheler",
        "Milli Uyanış: Mondros Ateşkes Antlaşması ve İşgaller",
        "Milli Uyanış: Cemiyetler (Milli Varlığa Yararlı ve Zararlı Cemiyetler)",
        "Milli Uyanış: Kuvay-ı Milliye Hareketi",
        "Milli Uyanış: Genelgeler ve Kongreler (Havza, Amasya, Erzurum, Sivas)",
        "Milli Uyanış: Misak-ı Milli ve Büyük Millet Meclisi'nin Açılması",
        "Milli Uyanış: BMM'ye Karşı Çıkarılan Ayaklanmalar ve Sevr Antlaşması",
        "Milli Bir Destan: Doğu ve Güney Cepheleri (Gümrü, Ankara Antlaşmaları)",
        "Milli Bir Destan: Batı Cephesi (I. ve II. İnönü Savaşları, Londra Konferansı)",
        "Milli Bir Destan: Kütahya-Eskişehir Savaşları ve Tekalif-i Milliye Emirleri",
        "Milli Bir Destan: Sakarya Meydan Muharebesi ve Başkomutanlık Meydan Muharebesi",
        "Milli Bir Destan: Mudanya Ateşkes Antlaşması ve Lozan Barış Antlaşması",
        "Atatürkçülük ve İnkılaplar: Atatürk İlkeleri (Cumhuriyetçilik, Milliyetçilik, Halkçılık, Devletçilik, Laiklik, İnkılapçılık)",
        "Atatürkçülük ve İnkılaplar: Siyasi Alanda İnkılaplar (Saltanatın Kaldırılması, Cumhuriyetin İlanı, Halifeliğin Kaldırılması)",
        "Atatürkçülük ve İnkılaplar: Hukuk Alanında İnkılaplar (Medeni Kanun ve Anayasalar)",
        "Atatürkçülük ve İnkılaplar: Eğitim ve Kültür Alanında İnkılaplar (Tevhid-i Tedrisat, Harf İnkılabı, TTK, TDK)",
        "Atatürkçülük ve İnkılaplar: Toplumsal Alanda İnkılaplar (Kılık-Kıyafet, Tekkeler, Soyadı Kanunu)",
        "Atatürkçülük ve İnkılaplar: Ekonomi Alanında İnkılaplar (İzmir İktisat Kongresi, Kabotaj, Sanayi)",
        "Demokratikleşme Çabaları: Çok Partili Hayata Geçiş Denemeleri (CHF, TCF, SCF)",
        "Demokratikleşme Çabaları: Rejime Karşı Tepkiler (Şeyh Sait İsyanı, İzmir Suikastı, Menemen Olayı)",
        "Dış Politika: Atatürk Dönemi Dış Politikanın Esasları",
        "Dış Politika: Yabancı Okullar, Musul Sorunu, Nüfus Mübadelesi",
        "Dış Politika: Montrö Boğazlar Sözleşmesi, Balkan Antantı, Sadabat Paktı, Hatay'ın Katılması",
        "Atatürk'ün Ölümü ve Sonrası: Atatürk'ün Vefatı, Eserleri ve II. Dünya Savaşı Etkileri"
    ],
    "Din Kültürü": [
        "Kader İnancı: Kader ve Kaza İnancı Tanımları",
        "Kader İnancı: Evrenin Yasaları (Fiziksel, Biyolojik ve Toplumsal Yasalar)",
        "Kader İnancı: İnsanın İradesi ve Kader (Külli ve Cüzi İrade)",
        "Kader İnancı: Kaderle İlgili Kavramlar (Ömür, Ecel, Rızık, Tevekkül, Başarı, Sağlık)",
        "Kader İnancı: Hz. Musa'nın Hayatı ve Ayet el-Kürsi",
        "Zekat ve Sadaka: İslam'ın Paylaşma ve Yardımlaşmaya Verdiği Önem",
        "Zekat ve Sadaka: Zekat İbadeti (Nisap Miktarı, Kimlere Verilir, Oranlar)",
        "Zekat ve Sadaka: Sadaka, Sadaka-i Cariye ve İnfak Kavramları",
        "Zekat ve Sadaka: Zekat ve Sadakanın Bireysel ve Toplumsal Faydaları",
        "Zekat ve Sadaka: Hz. Şuayb'ın Hayatı ve Maûn Suresi",
        "Din ve Hayat: Din, Birey ve Toplum İlişkisi",
        "Din ve Hayat: Dinin Temel Gayesi (Can, Akıl, Mal, Nesil ve Din Emniyeti)",
        "Din ve Hayat: Hz. Yusuf'un Hayatı ve Asr Suresi",
        "Hz. Muhammed'in Örnekliği: Hz. Muhammed'in Doğruluğu ve Güvenilirliği (El-Emin)",
        "Hz. Muhammed'in Örnekliği: Merhametli ve Affedici Oluşu, İstişareye Verdiği Önem",
        "Hz. Muhammed'in Örnekliği: Davasındaki Cesaret ve Kararlılığı, Hakkı Gözetmesi",
        "Hz. Muhammed'in Örnekliği: İnsanlara Değer Vermesi ve Kureyş Suresi",
        "Kur'an-ı Kerim ve Özellikleri: İslam Dininin Temel Kaynakları (Kur'an ve Sünnet)",
        "Kur'an-ı Kerim ve Özellikleri: Kur'an-ı Kerim'in Ana Konuları (İnanç, İbadet, Ahlak, Muamelat, Kıssalar)",
        "Kur'an-ı Kerim ve Özellikleri: Kur'an-ı Kerim'in Yol Gösterici Özellikleri ve Hz. Nuh'un Hayatı"
    ],
    "İngilizce": [
        "Unit 1: Friendship - Accepting, Refusing & Making Excuses",
        "Unit 1: Friendship - Personal Traits & Describing Friends",
        "Unit 2: Teen Life - Daily Routines & Regular Activities",
        "Unit 2: Teen Life - Expressing Preferences (Likes, Dislikes & Music/Sports)",
        "Unit 3: In The Kitchen - Cooking Methods & Process Sequencing",
        "Unit 3: In The Kitchen - Kitchen Utensils & Recipe Ingredients",
        "Unit 4: On The Phone - Phone Conversations & Phone Etiquette",
        "Unit 4: On The Phone - Taking & Leaving Messages",
        "Unit 5: The Internet - Internet Safety Rules & Precautions",
        "Unit 5: The Internet - Internet Terminology & Online Actions",
        "Unit 6: Adventures - Extreme Sports & Adventure Activities",
        "Unit 6: Adventures - Comparing Activities, Expressing Reasons & Preferences",
        "Unit 7: Tourism - Tourist Attractions & Historical Sites",
        "Unit 7: Tourism - Describing Experiences, Weather & Accommodations",
        "Unit 8: Chores - Household Chores & Responsibilities",
        "Unit 8: Chores - Expressing Obligations (Must / Have to / Need to)",
        "Unit 9: Science - Scientific Inventions, Discoveries & Experiments",
        "Unit 9: Science - Famous Scientists & Describing Scientific Actions",
        "Unit 10: Natural Forces - Natural Disasters & Environmental Issues",
        "Unit 10: Natural Forces - Causes, Consequences & Predictions about Nature"
    ]
}

# --- VERİ İŞLEMLERİ (GOOGLE SHEETS & JSON HİBRİT STORAGE) ---

def _is_valid_lgs_exam(item):
    """Gelen verinin geçerli bir LGS deneme kaydı olup olmadığını denetler."""
    if not isinstance(item, dict):
        return False
    return "deneme_adi" in item or "dersler" in item or "toplam_net" in item

def load_lgs_exams_local():
    """Tüm LGS denemelerini yerel JSON dosyasından yükler."""
    if not os.path.exists(LGS_DATA_FILE):
        return []
    try:
        with open(LGS_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                valid = [x for x in data if _is_valid_lgs_exam(x)]
                return valid
            return []
    except Exception as e:
        print(f"LGS yerel veri okuma hatası: {e}")
        return []

def save_lgs_exams_local(exams):
    """LGS denemelerini yerel JSON dosyasına kaydeder."""
    try:
        valid = [x for x in exams if _is_valid_lgs_exam(x)]
        with open(LGS_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(valid, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"LGS yerel veri yazma hatası: {e}")
        return False

def load_lgs_exams(api_url=None, force_refresh=False):
    """
    Tüm LGS denemelerini yükler.
    - api_url varsa önce Google Sheets API'den çeker (?type=lgs).
    - Başarılı olursa verileri yerel JSON dosyasına da yedekler/önbellekler.
    - api_url yoksa veya bağlantı hatası olursa yerel JSON dosyasından okur.
    """
    if api_url:
        try:
            sep = "&" if "?" in api_url else "?"
            url = f"{api_url}{sep}type=lgs"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                raw_data = resp.json()
                if isinstance(raw_data, list):
                    cloud_data = [x for x in raw_data if _is_valid_lgs_exam(x)]
                    if len(cloud_data) > 0 or (force_refresh and len(raw_data) == 0):
                        save_lgs_exams_local(cloud_data)
                        return cloud_data
                    # Eğer Google Apps Script henüz güncellenmemişse veya boşsa yereli koru
                    local_data = load_lgs_exams_local()
                    if len(local_data) > 0 and len(cloud_data) == 0:
                        return local_data
                    return cloud_data
        except Exception as e:
            print(f"LGS Google Sheets veri okuma hatası (yerel dosya devrede): {e}")
            
    return load_lgs_exams_local()

def save_lgs_exams(exams, api_url=None):
    """LGS denemelerini hem yerel dosyaya hem de varsa Google Sheets'e kaydeder."""
    res_local = save_lgs_exams_local(exams)
    if api_url:
        try:
            payload = {"action": "sync_all_lgs", "exams": exams}
            requests.post(api_url, json=payload, timeout=15)
        except Exception as e:
            print(f"LGS Google Sheets sync hatası: {e}")
    return res_local

def sync_local_to_cloud(api_url):
    """Yerel JSON dosyasındaki tüm denemeleri Google Sheets'e toplu aktarır."""
    if not api_url:
        return False, "API URL bulunamadı."
    exams = load_lgs_exams_local()
    if not exams:
        return True, "Aktarılacak yerel deneme bulunamadı."
    try:
        payload = {"action": "sync_all_lgs", "exams": exams}
        resp = requests.post(api_url, json=payload, timeout=15)
        if resp.status_code == 200:
            return True, f"{len(exams)} adet deneme Google Sheets'e aktarıldı."
        return False, f"Sunucu hatası: {resp.text}"
    except Exception as e:
        return False, f"Bağlantı hatası: {e}"

def get_student_exams(student_name=None, api_url=None, force_refresh=False):
    """Belirli bir öğrenciye veya tümüne ait denemeleri tarihe göre sıralı getirir."""
    exams = load_lgs_exams(api_url=api_url, force_refresh=force_refresh)
    if student_name and student_name != "Tümü":
        exams = [e for e in exams if e.get("ogrenci") == student_name]
    # Tarihe ve created_at'e göre sırala (en yeniden en eskiye)
    exams.sort(key=lambda x: (x.get("tarih", ""), x.get("created_at", "")), reverse=True)
    return exams

# --- HESAPLAMA MOTORU ---

def calculate_net(dogru, yanlis):
    """LGS Net hesaplama: Net = Doğru - (Yanlış / 3.0)"""
    dogru = int(dogru or 0)
    yanlis = int(yanlis or 0)
    net = dogru - (yanlis / 3.0)
    return round(max(0.0, net), 2)

def calculate_lgs_score(lesson_nets):
    """
    MEB yaklaşık LGS Puanı hesaplama simülasyonu (100 - 500 Puan).
    Taban Puan: 195.50
    Türkçe: Net * 3.67
    Matematik: Net * 4.95
    Fen: Net * 4.07
    İnkılap: Net * 1.68
    Din: Net * 1.63
    İngilizce: Net * 1.45
    90 Net tam çekildiğinde puan ~500.00 olur.
    """
    base_score = 195.50
    total_added = 0.0
    for lesson, info in LGS_LESSONS.items():
        net = lesson_nets.get(lesson, 0.0)
        puan_kat = info["puan_kat"]
        total_added += net * puan_kat
    
    score = base_score + total_added
    # 100 - 500 arasına sınırla
    score = min(500.0, max(100.0, score))
    return round(score, 2)

def create_exam_record(ogrenci, deneme_adi, yayin, tarih, sure_dk, zorluk, notlar, dersler_data):
    """
    Deneme sınavı kaydı oluşturur, ders ve toplam netleri/puanları hesaplar.
    dersler_data format:
    {
      "Türkçe": {
         "dogru": 18, "yanlis": 2, "bos": 0,
         "konular": [{"konu": "...", "soru": 2, "dogru": 2, "yanlis": 0, "bos": 0}, ...]
      },
      ...
    }
    """
    exam_id = str(uuid.uuid4())[:8]
    created_at = datetime.now().isoformat()
    
    lesson_records = {}
    lesson_nets = {}
    
    tot_dogru = 0
    tot_yanlis = 0
    tot_bos = 0
    tot_soru = 0
    
    sozel_net = 0.0
    sayisal_net = 0.0
    
    for lesson_name, lesson_info in LGS_LESSONS.items():
        ldata = dersler_data.get(lesson_name, {})
        d = int(ldata.get("dogru", 0))
        y = int(ldata.get("yanlis", 0))
        max_soru = lesson_info["soru_sayisi"]
        b = int(ldata.get("bos", max(0, max_soru - (d + y))))
        toplam_cozulen = d + y + b
        
        # Eğer girilen soru toplamı max_soru'dan farklıysa düzelt
        if toplam_cozulen > max_soru:
            b = max(0, max_soru - (d + y))
            toplam_cozulen = max_soru
            
        net = calculate_net(d, y)
        lesson_nets[lesson_name] = net
        
        if lesson_info["bolum"] == "Sözel":
            sozel_net += net
        else:
            sayisal_net += net
            
        tot_dogru += d
        tot_yanlis += y
        tot_bos += b
        tot_soru += max_soru
        
        konular = ldata.get("konular", [])
        
        lesson_records[lesson_name] = {
            "dogru": d,
            "yanlis": y,
            "bos": b,
            "toplam_soru": max_soru,
            "net": net,
            "basari_yuzdesi": round((net / max_soru) * 100, 1) if max_soru > 0 else 0,
            "konular": konular
        }
    
    toplam_net = round(sozel_net + sayisal_net, 2)
    tahmini_puan = calculate_lgs_score(lesson_nets)
    
    exam_obj = {
        "id": exam_id,
        "ogrenci": ogrenci,
        "deneme_adi": deneme_adi or "LGS Deneme Sınavı",
        "yayin": yayin or "Belirtilmedi",
        "tarih": str(tarih),
        "sure_dk": int(sure_dk or 155),
        "zorluk": zorluk or "Orta",
        "notlar": notlar or "",
        "dersler": lesson_records,
        "toplam_dogru": tot_dogru,
        "toplam_yanlis": tot_yanlis,
        "toplam_bos": tot_bos,
        "toplam_soru": tot_soru,
        "toplam_net": toplam_net,
        "sozel_net": round(sozel_net, 2),
        "sayisal_net": round(sayisal_net, 2),
        "tahmini_puan": tahmini_puan,
        "created_at": created_at
    }
    return exam_obj

def add_exam(exam_obj, api_url=None):
    """Yeni bir deneme sınavı ekler (Yerel ve Google Sheets)."""
    # 1. Yerel listeye ekle
    exams = load_lgs_exams_local()
    exams = [e for e in exams if e.get("id") != exam_obj.get("id")]
    exams.append(exam_obj)
    save_lgs_exams_local(exams)
    
    # 2. Google Sheets API'ye ekle
    if api_url:
        try:
            payload = {
                "action": "add_lgs",
                "id": exam_obj.get("id", ""),
                "ogrenci": exam_obj.get("ogrenci", ""),
                "deneme_adi": exam_obj.get("deneme_adi", ""),
                "yayin": exam_obj.get("yayin", ""),
                "tarih": str(exam_obj.get("tarih", "")),
                "sure_dk": exam_obj.get("sure_dk", 0),
                "zorluk": exam_obj.get("zorluk", "Orta"),
                "notlar": exam_obj.get("notlar", ""),
                "toplam_net": exam_obj.get("toplam_net", 0),
                "lgs_puani": exam_obj.get("tahmini_puan", 0),
                "dersler": exam_obj.get("dersler", {}),
                "created_at": exam_obj.get("created_at", "")
            }
            requests.post(api_url, json=payload, timeout=10)
        except Exception as e:
            print(f"LGS Cloud add_lgs hatası: {e}")
            
    return exam_obj

def update_exam(exam_id, updated_data, api_url=None):
    """Mevcut bir denemeyi günceller."""
    exams = load_lgs_exams_local()
    for i, e in enumerate(exams):
        if e.get("id") == exam_id:
            exams[i] = updated_data
            save_lgs_exams_local(exams)
            if api_url:
                save_lgs_exams(exams, api_url=api_url)
            return True
    return False

def delete_exam(exam_id, api_url=None):
    """Deneme sınavını siler (Yerel ve Google Sheets)."""
    # 1. Yerelden sil
    exams = load_lgs_exams_local()
    new_exams = [e for e in exams if e.get("id") != exam_id]
    save_lgs_exams_local(new_exams)
    
    # 2. Buluttan sil
    if api_url:
        try:
            payload = {"action": "delete_lgs", "id": exam_id}
            requests.post(api_url, json=payload, timeout=10)
        except Exception as e:
            print(f"LGS Cloud delete_lgs hatası: {e}")
    return True

# --- DELTA (ÖNCEKİ DENEMEYE GÖRE DEĞİŞİM) ANALİZİ ---

def get_delta_analysis(current_exam, previous_exam):
    """
    İki deneme arasındaki farkları detaylıca hesaplar.
    current_exam: Yeni/seçilen deneme
    previous_exam: Karşılaştırılan önceki deneme
    """
    if not current_exam or not previous_exam:
        return None
        
    delta_net = round(current_exam.get("toplam_net", 0) - previous_exam.get("toplam_net", 0), 2)
    delta_puan = round(current_exam.get("tahmini_puan", 0) - previous_exam.get("tahmini_puan", 0), 2)
    delta_dogru = current_exam.get("toplam_dogru", 0) - previous_exam.get("toplam_dogru", 0)
    delta_yanlis = current_exam.get("toplam_yanlis", 0) - previous_exam.get("toplam_yanlis", 0)
    delta_bos = current_exam.get("toplam_bos", 0) - previous_exam.get("toplam_bos", 0)
    delta_sozel_net = round(current_exam.get("sozel_net", 0) - previous_exam.get("sozel_net", 0), 2)
    delta_sayisal_net = round(current_exam.get("sayisal_net", 0) - previous_exam.get("sayisal_net", 0), 2)
    
    lesson_deltas = {}
    curr_lessons = current_exam.get("dersler", {})
    prev_lessons = previous_exam.get("dersler", {})
    
    for l_name in LGS_LESSONS.keys():
        c_l = curr_lessons.get(l_name, {})
        p_l = prev_lessons.get(l_name, {})
        
        c_net = c_l.get("net", 0.0)
        p_net = p_l.get("net", 0.0)
        l_delta_net = round(c_net - p_net, 2)
        
        c_d = c_l.get("dogru", 0)
        p_d = p_l.get("dogru", 0)
        
        c_y = c_l.get("yanlis", 0)
        p_y = p_l.get("yanlis", 0)
        
        c_b = c_l.get("bos", 0)
        p_b = p_l.get("bos", 0)
        
        lesson_deltas[l_name] = {
            "current_net": c_net,
            "previous_net": p_net,
            "delta_net": l_delta_net,
            "current_d": c_d, "previous_d": p_d, "delta_d": c_d - p_d,
            "current_y": c_y, "previous_y": p_y, "delta_y": c_y - p_y,
            "current_b": c_b, "previous_b": p_b, "delta_b": c_b - p_b,
        }
        
    # Konu bazlı değişimler (eğer madde analizi girilmişse)
    improved_topics = []
    regressed_topics = []
    
    prev_topic_map = {}
    for l_name, l_data in prev_lessons.items():
        for top in l_data.get("konular", []):
            t_key = f"{l_name} - {top.get('konu')}"
            prev_topic_map[t_key] = top
            
    for l_name, l_data in curr_lessons.items():
        for top in l_data.get("konular", []):
            t_key = f"{l_name} - {top.get('konu')}"
            if t_key in prev_topic_map:
                p_top = prev_topic_map[t_key]
                c_y = top.get("yanlis", 0)
                p_y = p_top.get("yanlis", 0)
                c_d = top.get("dogru", 0)
                p_d = p_top.get("dogru", 0)
                
                if p_y > 0 and c_y == 0 and c_d > 0:
                    improved_topics.append({
                        "ders": l_name, "konu": top.get("konu"),
                        "mesaj": f"Önceki denemede {p_y} yanlış vardı, bu denemede 0 yanlış! 🎯"
                    })
                elif c_y > p_y and c_y > 0:
                    regressed_topics.append({
                        "ders": l_name, "konu": top.get("konu"),
                        "mesaj": f"Bu denemede {c_y} yanlış çıktı (Önceki: {p_y}). Tekrar edilmeli. ⚠️"
                    })
                    
    return {
        "delta_net": delta_net,
        "delta_puan": delta_puan,
        "delta_dogru": delta_dogru,
        "delta_yanlis": delta_yanlis,
        "delta_bos": delta_bos,
        "delta_sozel_net": delta_sozel_net,
        "delta_sayisal_net": delta_sayisal_net,
        "lesson_deltas": lesson_deltas,
        "improved_topics": improved_topics,
        "regressed_topics": regressed_topics,
        "current_name": current_exam.get("deneme_adi"),
        "previous_name": previous_exam.get("deneme_adi"),
        "current_date": current_exam.get("tarih"),
        "previous_date": previous_exam.get("tarih")
    }

# --- KONU KARNESİ VE MADDE ANALİZİ (TOPIC MASTERY) ---

def get_topic_mastery_report(student_name=None, api_url=None):
    """
    Tüm denemelerdeki madde analizlerini birleştirip konu karnesi üretir.
    En çok hata yapılan konuları, ustalaşılan konuları ve konu başarı oranlarını çıkarır.
    """
    exams = get_student_exams(student_name, api_url=api_url)
    if not exams:
        return {"all_topics": [], "trouble_topics": [], "mastered_topics": []}
        
    topic_aggregates = {}
    
    for ex in exams:
        lessons = ex.get("dersler", {})
        for l_name, l_data in lessons.items():
            for top in l_data.get("konular", []):
                t_name = top.get("konu", "").strip()
                if not t_name:
                    continue
                key = (l_name, t_name)
                if key not in topic_aggregates:
                    topic_aggregates[key] = {
                        "ders": l_name,
                        "konu": t_name,
                        "toplam_soru": 0,
                        "toplam_dogru": 0,
                        "toplam_yanlis": 0,
                        "toplam_bos": 0,
                        "deneme_sayisi": 0
                    }
                topic_aggregates[key]["toplam_soru"] += int(top.get("soru", 0))
                topic_aggregates[key]["toplam_dogru"] += int(top.get("dogru", 0))
                topic_aggregates[key]["toplam_yanlis"] += int(top.get("yanlis", 0))
                topic_aggregates[key]["toplam_bos"] += int(top.get("bos", 0))
                topic_aggregates[key]["deneme_sayisi"] += 1
                
    topic_list = []
    for key, data in topic_aggregates.items():
        s = data["toplam_soru"]
        d = data["toplam_dogru"]
        y = data["toplam_yanlis"]
        net = round(d - (y / 3.0), 2)
        rate = round((d / s) * 100, 1) if s > 0 else 0.0
        
        topic_list.append({
            "ders": data["ders"],
            "konu": data["konu"],
            "toplam_soru": s,
            "toplam_dogru": d,
            "toplam_yanlis": y,
            "toplam_bos": data["toplam_bos"],
            "toplam_net": net,
            "basari_yuzdesi": rate,
            "deneme_sayisi": data["deneme_sayisi"]
        })
        
    # En çok hata yapılanlar (Öncelikli tekrar listesi - Yanlış sayısı ve başarı oranına göre)
    trouble_topics = [t for t in topic_list if t["toplam_yanlis"] > 0 or t["basari_yuzdesi"] < 70.0]
    trouble_topics.sort(key=lambda x: (x["toplam_yanlis"], -x["basari_yuzdesi"]), reverse=True)
    
    # Ustalaşılan konular (%85+ başarı ve en az 2 soru)
    mastered_topics = [t for t in topic_list if t["basari_yuzdesi"] >= 85.0 and t["toplam_soru"] >= 2]
    mastered_topics.sort(key=lambda x: (x["basari_yuzdesi"], x["toplam_soru"]), reverse=True)
    
    return {
        "all_topics": topic_list,
        "trouble_topics": trouble_topics[:10], # İlk 10 alarm veren konu
        "mastered_topics": mastered_topics
    }

# --- PLOTLY GRAFİK ÜRETİCİLERİ ---

def create_net_and_score_trend_chart(exams):
    """Denemeler boyunca Toplam Net ve LGS Puanı gelişim trendi grafiği."""
    if not exams:
        return None
        
    # Kronolojik sıra (eskiden yeniye)
    sorted_exams = sorted(exams, key=lambda x: (x.get("tarih", ""), x.get("created_at", "")))
    
    dates_and_names = [f"{e.get('tarih')} - {e.get('deneme_adi', '')[:18]}" for e in sorted_exams]
    nets = [e.get("toplam_net", 0) for e in sorted_exams]
    scores = [e.get("tahmini_puan", 0) for e in sorted_exams]
    
    fig = go.Figure()
    
    # Net Çizgisi (Sol Y ekseni)
    fig.add_trace(go.Scatter(
        x=dates_and_names,
        y=nets,
        name="Toplam Net (Max 90)",
        mode="lines+markers+text",
        text=[f"{n:.2f}" for n in nets],
        textposition="top center",
        line=dict(color="#D81B60", width=3.5),
        marker=dict(size=10, color="#C2185B", symbol="circle"),
        yaxis="y1"
    ))
    
    # Puan Çizgisi (Sağ Y ekseni)
    fig.add_trace(go.Scatter(
        x=dates_and_names,
        y=scores,
        name="Tahmini LGS Puanı",
        mode="lines+markers+text",
        text=[f"{s:.1f}" for s in scores],
        textposition="bottom center",
        line=dict(color="#8E24AA", width=2.5, dash="dot"),
        marker=dict(size=8, color="#6A1B9A", symbol="diamond"),
        yaxis="y2"
    ))
    
    fig.update_layout(
        title=dict(text="📈 LGS Deneme Net ve Puan Gelişim Trendi", font=dict(family="Quicksand, sans-serif", size=18, color="#880E4F")),
        paper_bgcolor="rgba(255,255,255,0.7)",
        plot_bgcolor="rgba(255,240,245,0.4)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(
            title=dict(text="Toplam Net", font=dict(color="#D81B60")),
            tickfont=dict(color="#D81B60"),
            range=[0, 95]
        ),
        yaxis2=dict(
            title=dict(text="Tahmini Puan (500)", font=dict(color="#8E24AA")),
            tickfont=dict(color="#8E24AA"),
            anchor="x",
            overlaying="y",
            side="right",
            range=[100, 510]
        ),
        xaxis=dict(tickangle=-25)
    )
    return fig

def create_lesson_trend_chart(exams):
    """Her dersin denemeler içindeki net gelişim çizgileri."""
    if not exams:
        return None
        
    sorted_exams = sorted(exams, key=lambda x: (x.get("tarih", ""), x.get("created_at", "")))
    dates_and_names = [f"{e.get('tarih')} - {e.get('deneme_adi', '')[:14]}" for e in sorted_exams]
    
    fig = go.Figure()
    
    for l_name, l_info in LGS_LESSONS.items():
        l_nets = []
        for ex in sorted_exams:
            l_net = ex.get("dersler", {}).get(l_name, {}).get("net", 0.0)
            l_nets.append(l_net)
            
        fig.add_trace(go.Scatter(
            x=dates_and_names,
            y=l_nets,
            name=f"{l_info['icon']} {l_name}",
            mode="lines+markers",
            line=dict(color=l_info["color"], width=2.5),
            marker=dict(size=7)
        ))
        
    fig.update_layout(
        title=dict(text="🎯 Ders Bazlı Net Değişimi", font=dict(family="Quicksand, sans-serif", size=18, color="#880E4F")),
        paper_bgcolor="rgba(255,255,255,0.7)",
        plot_bgcolor="rgba(255,240,245,0.4)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        yaxis=dict(title="Net", range=[0, 22]),
        xaxis=dict(tickangle=-25)
    )
    return fig

def create_lesson_comparison_bar(current_exam, previous_exam):
    """İki deneme arasındaki ders netlerini yan yana çubuklarla kıyaslar."""
    lessons = list(LGS_LESSONS.keys())
    curr_nets = [current_exam.get("dersler", {}).get(l, {}).get("net", 0.0) for l in lessons]
    prev_nets = [previous_exam.get("dersler", {}).get(l, {}).get("net", 0.0) for l in lessons]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=lessons,
        y=prev_nets,
        name=f"Önceki: {previous_exam.get('deneme_adi', '')[:15]}",
        marker_color="#F48FB1",
        text=[f"{n:.2f}" for n in prev_nets],
        textposition="outside"
    ))
    
    fig.add_trace(go.Bar(
        x=lessons,
        y=curr_nets,
        name=f"Seçilen: {current_exam.get('deneme_adi', '')[:15]}",
        marker_color="#D81B60",
        text=[f"{n:.2f}" for n in curr_nets],
        textposition="outside"
    ))
    
    fig.update_layout(
        barmode="group",
        title=dict(text="📊 Ders Bazında Karşılaştırma", font=dict(family="Quicksand, sans-serif", size=16, color="#880E4F")),
        paper_bgcolor="rgba(255,255,255,0.7)",
        plot_bgcolor="rgba(255,240,245,0.4)",
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Net", range=[0, 23])
    )
    return fig

def create_topic_mastery_chart(topic_list, lesson_filter=None):
    """Konu karnesi başarı oranları çubuk grafiği."""
    if not topic_list:
        return None
        
    filtered = topic_list
    if lesson_filter and lesson_filter != "Tüm Dersler":
        filtered = [t for t in topic_list if t["ders"] == lesson_filter]
        
    if not filtered:
        return None
        
    # Başarı oranına göre sırala
    filtered.sort(key=lambda x: x["basari_yuzdesi"], reverse=True)
    
    konu_labels = [f"{t['ders'][:3]}: {t['konu'][:25]}" for t in filtered]
    success_rates = [t["basari_yuzdesi"] for t in filtered]
    colors = ["#4CAF50" if r >= 80 else "#FF9800" if r >= 60 else "#E91E63" for r in success_rates]
    
    fig = go.Figure(go.Bar(
        x=success_rates,
        y=konu_labels,
        orientation='h',
        marker_color=colors,
        text=[f"%{r:.1f} ({t['toplam_dogru']}/{t['toplam_soru']} D)" for r, t in zip(success_rates, filtered)],
        textposition="outside"
    ))
    
    fig.update_layout(
        title=dict(text="📚 Konu Başarı Oranları (Doğruluk %)", font=dict(family="Quicksand, sans-serif", size=16, color="#880E4F")),
        paper_bgcolor="rgba(255,255,255,0.7)",
        plot_bgcolor="rgba(255,240,245,0.4)",
        margin=dict(l=150, r=40, t=40, b=30),
        xaxis=dict(title="Başarı Yüzdesi (%)", range=[0, 115]),
        yaxis=dict(autorange="reversed")
    )
    return fig
