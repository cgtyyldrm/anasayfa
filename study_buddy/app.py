import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import time
import random
import pytz
import base64
import os
import json
import lgs_manager as lm

try:
    import extra_streamlit_components as stx # YENİ EKLENDİ
except Exception:
    class _FallbackCookieManager:
        def __init__(self):
            if "_cookies" not in st.session_state:
                st.session_state["_cookies"] = {}
        def get(self, cookie=None):
            return st.session_state.get("_cookies", {}).get(cookie)
        def set(self, cookie, value, expires_at=None):
            if "_cookies" not in st.session_state:
                st.session_state["_cookies"] = {}
            st.session_state["_cookies"][cookie] = value
        def delete(self, cookie):
            if "_cookies" in st.session_state:
                st.session_state["_cookies"].pop(cookie, None)

    class _stx:
        CookieManager = _FallbackCookieManager

    stx = _stx()
    st.warning("`extra_streamlit_components` not installed — using fallback cookie manager.\nInstall with: pip install extra-streamlit-components")

try:
    st_fragment = st.fragment
except AttributeError:
    try:
        st_fragment = st.experimental_fragment
    except AttributeError:
        st_fragment = lambda f: f

# LOGO HANDLING
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# Construct absolute path to logo.png
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")

logo_base64 = get_base64_image(logo_path)

if logo_base64:
    LOGO_DATA_URI = f"data:image/png;base64,{logo_base64}"
    page_icon_target = logo_path
else:
    # FALLBACK to remote URL if local file is missing (e.g. not committed to git on Cloud)
    LOGO_DATA_URI = "https://raw.githubusercontent.com/cgtyyldrm/anasayfa/main/assets/logo.PNG"
    page_icon_target = LOGO_DATA_URI
    print(f"Warning: Local logo not found at {logo_path}. Using remote fallback.")

# --- 1. Sayfa ve Stil Ayarları ---
st.set_page_config(page_title="Study Buddy", page_icon=page_icon_target, layout="wide")
# --- 1. Sayfa ve Stil Ayarları ---

# --- IOS ANA EKRAN LOGOSU İÇİN ÖZEL KOD ---
st.markdown(
    f"""
    <style>
    </style>
    <link rel="apple-touch-icon" sizes="180x180" href="{LOGO_DATA_URI}">
    <link rel="icon" type="image/png" href="{LOGO_DATA_URI}">
    <link rel="shortcut icon" type="image/png" href="{LOGO_DATA_URI}">
    <meta name="apple-mobile-web-app-title" content="Study Buddy">
    <meta name="application-name" content="Study Buddy">
    """,
    unsafe_allow_html=True
)
# -------------------------------------------
# --- ANDROID & IOS EKRAN KORUMA SİSTEMİ (Mevcut tasarıma dokunmaz) ---
st.markdown("""
<script>
    let wakeLock = null;

    // 1. Ekran Kilidini İsteyen Fonksiyon
    async function requestWakeLock() {
        if ('wakeLock' in navigator) {
            try {
                wakeLock = await navigator.wakeLock.request('screen');
                console.log('Ekran Kilidi: AKTİF');
            } catch (err) {
                console.log('Kilit Hatası:', err.name, err.message);
            }
        }
    }

    // 2. Android İçin Tetikleyici (Dokunma ile Kilidi Tazeler)
    // Android Chrome, kullanıcı ekrana dokunmazsa kilidi bazen devreye sokmaz.
    const reLock = async () => {
        if (wakeLock === null && document.visibilityState === 'visible') {
            await requestWakeLock();
        }
    };

    // Kullanıcı ekrana her dokunduğunda veya kaydırdığında kilidi yenile
    ['click', 'touchstart', 'scroll', 'keydown'].forEach(evt => 
        document.addEventListener(evt, reLock, {passive: true})
    );

    // Sekme tekrar açıldığında (başka uygulamadan dönüldüğünde)
    document.addEventListener('visibilitychange', async () => {
        if (wakeLock !== null && document.visibilityState === 'visible') {
            await requestWakeLock();
        }
    });

    // İlk açılışta başlat
    requestWakeLock();
</script>
""", unsafe_allow_html=True)
# -------------------------------------------------------------------

# --- Cookie Manager Kurulumu (Oturum Yönetimi) ---
cookie_manager = stx.CookieManager()

# --- Türkiye Saati Ayarı ---
def get_turkey_time():
    try:
        tz = pytz.timezone('Turkey')
        return datetime.now(tz).date()
    except:
        return date.today()

# CSS Ayarları
st.markdown("""
<script>
    // Robust Wake Lock API Wrapper
    let wakeLock = null;

    async function requestWakeLock() {
        if ('wakeLock' in navigator) {
            try {
                wakeLock = await navigator.wakeLock.request('screen');
                console.log('Wake Lock active!');

                wakeLock.addEventListener('release', () => {
                   console.log('Wake Lock released'); 
                });
            } catch (err) {
                console.error(`${err.name}, ${err.message}`);
            }
        }
    }

    // Re-acquire lock when page comes back to visibility
    document.addEventListener('visibilitychange', async () => {
        if (wakeLock !== null && document.visibilityState === 'visible') {
            await requestWakeLock();
        }
    });

    // Request on load
    requestWakeLock();
</script>
<style>
    /* Google Fonts import (Optional - Streamlit runs locally so maybe skipped, sticking to websafe) */
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap');

    /* Main App Background - Baby Pink */
    [data-testid="stAppViewContainer"] {
        background-color: #FFF0F5; 
        background-image: linear-gradient(to bottom right, #FFF0F5, #FCE4EC);
    }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #F8BBD0;
        border-right: 2px solid #F48FB1;
    }

    /* Titles */
    .main-title { 
        font-size: 3rem !important; 
        font-weight: 800; 
        color: #D81B60; /* Deep Pink */
        text-align: center; 
        margin-bottom: 5px; 
        font-family: 'Quicksand', 'Comic Sans MS', sans-serif;
        text-shadow: 2px 2px 4px #F8BBD0;
    }
    
    .sub-title { 
        font-size: 1.1rem; 
        color: #ec407a; 
        text-align: center; 
        margin-bottom: 25px; 
        font-style: italic; 
        font-family: 'Quicksand', sans-serif;
    }

    div[data-testid="column"] { align-items: center; }
    div[data-testid="column"] p { font-size: 15px !important; margin-bottom: 0px !important; color: #880E4F; }

    /* Buttons - White with Pink Accents */
    .stButton button { 
        background-color: #FFFFFF !important; 
        color: #D81B60 !important; 
        font-size: 14px !important; 
        padding: 6px 16px !important; 
        border-radius: 20px !important; 
        border: 2px solid #F06292 !important; 
        height: auto !important; 
        white-space: nowrap !important; 
        font-weight: bold !important;
        box-shadow: 0 2px 5px rgba(233, 30, 99, 0.2);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(233, 30, 99, 0.3);
        border-color: #D81B60 !important;
    }
    
    /* Images */
    img { border-radius: 50%; border: 3px solid #F48FB1; transition: transform .2s; max-width: 100%; }
    img:hover { transform: scale(1.1); border-color: #D81B60; }
    
    @media (min-width: 640px) { div[data-testid="column"] { display: flex; justify-content: flex-start; } }
    
    /* Timer Font */
    .timer-font { 
        font-family: 'Quicksand', monospace; 
        font-weight: bold; 
        color: #C2185B; /* Pink 700 */
        text-shadow: 2px 2px 0px #F8BBD0;
    }
    
    div[data-testid="stAlert"] { padding: 0.5rem 1rem !important; border-radius: 15px; border: 2px solid #F48FB1; background-color: #FCE4EC; }
    
    /* Table Headers */
    div[data-testid="stMarkdownContainer"] p {
         font-family: 'Quicksand', sans-serif;
         font-weight: 600;
    }

    /* GLOBAL TEXT FIXES FOR READABILITY - PINK EDITION */
    /* Using Dark Pink #880E4F instead of Black/Grey */
    h1, h2, h3, h4, h5, h6, p, li, span, label, div[data-testid="stMarkdownContainer"], div[data-testid="stText"] {
        color: #880E4F !important; /* Pink 900 */
    }
    
    /* LOGIN & FORM CARD STYLE */
    [data-testid="stForm"] {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 30px;
        border: 4px solid #F8BBD0; /* Soft Pink Border */
        box-shadow: 0 10px 30px rgba(233, 30, 99, 0.2);
    }
    
    /* CUTE SOLID INPUT FIELDS */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        color: #880E4F !important;
        caret-color: #EC407A !important;
        background-color: #ffffff !important; /* Solid White */
        border: 2px solid #F06292 !important; /* Pink Border */
        border-radius: 25px !important; /* Very round pill shape */
        padding: 12px 20px !important;
        font-size: 1.1rem !important;
        font-family: 'Quicksand', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(233, 30, 99, 0.05) !important;
    }
    
    /* Input Focus State */
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #D81B60 !important;
        background-color: #FFF0F5 !important; /* Slight pink tint on focus */
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(233, 30, 99, 0.15) !important;
    }

    /* Remove native blackness from placeholders */
    ::placeholder {
        color: #F48FB1 !important; /* Pink Placeholder */
        font-weight: 500;
        opacity: 1 !important;
    }
    
    /* STATUS BADGE STYLES */
    .status-badge {
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        text-align: center;
        width: 100%;
    }
    .badge-done { background-color: #FCE4EC; color: #880E4F; border: 1px solid #F8BBD0; }
    .badge-planned { background-color: rgba(255,255,255,0.6); color: #AD1457; border: 1px dashed #F48FB1; }
    .badge-working { background-color: #EC407A; color: white; border: 1px solid #D81B60; box-shadow: 0 0 5px #EC407A; }
    .badge-waiting { background-color: #FFF0F5; color: #C2185B; opacity: 0.8; }

    /* Fix for Chrome/Safari Autofill "Yellow/White" background */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active{
        -webkit-box-shadow: 0 0 0 30px #ffffff inset !important; /* Match white background */
        -webkit-text-fill-color: #880E4F !important;
        transition: background-color 5000s ease-in-out 0s;
    }
    
    /* Input Labels */
    .stTextInput label, .stNumberInput label {
        font-weight: 700 !important;
        color: #C2185B !important;
        font-size: 0.95rem !important;
    }

    /* PRETTY DATE PICKER STYLE */
    .stDateInput div[data-baseweb="input"] {
        background-color: #F8BBD0 !important; /* Pink background */
        border: 2px solid #EC407A !important;
        border-radius: 25px !important; /* Pill shape */
        padding: 5px 10px;
        box-shadow: 0 4px 6px rgba(233, 30, 99, 0.15);
        transition: all 0.3s ease;
    }
    .stDateInput div[data-baseweb="input"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(233, 30, 99, 0.25);
        border-color: #D81B60 !important;
    }
    .stDateInput input {
        color: #880E4F !important;
        font-weight: bold !important;
        text-align: center;
    }
    /* Calendar Icon color inside input */
    .stDateInput svg {
        fill: #D81B60 !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #EC407A !important;
        box-shadow: 0 0 5px #F48FB1 !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #D81B60 !important; /* Deep Pink */
    }
    div[data-testid="stMetricLabel"] {
        color: #AD1457 !important; /* Pink 800 */
    }
    
    /* Exceptions for our custom classes */
    .main-title { color: #D81B60 !important; }
    .sub-title { color: #AD1457 !important; }
    
    /* Buttons - General (Secondary) */
    .stButton button { 
        background-color: #FFFFFF !important; 
        color: #C2185B !important; /* Pink 700 */
        border: 2px solid #F06292 !important; /* Pink 300 */
        border-radius: 20px !important;
    }
    .stButton button:hover {
        background-color: #FCE4EC !important; /* Light Pink hover */
        border-color: #EC407A !important;
        color: #880E4F !important;
    }
    .stButton button:active {
        background-color: #F8BBD0 !important;
        color: #880E4F !important;
    }

    /* Buttons - Primary (e.g. 'Devam Et', 'Bitir') */
    /* Streamlit uses kind="primary" or specific classes, but we can try to target specific overrides if needed.
       Since we can't easily distinguish 'kind' in pure CSS without complex selectors that might break,
       we will stick to a beautiful unified style, OR rely on Streamlit's class structure if constant.
       Actually, Streamlit adds a specific class for primary buttons usually, but it varies. 
       Let's force a consistent style for ALL buttons to be safe, or use the data attribute if available.
    */
    
    /* Attempting to target data-testid logic if possible, otherwise we make all buttons look "Pink-Secondary" style which is safer for this theme.
       However, if we want "Filled" buttons for primary:
    */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #EC407A !important; /* Pink 400 */
        color: white !important;
        border: none !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #D81B60 !important; /* Pink 600 */
        color: white !important;
        box-shadow: 0 4px 6px rgba(233, 30, 99, 0.3);
    }
    div[data-testid="stFormSubmitButton"] button {
        background-color: #EC407A !important;
        color: white !important;
        border: none !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #D81B60 !important;
        color: white !important;
    }

    /* Expander Header */
    .streamlit-expanderHeader {
        color: #880E4F !important;
        background-color: #F8BBD0 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #F48FB1 !important;
        border-radius: 10px !important;
        background-color: #FFF0F5 !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #AD1457 !important;
        border-radius: 4px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FCE4EC !important;
        border: 1px solid #F48FB1 !important;
    }

    /* LGS Delta Badges & Cards */
    .delta-badge-pos {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
        border: 1px solid #A5D6A7;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        font-size: 0.95rem;
    }
    .delta-badge-neg {
        background-color: #FFEBEE !important;
        color: #C62828 !important;
        border: 1px solid #FFCDD2;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        font-size: 0.95rem;
    }
    .delta-badge-neu {
        background-color: #F5F5F5 !important;
        color: #616161 !important;
        border: 1px solid #E0E0E0;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        font-size: 0.95rem;
    }
    .trouble-card {
        background: #FFF8E1;
        border-left: 5px solid #FF9800;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    .mastered-card {
        background: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Session State ve Cookie Kontrolü ---
if "timer_active" not in st.session_state: st.session_state.timer_active = False  
if "timer_start_time" not in st.session_state: st.session_state.timer_start_time = None 
if "timer_accumulated" not in st.session_state: st.session_state.timer_accumulated = 0 
if "timer_running" not in st.session_state: st.session_state.timer_running = False 
if "current_task_info" not in st.session_state: st.session_state.current_task_info = {} 
if "temp_dogru" not in st.session_state: st.session_state.temp_dogru = 0
if "temp_yanlis" not in st.session_state: st.session_state.temp_yanlis = 0
if "temp_bos" not in st.session_state: st.session_state.temp_bos = 0
if "authenticated_user" not in st.session_state: st.session_state.authenticated_user = None
if "edit_mode_index" not in st.session_state: st.session_state.edit_mode_index = None
if "global_student_selection" not in st.session_state: st.session_state.global_student_selection = "Tümü"

# --- OTURUM KONTROLÜ (COOKIE) ---
# Sayfa yüklendiğinde çerez var mı diye bakıyoruz
cookie_user = cookie_manager.get(cookie="study_buddy_user")

# Eğer çerez varsa ve session boşsa, session'ı doldur (Otomatik Giriş)
if cookie_user and st.session_state.authenticated_user is None and not st.session_state.get("logout_clicked", False):
    st.session_state.authenticated_user = cookie_user

MOTIVATION_QUOTES = [
    "Başarı, her gün tekrarlanan küçük çabaların toplamıdır. 🌸",
    "Gelecek, bugün ne yaptığına bağlıdır. 🎀",
    "Zor yollar genellikle güzel yerlere çıkar. 🦄",
    "İnanmak, başarmanın yarısıdır. Sen harikasın! 💖",
    "Bugün harika bir gün olacak! 🌈",
    "Prensesler de çok çalışır! 👑"
]

# --- 4. Giriş Ekranı ---
@st_fragment
def login_screen():
    st.markdown('<div class="main-title">📚 Study Buddy</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">"{random.choice(MOTIVATION_QUOTES)}"</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.container(border=True):
            # Ribbon Title for Login Form
            st.markdown("<div style='text-align:center;'><div class='ribbon-title' style='margin-top:0px;'>✨ Giriş Yap</div></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Kullanıcı Adı")
                password = st.text_input("Şifre", type="password")
                
                if st.form_submit_button("🚀 Giriş Yap", use_container_width=True):
                    if "passwords" in st.secrets and username in st.secrets["passwords"] and \
                       password == st.secrets["passwords"][username]:
                        
                        # Session'a kaydet
                        st.session_state["authenticated_user"] = username
                        st.session_state["logout_clicked"] = False
                        
                        # Çereze kaydet (30 gün geçerli)
                        cookie_manager.set("study_buddy_user", username, expires_at=datetime.now() + timedelta(days=30))
                        
                        st.toast(f"Hoş geldin {username}!", icon="👋")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Hatalı giriş bilgileri.")

# --- SETTINGS MANAGEMENT ---
SETTINGS_FILE = os.path.join(script_dir, "user_settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Ayarlar kaydedilemedi: {e}")

# --- 5. Veri İşlemleri (API) ---
@st.cache_data(ttl=60, show_spinner=False)
def get_data():
    if "connections" not in st.secrets: return pd.DataFrame()
    url = st.secrets["connections"]["webapp_url"]
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            
            rename_map = {
                "Süre": "Sure", "Süre (dk)": "Sure",
                "Doğru": "Dogru", "Yanlış": "Yanlis", "Toplam": "Toplam",
                "Soru Sayısı": "Toplam"
            }
            df.rename(columns=rename_map, inplace=True)

            expected = ["Tarih", "Kullanıcı", "Ders", "Konu", "Durum", "Notlar", "Sure", "Dogru", "Yanlis", "Bos", "Toplam", "rowIndex"]
            for col in expected:
                if col not in df.columns: df[col] = ""
            
            for col in ["Sure", "Dogru", "Yanlis", "Bos", "Toplam", "rowIndex"]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            # Sadece Dogru veya Yanlis varsa veya manuel girilmediyse Bos hesapla
            def calculate_bos(row):
                if row["Bos"] > 0: return row["Bos"]
                if row["Dogru"] > 0 or row["Yanlis"] > 0:
                    b = row["Toplam"] - (row["Dogru"] + row["Yanlis"])
                    return b if b >= 0 else 0
                return 0
            
            df["Bos"] = df.apply(calculate_bos, axis=1)

            df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').dt.date
            return df
        return pd.DataFrame()
    except Exception as e: 
        print(f"Hata: {e}")
        return pd.DataFrame()

def get_remote_audio_base64(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            return f"data:audio/mp3;base64,{b64}"
    except: return None


def add_task(tarih, kullanıcı, ders, konu, notlar=""):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "add", "tarih": str(tarih), "kullanici": kullanıcı, "ders": ders, "konu": konu, "durum": "Planlandı", "notlar": notlar}
    try: 
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            st.error(f"Ekleme Hatası: {response.text}")
        else:
            get_data.clear()
            # Check for generic script errors if returned as 200 JSON
            try:
                data = response.json()
                if data.get("status") == "error":
                     st.error(f"Sunucu Hatası: {data.get('message')}")
            except: pass
    except Exception as e: 
         st.error(f"Bağlantı Hatası (Ekleme): {e}")

def delete_task(row_index):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "delete", "rowIndex": row_index}
    try: 
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            st.error(f"Silme Hatası: {response.text}")
        else:
            get_data.clear()
    except Exception as e:
         st.error(f"Bağlantı Hatası (Silme): {e}")

def edit_task(row_index, tarih, ders, konu):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "edit", "rowIndex": row_index, "tarih": str(tarih), "ders": ders, "konu": konu}
    try: 
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            st.error(f"Düzenleme Hatası: {response.text}")
        else:
            get_data.clear()
    except Exception as e:
         st.error(f"Bağlantı Hatası (Düzenleme): {e}")

def update_task_progress(index, status, sure_saniye, dogru, yanlis, bos=0):
    url = st.secrets["connections"]["webapp_url"]
    payload = {
        "action": "complete", "rowIndex": index, "durum": status, 
        "sure": sure_saniye, "dogru": dogru, "yanlis": yanlis, "bos": bos
    }
    try: 
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            st.error(f"Güncelleme Hatası: {response.text}")
        else:
            get_data.clear()
            # Check JSON status
            try:
                data = response.json()
                if data.get("status") == "error":
                     st.error(f"Sunucu Hatası: {data.get('message')}")
            except: pass
    except Exception as e:
         st.error(f"Bağlantı Hatası (Güncelleme): {e}")

def log_task(tarih, kullanıcı, ders, konu, sure_saniye, dogru=0, yanlis=0, bos=0, notlar="Okuma Seansı"):
    url = st.secrets["connections"]["webapp_url"]
    toplam = dogru + yanlis + bos
    # Log directly as "Tamamlandı" with duration
    payload = {
        "action": "add", 
        "tarih": str(tarih), 
        "kullanici": kullanıcı, 
        "ders": ders, 
        "konu": konu, 
        "durum": "Tamamlandı", 
        "notlar": notlar,
        "sure": sure_saniye,
        "dogru": dogru, "yanlis": yanlis, "bos": bos, "toplam": toplam
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
             st.error(f"Log Hatası: {response.text}")
        else:
            get_data.clear()
            # Check JSON
            try:
                data = response.json()
                if data.get("status") == "error":
                     st.error(f"Sunucu Hatası (Log): {data.get('message')}")
                else:
                     st.toast("Kayıt Başarılı!", icon="✅")
            except: pass
    except Exception as e:
         st.error(f"Bağlantı Hatası (Log): {e}")

def format_timer_display(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}"

def format_text_duration(seconds):
    seconds = int(seconds)
    if seconds < 60: return f"{seconds} sn"
    mins = seconds // 60
    if mins > 60:
        hr = mins // 60
        mn = mins % 60
        return f"{hr} sa {mn} dk"
    return f"{mins} dk"

def format_date_tr(d):
    months = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }
    days = {
        0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"
    }
    return f"{d.day} {months[d.month]} {d.year} {days[d.weekday()]}"

def check_achievements(df, user, today):
   user_df = df[df["Kullanıcı"] == user]
   if user_df.empty: return []
   
   # Exclude today for historical stats
   history = user_df[user_df["Tarih"] < today]
   today_data = user_df[user_df["Tarih"] == today]
   
   if today_data.empty: return []
   
   achievements = []
   today_total = today_data["Sure"].sum()
   
   # 1. Daily Average Beat
   if not history.empty:
       daily_sums = history.groupby("Tarih")["Sure"].sum()
       avg_daily = daily_sums.mean()
       
       # Avoid celebrating trivial beating of 0 average
       if avg_daily > 60 and today_total > avg_daily:
           achievements.append(f"🚀 Harikasın {user}! Bugün ortalama performansının üzerindesin! (Ort: {format_text_duration(avg_daily)})")
           
       # 2. Record Breaker
       max_daily = daily_sums.max()
       if max_daily > 0 and today_total > max_daily:
            achievements.append(f"🏆 YENİ REKOR! Bugüne kadarki en çok çalıştığın gün! ({format_text_duration(today_total)})")

@st_fragment
def admin_add_task_fragment(dashboard_date, active_student_filter):
    with st.container(border=True):
        c1, c2 = st.columns(2)
        tarih_inp = c1.date_input("Tarih", dashboard_date)
        
        default_student_idx = 0
        student_options = ["Berru", "Ela"]
        if active_student_filter in student_options:
            default_student_idx = student_options.index(active_student_filter)
            
        kisi_inp = c1.selectbox("Öğrenci", student_options, index=default_student_idx)
        ders_inp = c2.selectbox("Ders", ["Matematik", "Fen", "Türkçe", "Sosyal", "Hayat Bilgisi", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Kitap Okuma", "Diğer"])
        
        ders_map = {"Fen": "Fen Bilimleri", "Sosyal": "İnkılap Tarihi", "Din Kültürü ve Ahlak Bilgisi": "Din Kültürü"}
        lgs_ders = ders_map.get(ders_inp, ders_inp)
        
        if lgs_ders in lm.LGS_CURRICULUM:
            secilen_konu = c2.selectbox("Konu Kılavuzu", get_topic_options(lgs_ders), key="new_task_secilen")
            if secilen_konu == "Özel (Kendin Yaz)" or secilen_konu.startswith("---"):
                konu_inp = c2.text_input("Konu (İsteğe Bağlı)")
            else:
                konu_inp = secilen_konu
        else:
            konu_inp = c2.text_input("Konu (İsteğe Bağlı)")
            
        kaynak_inp = st.text_input("Kaynak / Ödev Detayı (İsteğe Bağlı)", placeholder="Örn: Okyanus Master Sayfa 15-20", key="admin_kaynak")
        
        if st.button("Ekle", use_container_width=True, type="primary"):
            add_task(tarih_inp, kisi_inp, ders_inp, konu_inp, notlar=kaynak_inp)
            st.success("Eklendi"); time.sleep(1); st.rerun()

@st_fragment
def student_free_study_fragment(today, user):
    with st.container(border=True):
        fs_ders = st.selectbox("Hangi Derse Çalışacaksın?", 
                               ["Matematik", "Fen", "Türkçe", "Sosyal", "Hayat Bilgisi", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Diğer"], key="fs_ders")
        
        ders_map = {"Fen": "Fen Bilimleri", "Sosyal": "İnkılap Tarihi", "Din Kültürü ve Ahlak Bilgisi": "Din Kültürü"}
        fs_lgs_ders = ders_map.get(fs_ders, fs_ders)
        
        if fs_lgs_ders in lm.LGS_CURRICULUM:
            fs_secilen_konu = st.selectbox("Konu Kılavuzu", get_topic_options(fs_lgs_ders), key="fs_secilen")
            if fs_secilen_konu == "Özel (Kendin Yaz)" or fs_secilen_konu.startswith("---"):
                fs_konu_inp = st.text_input("Konu (İsteğe Bağlı)", placeholder="Örn: Kesirler Test Çözümü", key="fs_konu_input")
            else:
                fs_konu_inp = fs_secilen_konu
        else:
            fs_konu_inp = st.text_input("Konu (İsteğe Bağlı)", placeholder="Örn: Kesirler Test Çözümü", key="fs_konu_input_2")
            
        fs_kaynak_inp = st.text_input("Kaynak (İsteğe Bağlı)", placeholder="Örn: Hız Yayınları Soru Bankası", key="fs_kaynak")
        
        if not fs_konu_inp:
            fs_konu = "Serbest Çalışma"
        else:
            fs_konu = fs_konu_inp
        
        submitted = st.button("🚀 Listeme Ekle ve Başla", type="primary", use_container_width=True)
        
        if submitted:
            add_task(today, user, fs_ders, fs_konu, notlar=fs_kaynak_inp)
            st.balloons()
            st.success("Harikasın! Görev listene eklendi. 'Görevlerim' sekmesinden BAŞLA diyebilirsin. 🏃‍♀️")
            time.sleep(2)
            st.rerun()

@st_fragment
def student_countdown_fragment():
    with st.container(border=True):
        cd_ders = st.selectbox("Hangi Ders?", 
                               ["Matematik", "Fen", "Türkçe", "Sosyal", "Hayat Bilgisi", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Diğer"], key="cd_ders")
        
        ders_map = {"Fen": "Fen Bilimleri", "Sosyal": "İnkılap Tarihi", "Din Kültürü ve Ahlak Bilgisi": "Din Kültürü"}
        cd_lgs_ders = ders_map.get(cd_ders, cd_ders)
        
        if cd_lgs_ders in lm.LGS_CURRICULUM:
            cd_secilen_konu = st.selectbox("Konu Kılavuzu", get_topic_options(cd_lgs_ders), key="cd_secilen")
            if cd_secilen_konu == "Özel (Kendin Yaz)" or cd_secilen_konu.startswith("---"):
                cd_konu_inp = st.text_input("Konu (Örn: Deneme Sınavı)", placeholder="Deneme Sınavı", key="cd_konu_input")
            else:
                cd_konu_inp = cd_secilen_konu
        else:
            cd_konu_inp = st.text_input("Konu (Örn: Deneme Sınavı)", placeholder="Deneme Sınavı", key="cd_konu_input_2")
            
        cd_kaynak_inp = st.text_input("Kaynak (İsteğe Bağlı)", placeholder="Örn: Nitelik Yayınları", key="cd_kaynak")
            
        cd_sure = st.number_input("Hedef Süre (Dakika)", min_value=1, max_value=180, value=40, step=5)
        
        if not cd_konu_inp:
            cd_konu = "Süreli Test"
        else:
            cd_konu = cd_konu_inp
            
        if st.button("⏳ Geri Sayımı Başlat", type="primary", use_container_width=True):
            st.session_state.timer_active = True
            st.session_state.timer_running = False
            st.session_state.timer_start_time = None
            st.session_state.timer_accumulated = 0
            st.session_state.temp_dogru = 0
            st.session_state.temp_yanlis = 0
            st.session_state.temp_bos = 0
            st.session_state.current_task_info = {
                "ders": cd_ders, 
                "konu": cd_konu, 
                "is_countdown": True,
                "target_duration": cd_sure,
                "notlar": cd_kaynak_inp
            }
            st.rerun()

def get_topic_options(lesson):
    if lesson not in lm.LGS_CURRICULUM:
        return ["Özel (Kendin Yaz)"]
    
    curriculum = lm.LGS_CURRICULUM[lesson]
    main_topics = []
    
    for topic in curriculum:
        if ":" in topic:
            main_t = topic.split(":")[0].strip() + " (Genel)"
            if main_t not in main_topics:
                main_topics.append(main_t)
                
    options = ["Özel (Kendin Yaz)", "Karma (Tüm Konular)"]
    if main_topics:
        options.extend(["--- ANA BAŞLIKLAR ---"])
        options.extend(main_topics)
        options.extend(["--- ALT KONULAR ---"])
        
    options.extend(curriculum)
    return options

# --- 7. ANA UYGULAMA ---
def main_app():
    user = st.session_state["authenticated_user"]
    parents = ["Baba", "Anne"]
    today = get_turkey_time()
    
    with st.sidebar:
        st.title(f"Profil: {user}")
        
        current_berru_img = "https://static.wixstatic.com/media/ed30a3_d16278085bbe4c29883c16a7bf4cf9da~mv2.png/v1/fill/w_568,h_520,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/ed30a3_d16278085bbe4c29883c16a7bf4cf9da~mv2.png"
        current_ela_img = "https://i.pinimg.com/736x/67/8c/e7/678ce70749aaa819143cd1411fc26749.jpg"
        
        c_img1, c_img2, c_img3 = st.columns([1, 2, 1])
        with c_img2:
            if user == "Berru": st.image(current_berru_img, width=100)
            elif user == "Ela": st.image(current_ela_img, width=100)
            elif user == "Anne": st.image("https://cdn-icons-png.flaticon.com/512/2942/2942802.png", width=100)
            else: st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=100)
            
        st.write("---")
        


        st.write("---")
        
        # --- GÜNCELLENMİŞ ÇIKIŞ YAP BUTONU ---
        if st.button("Çıkış Yap", use_container_width=True):
            # 1. Çerezi sil
            cookie_manager.delete("study_buddy_user")
            # 2. Session state'i temizle
            st.session_state["authenticated_user"] = None
            st.session_state["logout_clicked"] = True
            # 3. Bekle ve yenile
            time.sleep(0.5)
            st.rerun()

            time.sleep(0.5)
            st.rerun()

    # --- ODAK EKRANI ---
    if st.session_state.timer_active:
        task = st.session_state.current_task_info
        is_reading_mode = task.get('ders') == "Kitap Okuma"
        is_countdown_mode = task.get('is_countdown', False)
        
        remaining = 0
        # --- Wake Lock Injection for Mobile (Keep Screen On) ---
        # We inject this every rerun if timer is active to ensure lock is requested
        st.markdown("""
            <script>
            async function triggerWakeLock() {
                try {
                    const wakeLock = await navigator.wakeLock.request('screen');
                    console.log('Wake Lock Re-triggered');
                } catch (err) { console.log(err); }
            }
            triggerWakeLock();
            </script>
        """, unsafe_allow_html=True)

        c_focus_1, c_focus_2, c_focus_3 = st.columns([1, 2, 1])
        with c_focus_2:
            st.markdown(f"<div style='text-align:center; font-size: 2rem; font-weight:bold;'>{( '📖' if is_reading_mode else '🎯' )} {task['ders']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; color:gray;'>{task['konu']}</div>", unsafe_allow_html=True)
            st.divider()

            current_time = time.time()
            
            # --- READING/COUNTDOWN MODE SPECIFIC LOGIC ---
            if is_reading_mode or is_countdown_mode:
                if is_reading_mode:
                    if "reading_duration" not in st.session_state:
                        st.session_state.reading_duration = 15 # Default
                    if not st.session_state.timer_running and st.session_state.timer_accumulated == 0:
                         st.info("Ne kadar kitap okuyacaksın?")
                         dur = st.slider("Süre (Dakika)", 5, 60, 15, step=5)
                         st.session_state.reading_duration = dur
                    target_seconds = st.session_state.get("reading_duration", 15) * 60
                else:
                    target_seconds = task.get("target_duration", 15) * 60
                
                elapsed_since_start = (current_time - st.session_state.timer_start_time) if st.session_state.timer_running else 0
                total_elapsed = st.session_state.timer_accumulated + elapsed_since_start
                remaining = max(0, target_seconds - total_elapsed)
                
# --- SAYAÇ BİTİŞ: TİTREŞİM VE GÖRSEL UYARI ---
                if remaining == 0 and st.session_state.timer_running:
                     st.session_state.timer_running = False
                     st.session_state.timer_accumulated = total_elapsed
                     
                     st.balloons()
                     st.success("🎉 SÜRE DOLDU! Harikasın!")
                     
                     js_alert = """
                        <script>
                            if (navigator.vibrate) {
                                navigator.vibrate([500, 200, 500, 200, 1000]);
                            }
                            var overlay = document.createElement('div');
                            overlay.style.position = 'fixed';
                            overlay.style.top = '0';
                            overlay.style.left = '0';
                            overlay.style.width = '100vw';
                            overlay.style.height = '100vh';
                            overlay.style.zIndex = '99999';
                            overlay.style.pointerEvents = 'none';
                            overlay.style.backgroundColor = 'rgba(233, 30, 99, 0.5)';
                            overlay.style.animation = 'flashAnimation 1s infinite';
                            document.body.appendChild(overlay);

                            var style = document.createElement('style');
                            style.innerHTML = `
                                @keyframes flashAnimation {
                                    0% { background-color: rgba(233, 30, 99, 0.0); }
                                    50% { background-color: rgba(233, 30, 99, 0.6); }
                                    100% { background-color: rgba(233, 30, 99, 0.0); }
                                }
                            `;
                            document.head.appendChild(style);

                            setTimeout(() => {
                                document.body.removeChild(overlay);
                            }, 5000);
                        </script>
                     """
                     st.markdown(js_alert, unsafe_allow_html=True)
                     st.toast("⏰ SÜRE DOLDU!", icon="🚨")
                     
                st.markdown(f"<div style='text-align: center; font-size: 80px; color: #D81B60;' class='timer-font'>{format_timer_display(remaining)}</div>", unsafe_allow_html=True)
                
            else:
                # --- STANDARD MODE (Stopwatch) ---
                elapsed = st.session_state.timer_accumulated + (current_time - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                st.markdown(f"<div style='text-align: center; font-size: 80px; color: #D81B60;' class='timer-font'>{format_timer_display(elapsed)}</div>", unsafe_allow_html=True)

            if not is_reading_mode:
                c_input1, c_input2, c_input3 = st.columns(3)
                with c_input1:
                    d_input = st.number_input("✅ Doğru", min_value=0, step=1, value=st.session_state.temp_dogru)
                    st.session_state.temp_dogru = d_input
                with c_input2:
                    y_input = st.number_input("❌ Yanlış", min_value=0, step=1, value=st.session_state.temp_yanlis)
                    st.session_state.temp_yanlis = y_input
                with c_input3:
                    b_input = st.number_input("⚪ Boş", min_value=0, step=1, value=st.session_state.temp_bos)
                    st.session_state.temp_bos = b_input
                st.caption(f"Toplam Çözülen: **{st.session_state.temp_dogru + st.session_state.temp_yanlis + st.session_state.temp_bos}** (Doğru + Yanlış + Boş)")
            else:
                 st.info("Kitap okuma saati! Sessiz ve odaklanmış kalalım. 🤫")

            st.write("")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.session_state.timer_running:
                    if st.button("⏸️ Mola Ver", use_container_width=True):
                        st.session_state.timer_accumulated += (time.time() - st.session_state.timer_start_time)
                        st.session_state.timer_running = False
                        st.rerun()
                else:
                    btn_text = "▶️ Başla" if st.session_state.timer_accumulated == 0 else "▶️ Devam Et"
                    if remaining == 0 and (is_reading_mode or is_countdown_mode) and st.session_state.timer_accumulated > 0:
                         pass # Completed, don't show Resume
                    else:
                        if st.button(btn_text, type="primary", use_container_width=True):
                            st.session_state.timer_start_time = time.time()
                            st.session_state.timer_running = True
                            st.rerun()
            
            with col_btn2:
                # Finish Logic
                finish_label = "🏁 Bitir"
                if is_reading_mode or is_countdown_mode: 
                    if remaining == 0 and st.session_state.timer_accumulated > 0:
                        finish_label = "✅ SÜRE BİTTİ - KAYDET VE BİTİR"
                    elif is_reading_mode:
                        finish_label = "✅ Okumayı Bitir"
                    else:
                        finish_label = "🏁 Testi Bitir"
                
                if st.button(finish_label, type="primary", use_container_width=True):
                    final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                    
                    if task.get("is_reading_session", False):
                         # Direct Log for Library Session
                         log_task(today, user, task['ders'], task['konu'], int(final_sec))
                    elif task.get("is_countdown", False):
                         log_task(today, user, task['ders'], task['konu'], int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis, st.session_state.temp_bos, task.get("notlar", "Süreli Soru"))
                    else:
                        # Update Task Progress for Normal Tasks
                        update_task_progress(task['index'], "Tamamlandı", int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis, st.session_state.temp_bos)
                    
                    if task.get("ders") != "Kitap Okuma":
                         added_qs = st.session_state.temp_dogru + st.session_state.temp_yanlis + st.session_state.temp_bos
                         if added_qs > 0:
                             st.session_state.check_goal_progress = True
                    
                    st.session_state.timer_active = False
                    st.session_state.timer_running = False
                    st.session_state.timer_accumulated = 0
                    st.session_state.temp_dogru = 0
                    st.session_state.temp_yanlis = 0
                    st.session_state.temp_bos = 0
                    if "reading_duration" in st.session_state: del st.session_state.reading_duration
                    st.balloons(); time.sleep(1.5); st.rerun()

            st.write("")
            # Save for Later (Not relevant for Reading Mode usually, but kept for consistency)
            if not is_reading_mode and not is_countdown_mode and st.button("💾 Kaydet ve Çık (Bitmedi)", use_container_width=True):
                final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                update_task_progress(task['index'], "Beklemede", int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis, st.session_state.temp_bos)
                st.session_state.timer_active = False
                st.session_state.timer_running = False
                st.session_state.timer_accumulated = 0
                st.session_state.temp_dogru = 0
                st.session_state.temp_yanlis = 0
                st.session_state.temp_bos = 0
                st.rerun()
            elif (is_reading_mode or is_countdown_mode) and st.button("🔙 İptal / Çık", use_container_width=True):
                 st.session_state.timer_active = False
                 st.session_state.timer_running = False
                 st.session_state.temp_dogru = 0
                 st.session_state.temp_yanlis = 0
                 st.session_state.temp_bos = 0
                 if "reading_duration" in st.session_state: del st.session_state.reading_duration
                 st.rerun()

        if st.session_state.timer_running: time.sleep(1); st.rerun()
        return

    # --- ANA SAYFA ---
    st.markdown('<div class="main-title">Study Buddy</div>', unsafe_allow_html=True)
    df = get_data()

    if st.session_state.get("check_goal_progress", False):
        st.session_state.check_goal_progress = False
        user_settings = load_settings()
        my_settings = user_settings.get(user, None)
        if my_settings and not df.empty:
            if my_settings["type"] == "Haftalık":
                start_date = today - timedelta(days=today.weekday())
                end_date = start_date + timedelta(days=6)
                goal_data = df[(df["Kullanıcı"] == user) & (df["Ders"] != "Kitap Okuma") & (pd.to_datetime(df["Tarih"]).dt.date >= start_date) & (pd.to_datetime(df["Tarih"]).dt.date <= end_date)]
            else:
                goal_data = df[(df["Kullanıcı"] == user) & (df["Ders"] != "Kitap Okuma") & (pd.to_datetime(df["Tarih"]).dt.month == today.month) & (pd.to_datetime(df["Tarih"]).dt.year == today.year)]
            current_total = goal_data["Dogru"].sum() + goal_data["Yanlis"].sum() + goal_data["Bos"].sum()
            target = my_settings["target"]
            if current_total >= target:
                st.toast(f"🎉 TEBRİKLER! {my_settings['type']} hedefin olan {target} soruya ulaştın!", icon="🏆")
                st.balloons()
            else:
                kalan = target - current_total
                st.toast(f"Harika gidiyorsun! {my_settings['type']} hedefine ulaşmak için son {kalan} soru kaldı! 💪", icon="🎯")

    active_student_filter = user 
    
    if user in parents:
        img_berru_src = "https://static.wixstatic.com/media/ed30a3_d16278085bbe4c29883c16a7bf4cf9da~mv2.png/v1/fill/w_568,h_520,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/ed30a3_d16278085bbe4c29883c16a7bf4cf9da~mv2.png"
        img_ela_src = "https://i.pinimg.com/736x/67/8c/e7/678ce70749aaa819143cd1411fc26749.jpg"
        img_all_src = "https://cdn-icons-png.flaticon.com/512/681/681494.png"

        c_space1, c_sel_all, c_sel_berru, c_sel_ela, c_space2 = st.columns([2, 1, 1, 1, 2])
        
        with c_sel_all:
            st.markdown(f"<img src='{img_all_src}' style='width:60px; height:60px; object-fit:cover; border-radius:50%; display:block; margin: 0 auto 10px auto;'>", unsafe_allow_html=True)
            btn_type = "primary" if st.session_state.global_student_selection == "Tümü" else "secondary"
            if st.button("Tümü", key="btn_all", type=btn_type, use_container_width=True):
                st.session_state.global_student_selection = "Tümü"
                st.rerun()

        with c_sel_berru:
            st.markdown(f"<img src='{img_berru_src}' style='width:60px; height:60px; object-fit:cover; border-radius:50%; display:block; margin: 0 auto 10px auto;'>", unsafe_allow_html=True)
            btn_type = "primary" if st.session_state.global_student_selection == "Berru" else "secondary"
            if st.button("Berru", key="btn_berru", type=btn_type, use_container_width=True):
                st.session_state.global_student_selection = "Berru"
                st.rerun()
                
        with c_sel_ela:
            st.markdown(f"<img src='{img_ela_src}' style='width:60px; height:60px; object-fit:cover; border-radius:50%; display:block; margin: 0 auto 10px auto;'>", unsafe_allow_html=True)
            btn_type = "primary" if st.session_state.global_student_selection == "Ela" else "secondary"
            if st.button("Ela", key="btn_ela", type=btn_type, use_container_width=True):
                st.session_state.global_student_selection = "Ela"
                st.rerun()
        
        if st.session_state.global_student_selection == "Tümü":
            active_student_filter = None
        else:
            active_student_filter = st.session_state.global_student_selection
    
    st.divider()

    if not df.empty:
        filtered_df = df if active_student_filter is None else df[df["Kullanıcı"] == active_student_filter]

        c_p1, c_p2 = st.columns([1, 2])
        with c_p1:
             dashboard_date = st.date_input("Tarih", value=today, label_visibility="collapsed", key="dash_date_pick")
        with c_p2:
             period = st.radio("", ["Günlük", "Haftalık", "Aylık"], horizontal=True, label_visibility="collapsed")
        
        dashboard_data = pd.DataFrame()
        if period == "Günlük":
            dashboard_data = filtered_df[filtered_df["Tarih"] == dashboard_date]
            metric_label = f"{format_date_tr(dashboard_date)}"
        elif period == "Haftalık":
            start_week = dashboard_date - timedelta(days=dashboard_date.weekday())
            end_week = start_week + timedelta(days=6)
            dashboard_data = filtered_df[(filtered_df["Tarih"] >= start_week) & (filtered_df["Tarih"] <= end_week)]
            metric_label = "Seçilen Hafta"
        elif period == "Aylık":
            dates = pd.to_datetime(filtered_df["Tarih"], errors='coerce')
            dashboard_data = filtered_df[(dates.dt.month == dashboard_date.month) & (dates.dt.year == dashboard_date.year)]
            metric_label = "Seçilen Ay"

        # --- MOTIVATIONAL MESSAGES ---
        if active_student_filter and period == "Günlük" and dashboard_date == today:
            achievements = check_achievements(filtered_df, active_student_filter, today)
            if achievements:
                for msg in achievements:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(45deg, #F8BBD0, #F48FB1);
                        padding: 15px;
                        border-radius: 10px;
                        color: #880E4F;
                        font-weight: bold;
                        margin-bottom: 20px;
                        text-align: center;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        border: 2px solid #EC407A;
                        animation: pulse 2s infinite;
                    ">
                    {msg}
                    </div>
                    <style>
                        @keyframes pulse {{
                            0% {{ box-shadow: 0 0 0 0 rgba(233, 30, 99, 0.4); }}
                            70% {{ box-shadow: 0 0 0 10px rgba(233, 30, 99, 0); }}
                            100% {{ box-shadow: 0 0 0 0 rgba(233, 30, 99, 0); }}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                    st.balloons()

        total_time = format_text_duration(dashboard_data["Sure"].sum())
        question_data = dashboard_data[dashboard_data["Ders"] != "Kitap Okuma"]
        total_questions = question_data["Dogru"].sum() + question_data["Yanlis"].sum() + question_data["Bos"].sum()
        total_correct = dashboard_data["Dogru"].sum()
        total_wrong = dashboard_data["Yanlis"].sum()
        completed_count = len(dashboard_data[dashboard_data["Durum"] == "Tamamlandı"])
        
        # Calculate Reading Time
        reading_data = dashboard_data[dashboard_data["Ders"] == "Kitap Okuma"]
        total_reading_time = format_text_duration(reading_data["Sure"].sum())

        # --- ÖZEL METRİK KARTLARI (ANİMASYONLU) ---
        # --- ÖZEL METRİK KARTLARI (ANİMASYONLU) ---
        # Not: Markdown code-block olmaması için indentation kaldırıldı
        metric_html = f"""
<style>
.metric-container {{
    display: flex;
    justify-content: space-between;
    background-color: rgba(255, 255, 255, 0.8);
    padding: 15px;
    border-radius: 15px;
    border: 2px solid #F48FB1;
    box-shadow: 0 4px 10px rgba(233, 30, 99, 0.1);
    margin-bottom: 20px;
    gap: 10px;
    flex-wrap: wrap;
}}
.metric-card {{
    flex: 1;
    text-align: center;
    padding: 5px;
    min-width: 80px;
}}
.metric-icon {{ font-size: 1.8rem; margin-bottom: 0px; display: block; }}
.metric-value {{ 
    font-size: 1.6rem; 
    font-weight: 800; 
    color: #D81B60;
    font-family: 'Quicksand', sans-serif;
}}
.metric-label {{ 
    font-size: 0.8rem; 
    font-weight: 700; 
    color: #880E4F; 
    text-transform: uppercase;
}}
</style>

<div class="metric-container">
    <div class="metric-card">
        <span class="metric-icon">🧸</span>
        <div class="metric-value">{total_time}</div>
        <div class="metric-label">Toplam Süre</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">📚</span>
        <div class="metric-value">{total_reading_time}</div>
        <div class="metric-label">Kitap</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">🏆</span>
        <div class="metric-value"><span class='animate-num' data-end='{total_questions}'>{total_questions}</span></div>
        <div class="metric-label">Soru</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">💖</span>
        <div class="metric-value"><span class='animate-num' data-end='{total_correct}'>{total_correct}</span></div>
        <div class="metric-label">Doğru</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">🥀</span>
        <div class="metric-value"><span class='animate-num' data-end='{total_wrong}'>{total_wrong}</span></div>
        <div class="metric-label">Yanlış</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">☁️</span>
        <div class="metric-value"><span class='animate-num' data-end='{dashboard_data["Bos"].sum() if not dashboard_data.empty else 0}'>{dashboard_data["Bos"].sum() if not dashboard_data.empty else 0}</span></div>
        <div class="metric-label">Boş</div>
    </div>
</div>

<script>
function animateValue(obj, start, end, duration) {{
    let startTimestamp = null;
    const step = (timestamp) => {{
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {{
            window.requestAnimationFrame(step);
        }}
    }};
    window.requestAnimationFrame(step);
}}

const animatedElements = window.parent.document.querySelectorAll('.animate-num'); 
/* Streamlit iframe sandboxing might require aggressive selection or direct execution within same frame if markdown is safe */
/* Trying standard selection first, often works in markdown with unsafe_allow_html */
const localElements = document.querySelectorAll('.animate-num');
localElements.forEach(el => {{
    const endVal = parseInt(el.getAttribute('data-end'));
    if (!isNaN(endVal)) {{
       animateValue(el, 0, endVal, 1500);
    }}
}});
</script>
"""
        st.markdown(metric_html, unsafe_allow_html=True)
        
        # --- CSS for Ribbons & Table Headers ---
        st.markdown("""
        <style>
        /* Ribbon style */
        .ribbon-title {
            position: relative;
            background: #F06292;
            color: white;
            padding: 5px 20px;
            font-size: 1.2rem;
            border-radius: 5px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
            font-family: 'Quicksand', sans-serif;
            margin-bottom: 20px;
            margin-top: 28px; /* Align with Date Picker Input (Label offset) */
            display: inline-block;
        }
        .ribbon-title:after {
            content: '';
            position: absolute;
            top: 10px;
            right: -10px;
            border-top: 15px solid #C2185B;
            border-right: 15px solid transparent;
        }
        
        /* Table Header Style */
        .table-header {
            background-color: #F8BBD0;
            color: #880E4F;
            padding: 8px 4px; /* Reduced side padding */
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            font-family: 'Quicksand', sans-serif;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            white-space: nowrap; /* Prevent wrapping */
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: clamp(0.7rem, 1vw, 1rem); /* Responsive font size */
        }
        </style>
        """, unsafe_allow_html=True)
        
        if period != "Günlük" and not dashboard_data.empty:
            with st.expander(f"📊 {metric_label} Performans Grafiği", expanded=True):
                # Pembe renkli bar chart
                chart_data = dashboard_data.groupby("Ders")["Dogru"].sum()
                st.bar_chart(chart_data, color="#EC407A")

    st.write("---")

    # Adjusted ratios: Increased 'Öğrenci' (0.8 -> 1.1), Reduced '#' (0.4 -> 0.3)
    col_ratios = [0.3, 1.1, 1.2, 3.0, 1.2, 0.8, 0.6, 0.6, 0.6, 0.8, 1.5]
    
    def show_task_table(data, is_admin=False):
        if data.empty:
            st.info("Bu tarihte kayıtlı görev yok.", icon=":material/info:")
            return

        header_cols = st.columns(col_ratios)
        titles = ["#", "Öğrenci", "Ders", "Konu", "Durum", "Süre", "D", "Y", "B", "T", "İşlemler"]
        
        for col, title in zip(header_cols, titles):
            col.markdown(f"<div class='table-header'>{title}</div>", unsafe_allow_html=True)
        
        st.markdown("---") 

        for index, row in enumerate(data.itertuples(), start=1):
            if is_admin and st.session_state.edit_mode_index == row.rowIndex:
                with st.container(border=True):
                    st.info(f"Düzenleniyor: {row.Kullanıcı} - {row.Ders}")
                    with st.form(f"edit_form_{index}"):
                        c_edit1, c_edit2, c_edit3 = st.columns(3)
                        ders_list = ["Matematik", "Fen", "Türkçe", "Sosyal", "Hayat Bilgisi", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Kitap Okuma", "Diğer"]
                        current_ders_idx = ders_list.index(row.Ders) if row.Ders in ders_list else 0
                        
                        new_tarih = c_edit1.date_input("Tarih", value=row.Tarih)
                        new_ders = c_edit2.selectbox("Ders", ders_list, index=current_ders_idx)
                        new_konu = c_edit3.text_input("Konu", value=row.Konu)
                        
                        c_save, c_cancel = st.columns([1, 1])
                        if c_save.form_submit_button("Kaydet", icon=":material/save:", use_container_width=True, type="primary"):
                            edit_task(row.rowIndex, new_tarih, new_ders, new_konu)
                            st.session_state.edit_mode_index = None
                            st.toast("Başarıyla Güncellendi!")
                            time.sleep(1)
                            st.rerun()
                        if c_cancel.form_submit_button("İptal", icon=":material/close:", use_container_width=True):
                            st.session_state.edit_mode_index = None
                            st.rerun()
            else:
                row_cols = st.columns(col_ratios)
                row_cols[0].write(f"{index}")
                row_cols[1].write(row.Kullanıcı)
                row_cols[2].write(row.Ders)
                row_cols[3].write(row.Konu)
                
                with row_cols[4]:
                    # Status Badge Rendering (Icons Only)
                    if row.Durum == "Tamamlandı":
                        st.markdown(f"<span class='status-badge badge-done'>🌟</span>", unsafe_allow_html=True)
                    elif row.Durum == "Planlandı":
                        st.markdown(f"<span class='status-badge badge-planned'>📅</span>", unsafe_allow_html=True)
                    elif row.Durum == "Beklemede":
                        st.markdown(f"<span class='status-badge badge-waiting'>⏳</span>", unsafe_allow_html=True)
                    elif row.Durum == "Çalışılıyor":
                         st.markdown(f"<span class='status-badge badge-working'>🔥</span>", unsafe_allow_html=True)
                    else:
                        st.write(row.Durum)
                
                row_cols[5].write(format_text_duration(row.Sure))
                row_cols[6].write(f"{row.Dogru}")
                row_cols[7].write(f"{row.Yanlis}")
                row_cols[8].write(f"{row.Bos}")
                row_cols[9].write(f"{row.Toplam}")
                
                with row_cols[10]:
                    if is_admin:
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("", icon=":material/edit:", key=f"btn_edit_{row.rowIndex}", use_container_width=True):
                                st.session_state.edit_mode_index = row.rowIndex
                                st.rerun()
                        with b2:
                            if st.button("", icon=":material/delete:", key=f"btn_del_{row.rowIndex}", type="primary", use_container_width=True):
                                delete_task(row.rowIndex)
                                st.toast("Görev silindi!", icon=":material/delete:")
                                time.sleep(1)
                                st.rerun()
                    else:
                        if row.Durum != "Tamamlandı":
                            btn_txt = "DEVAM" if row.Sure > 0 else "BAŞLA"
                            btn_style = "primary" if row.Sure > 0 else "secondary"
                            if st.button(btn_txt, key=f"b_{index}", type=btn_style, use_container_width=True):
                                st.session_state.timer_active = True
                                st.session_state.timer_running = True
                                st.session_state.timer_start_time = time.time()
                                st.session_state.timer_accumulated = row.Sure
                                st.session_state.temp_dogru = row.Dogru
                                st.session_state.temp_yanlis = row.Yanlis
                                st.session_state.temp_bos = row.Bos
                                st.session_state.current_task_info = {"index": row.rowIndex, "ders": row.Ders, "konu": row.Konu}
                                update_task_progress(row.rowIndex, "Çalışılıyor", row.Sure, row.Dogru, row.Yanlis, row.Bos)
                                st.rerun()
                        else:
                            st.button("Bitti", disabled=True, key=f"d_{index}", use_container_width=True)
                
                st.divider()

    def render_lgs_tab(active_user, is_admin=False, active_student_filter=None):
        webapp_url = st.secrets.get("connections", {}).get("webapp_url") if "connections" in st.secrets else None

        header_col1, header_col2 = st.columns([5, 1])
        with header_col1:
            if is_admin:
                student_name = active_student_filter if active_student_filter and active_student_filter != "Tümü" else "Berru"
                st.markdown(f"<div class='ribbon-title'>🎯 LGS Deneme Takibi & Analizi ({student_name})</div>", unsafe_allow_html=True)
            else:
                student_name = active_user
                st.markdown(f"<div class='ribbon-title'>🎯 LGS Deneme Sınavlarım & Madde Analizi</div>", unsafe_allow_html=True)
        with header_col2:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if webapp_url:
                if st.button("🔄 Yenile", key="lgs_sync_refresh", help="Google Sheets'ten en güncel LGS denemelerini çeker", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.caption("💾 Yerel Mod (Bulut bağlantısı yok)")

        exams = lm.get_student_exams(student_name, api_url=webapp_url)

        lgs_sub1, lgs_sub2, lgs_sub3, lgs_sub4, lgs_sub5 = st.tabs([
            "📊 Son Deneme & Gelişim (Delta)",
            "📚 Konu Karnesi & Eksik Konu Alarmı",
            "📈 Gelişim Grafikleri",
            "➕ Yeni Deneme Ekle",
            "📋 Tüm Denemeler"
        ])

        # --- SUB-TAB 1: SON DENEME & GELİŞİM (DELTA) ---
        with lgs_sub1:
            if not exams:
                st.info("ℹ️ Henüz kayıtlı LGS denemeniz bulunmuyor. '➕ Yeni Deneme Ekle' sekmesinden ilk denemenizi ekleyebilirsiniz!", icon="🎯")
            else:
                latest = exams[0]
                tarih_display = format_date_tr(pd.to_datetime(latest.get('tarih')).date()) if latest.get('tarih') else str(today)
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #FFF0F5 0%, #FCE4EC 100%); border: 2px solid #F48FB1; border-radius: 18px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(233,30,99,0.1);'>
                    <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;'>
                        <div>
                            <span style='font-size: 1.35rem; font-weight: 800; color: #880E4F;'>🏆 {latest.get('deneme_adi', 'LGS Deneme Sınavı')}</span>
                            <span style='background: #F8BBD0; color: #880E4F; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; margin-left: 10px;'>{latest.get('yayin', 'Yayın')}</span>
                        </div>
                        <div style='color: #AD1457; font-weight: 700; font-size: 0.95rem;'>
                            📅 {tarih_display} &nbsp;|&nbsp; ⏱️ {latest.get('sure_dk', 155)} dk &nbsp;|&nbsp; 🎯 Zorluk: {latest.get('zorluk', 'Orta')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 5 Big Metric Cards
                m_c1, m_c2, m_c3, m_c4, m_c5 = st.columns(5)
                with m_c1:
                    st.metric("Toplam Net", f"{latest.get('toplam_net', 0):.2f} / 90")
                with m_c2:
                    st.metric("Tahmini LGS Puanı", f"{latest.get('tahmini_puan', 0):.1f} / 500")
                with m_c3:
                    st.metric("Doğru / Yanlış / Boş", f"{latest.get('toplam_dogru', 0)}D - {latest.get('toplam_yanlis', 0)}Y - {latest.get('toplam_bos', 0)}B")
                with m_c4:
                    st.metric("Sözel Net", f"{latest.get('sozel_net', 0):.2f} / 50")
                with m_c5:
                    st.metric("Sayısal Net", f"{latest.get('sayisal_net', 0):.2f} / 40")

                if latest.get("notlar"):
                    st.info(f"💡 **Deneme Notları:** {latest.get('notlar')}")

                # DELTA ANALİZİ (Eğer 2 veya daha fazla deneme varsa)
                if len(exams) >= 2:
                    prev = exams[1]
                    delta = lm.get_delta_analysis(latest, prev)

                    st.markdown("<hr style='margin: 25px 0; border: none; border-top: 2px dashed #F48FB1;'>", unsafe_allow_html=True)
                    st.markdown(f"### 🚀 Önceki Denemeye Göre Ne Değişti?")
                    st.caption(f"Karşılaştırılan: **{prev.get('deneme_adi', 'Önceki Deneme')}** ({prev.get('tarih')}) ➡️ **{latest.get('deneme_adi', 'Son Deneme')}** ({latest.get('tarih')})")

                    # Delta summary cards
                    d_c1, d_c2, d_c3, d_c4 = st.columns(4)
                    
                    net_diff = delta['delta_net']
                    puan_diff = delta['delta_puan']
                    yanlis_diff = delta['delta_yanlis']
                    sayisal_diff = delta['delta_sayisal_net']

                    with d_c1:
                        badge_cls = "delta-badge-pos" if net_diff > 0 else "delta-badge-neg" if net_diff < 0 else "delta-badge-neu"
                        arrow = "🔼" if net_diff > 0 else "🔻" if net_diff < 0 else "➖"
                        st.markdown(f"""
                        <div style='background: white; border: 1.5px solid #F8BBD0; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.03);'>
                            <div style='color: #880E4F; font-size: 0.85rem; font-weight: 700;'>Toplam Net Farkı</div>
                            <div style='margin: 6px 0;'><span class='{badge_cls}'>{"+" if net_diff > 0 else ""}{net_diff:.2f} Net {arrow}</span></div>
                            <div style='font-size: 0.75rem; color: #666;'>Önceki: {prev.get('toplam_net', 0):.2f} ➡️ Yeni: {latest.get('toplam_net', 0):.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with d_c2:
                        badge_cls = "delta-badge-pos" if puan_diff > 0 else "delta-badge-neg" if puan_diff < 0 else "delta-badge-neu"
                        arrow = "🚀" if puan_diff > 0 else "🔻" if puan_diff < 0 else "➖"
                        st.markdown(f"""
                        <div style='background: white; border: 1.5px solid #F8BBD0; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.03);'>
                            <div style='color: #880E4F; font-size: 0.85rem; font-weight: 700;'>LGS Puan Farkı</div>
                            <div style='margin: 6px 0;'><span class='{badge_cls}'>{"+" if puan_diff > 0 else ""}{puan_diff:.1f} Puan {arrow}</span></div>
                            <div style='font-size: 0.75rem; color: #666;'>Önceki: {prev.get('tahmini_puan', 0):.1f} ➡️ Yeni: {latest.get('tahmini_puan', 0):.1f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with d_c3:
                        badge_cls = "delta-badge-pos" if yanlis_diff < 0 else "delta-badge-neg" if yanlis_diff > 0 else "delta-badge-neu"
                        arrow = "📉 (Azaldı ✨)" if yanlis_diff < 0 else "📈 (Arttı ⚠️)" if yanlis_diff > 0 else "➖"
                        st.markdown(f"""
                        <div style='background: white; border: 1.5px solid #F8BBD0; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.03);'>
                            <div style='color: #880E4F; font-size: 0.85rem; font-weight: 700;'>Yanlış Soru Farkı</div>
                            <div style='margin: 6px 0;'><span class='{badge_cls}'>{"+" if yanlis_diff > 0 else ""}{yanlis_diff} Yanlış {arrow}</span></div>
                            <div style='font-size: 0.75rem; color: #666;'>Önceki: {prev.get('toplam_yanlis', 0)}Y ➡️ Yeni: {latest.get('toplam_yanlis', 0)}Y</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with d_c4:
                        badge_cls = "delta-badge-pos" if sayisal_diff > 0 else "delta-badge-neg" if sayisal_diff < 0 else "delta-badge-neu"
                        arrow = "🔼" if sayisal_diff > 0 else "🔻" if sayisal_diff < 0 else "➖"
                        st.markdown(f"""
                        <div style='background: white; border: 1.5px solid #F8BBD0; border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.03);'>
                            <div style='color: #880E4F; font-size: 0.85rem; font-weight: 700;'>Sayısal Net Farkı</div>
                            <div style='margin: 6px 0;'><span class='{badge_cls}'>{"+" if sayisal_diff > 0 else ""}{sayisal_diff:.2f} Net {arrow}</span></div>
                            <div style='font-size: 0.75rem; color: #666;'>Sözel Net Farkı: {"+" if delta['delta_sozel_net'] > 0 else ""}{delta['delta_sozel_net']:.2f} Net</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### 🎯 Ders Bazlı Değişim Raporu")
                    
                    lesson_rows = []
                    for l_name, l_info in lm.LGS_LESSONS.items():
                        l_data = delta["lesson_deltas"].get(l_name, {})
                        d_net = l_data.get("delta_net", 0.0)
                        c_net = l_data.get("current_net", 0.0)
                        p_net = l_data.get("previous_net", 0.0)
                        d_d = l_data.get("delta_d", 0)
                        d_y = l_data.get("delta_y", 0)
                        d_b = l_data.get("delta_b", 0)
                        
                        durum = "🚀 Yükseliş" if d_net > 0 else "🔻 Düşüş" if d_net < 0 else "➖ Sabit"
                        
                        lesson_rows.append({
                            "Ders": f"{l_info['icon']} {l_name}",
                            "Önceki Net": f"{p_net:.2f}",
                            "Son Net": f"{c_net:.2f}",
                            "Net Farkı (Δ)": f"{'+' if d_net > 0 else ''}{d_net:.2f}",
                            "Doğru Değişimi": f"{'+' if d_d > 0 else ''}{d_d} D",
                            "Yanlış Değişimi": f"{'+' if d_y > 0 else ''}{d_y} Y",
                            "Boş Değişimi": f"{'+' if d_b > 0 else ''}{d_b} B",
                            "Durum": durum
                        })
                    
                    st.dataframe(pd.DataFrame(lesson_rows), use_container_width=True, hide_index=True)

                    # Konu / Madde Değişimi Bildirimleri
                    if delta.get("improved_topics") or delta.get("regressed_topics"):
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("#### 🔍 Madde Analizi İlerlemeleri & Uyarılar")
                        
                        if delta.get("improved_topics"):
                            st.success("🎉 **Hatalar Telafi Edildi & Doğruya Dönüştü:**")
                            for imp in delta["improved_topics"]:
                                st.markdown(f"- **{imp['ders']} - {imp['konu']}**: {imp['mesaj']}")
                                
                        if delta.get("regressed_topics"):
                            st.warning("⚠️ **Tekrar Edilmesi Gereken Konular (Yeni Yanlışlar):**")
                            for reg in delta["regressed_topics"]:
                                st.markdown(f"- **{reg['ders']} - {reg['konu']}**: {reg['mesaj']}")

                    # İki Deneme Seçmeli Kıyaslama Aracı
                    with st.expander("⚖️ İki Denemeyi Yan Yana Kıyasla (Detaylı Grafik & Analiz)", expanded=False):
                        exam_names = [f"{e.get('tarih')} - {e.get('deneme_adi', '')}" for e in exams]
                        col_k1, col_k2 = st.columns(2)
                        with col_k1:
                            sel_idx1 = st.selectbox("1. Deneme (Güncel)", range(len(exams)), format_func=lambda i: exam_names[i], index=0, key="sel_k1")
                        with col_k2:
                            sel_idx2 = st.selectbox("2. Deneme (Karşılaştırılan)", range(len(exams)), format_func=lambda i: exam_names[i], index=1 if len(exams) > 1 else 0, key="sel_k2")
                            
                        ex_sel1 = exams[sel_idx1]
                        ex_sel2 = exams[sel_idx2]
                        
                        fig_comp = lm.create_lesson_comparison_bar(ex_sel1, ex_sel2)
                        if fig_comp:
                            st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("✨ Harika! İlk LGS denemeniz sisteme kaydedildi. İkinci bir deneme eklediğinizde 'Önceki Denemeye Göre Değişim (Delta)' analizi burada otomatik olarak görüntülenecektir.")

        # --- SUB-TAB 2: KONU KARNESİ & EKSİK KONU ALARMI ---
        with lgs_sub2:
            st.subheader("📚 Konu Karnesi & Eksik Konu Alarmı (Madde Analizi)")
            st.markdown("Denemelerde çözülen tüm soruların konu bazlı birikimli analizi ve başarı oranları.")
            
            topic_report = lm.get_topic_mastery_report(student_name, api_url=webapp_url)
            
            if not topic_report["all_topics"]:
                st.info("ℹ️ Henüz konu bazlı madde analizi girilmiş deneme bulunmuyor. Yeni deneme eklerken '⭐ Detaylı Madde Analizi' seçeneğini işaretleyerek konu bazında soru ve doğru/yanlış sayılarını girebilirsiniz!")
            else:
                col_tr1, col_tr2 = st.columns(2)
                with col_tr1:
                    st.markdown("#### 🚨 Öncelikli Tekrar Edilmesi Gereken Konular")
                    if topic_report["trouble_topics"]:
                        for t in topic_report["trouble_topics"][:6]:
                            st.markdown(f"""
                            <div class='trouble-card'>
                                <div style='font-weight: 800; color: #E65100;'>{lm.LGS_LESSONS.get(t['ders'], {}).get('icon', '📌')} {t['ders']} - {t['konu']}</div>
                                <div style='font-size: 0.85rem; color: #5D4037; margin-top: 4px;'>
                                    <b>{t['toplam_yanlis']} Yanlış</b>, {t['toplam_bos']} Boş / {t['toplam_soru']} Soru &nbsp;|&nbsp; 
                                    Başarı: <b>%{t['basari_yuzdesi']}</b> (Net: {t['toplam_net']:.2f})
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("Tebrikler! Belirgin bir eksik konu alarmı bulunmuyor. 🌟")
                        
                with col_tr2:
                    st.markdown("#### ⭐ Ustalaşılan Konular (%85+ Başarı)")
                    if topic_report["mastered_topics"]:
                        for t in topic_report["mastered_topics"][:6]:
                            st.markdown(f"""
                            <div class='mastered-card'>
                                <div style='font-weight: 800; color: #1B5E20;'>{lm.LGS_LESSONS.get(t['ders'], {}).get('icon', '⭐')} {t['ders']} - {t['konu']}</div>
                                <div style='font-size: 0.85rem; color: #2E7D32; margin-top: 4px;'>
                                    <b>{t['toplam_dogru']} Doğru</b> / {t['toplam_soru']} Soru &nbsp;|&nbsp; 
                                    Başarı Oranı: <b>%{t['basari_yuzdesi']}</b>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Daha fazla deneme çözdükçe ustalaştığın konular burada parlayacak! ✨")
                        
                st.markdown("---")
                st.markdown("#### 📊 Ders Bazlı Konu Başarı Grafiği")
                lesson_filter = st.selectbox("Ders Seçin", ["Tüm Dersler"] + list(lm.LGS_LESSONS.keys()), key="lgs_topic_lesson_filter")
                
                fig_topic = lm.create_topic_mastery_chart(topic_report["all_topics"], lesson_filter)
                if fig_topic:
                    st.plotly_chart(fig_topic, use_container_width=True)
                    
                with st.expander("📋 Tüm Konuların Ayrıntılı Tablosu"):
                    df_topics = pd.DataFrame(topic_report["all_topics"])
                    df_topics = df_topics.rename(columns={
                        "ders": "Ders", "konu": "Konu", "toplam_soru": "Toplam Soru",
                        "toplam_dogru": "Doğru", "toplam_yanlis": "Yanlış", "toplam_bos": "Boş",
                        "toplam_net": "Toplam Net", "basari_yuzdesi": "Başarı %", "deneme_sayisi": "Çıktığı Deneme Sayısı"
                    })
                    st.dataframe(df_topics, use_container_width=True, hide_index=True)

        # --- SUB-TAB 3: GELİŞİM GRAFİKLERİ ---
        with lgs_sub3:
            st.subheader("📈 LGS Gelişim Grafikleri & Trendler")
            if not exams:
                st.info("ℹ️ Grafikleri görüntülemek için en az 1 deneme kaydetmelisiniz.")
            else:
                nets = [e.get('toplam_net', 0) for e in exams]
                scores = [e.get('tahmini_puan', 0) for e in exams]
                
                st_c1, st_c2, st_c3, st_c4 = st.columns(4)
                st_c1.metric("En Yüksek Net", f"{max(nets):.2f} Net")
                st_c2.metric("En Yüksek LGS Puanı", f"{max(scores):.1f} Puan")
                st_c3.metric("Ortalama Net", f"{sum(nets)/len(nets):.2f} Net")
                st_c4.metric("Toplam Deneme", f"{len(exams)} Adet")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                fig_trend = lm.create_net_and_score_trend_chart(exams)
                if fig_trend:
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                fig_lesson_trend = lm.create_lesson_trend_chart(exams)
                if fig_lesson_trend:
                    st.plotly_chart(fig_lesson_trend, use_container_width=True)

        # --- SUB-TAB 4: YENİ DENEME EKLE ---
        with lgs_sub4:
            st.subheader("➕ Yeni LGS Deneme Sınavı Ekle")
            
            with st.container(border=True):
                c_h1, c_h2, c_h3 = st.columns(3)
                
                if is_admin:
                    student_opt = ["Berru", "Ela"]
                    def_st_idx = student_opt.index(student_name) if student_name in student_opt else 0
                    exam_student = c_h1.selectbox("Öğrenci", student_opt, index=def_st_idx, key="lgs_add_st")
                else:
                    exam_student = student_name
                    c_h1.text_input("Öğrenci", value=student_name, disabled=True)
                    
                exam_name = c_h2.text_input("Deneme Adı", placeholder="Örn: Özdebir Türkiye Geneli 1", key="lgs_add_name")
                exam_publisher = c_h3.text_input("Yayın / Kurum", placeholder="Örn: Özdebir, Töder, Nitelik", key="lgs_add_pub")
                
                c_h4, c_h5, c_h6 = st.columns(3)
                exam_date = c_h4.date_input("Deneme Tarihi", value=today, key="lgs_add_date")
                exam_duration = c_h5.number_input("Süre (Dakika)", min_value=30, max_value=300, value=155, step=5, key="lgs_add_dur")
                exam_difficulty = c_h6.selectbox("Zorluk Derecesi", ["Kolay", "Orta", "Zor", "Çok Zor"], index=1, key="lgs_add_diff")
                
                exam_notes = st.text_input("Deneme Notları / Görüşler (İsteğe Bağlı)", placeholder="Örn: Matematikte yeni nesil geometri soruları zordu.", key="lgs_add_notes")
                
                st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                
                input_mode = st.radio(
                    "📌 Giriş Yöntemi Seçin:",
                    ["🟢 Hızlı Giriş (Sadece Ders D/Y/B Sayıları)", "⭐ Detaylı Madde Analizi (Konu Bazlı Soru ve D/Y Girişi)"],
                    horizontal=True,
                    key="lgs_input_mode"
                )
                
                is_detailed = "Detaylı" in input_mode
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_sozel, col_sayisal = st.columns(2)
                
                dersler_payload = {}
                
                # SÖZEL BÖLÜM
                with col_sozel:
                    st.markdown("### 📖 Sözel Bölüm (50 Soru)")
                    sozel_lessons = ["Türkçe", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]
                    
                    for l_name in sozel_lessons:
                        l_info = lm.LGS_LESSONS[l_name]
                        max_s = l_info["soru_sayisi"]
                        
                        with st.expander(f"{l_info['icon']} **{l_name}** ({max_s} Soru)", expanded=True):
                            if is_detailed:
                                selected_topics = st.multiselect(
                                    f"{l_name} Çıkan Konular:",
                                    lm.LGS_CURRICULUM.get(l_name, []),
                                    key=f"top_sel_{l_name}"
                                )
                                
                                topic_items = []
                                t_dogru_sum = 0
                                t_yanlis_sum = 0
                                t_soru_sum = 0
                                
                                for top in selected_topics:
                                    st.markdown(f"**🔹 {top}**")
                                    t_c1, t_c2, t_c3 = st.columns(3)
                                    s_cnt = t_c1.number_input("Soru", min_value=1, max_value=max_s, value=1, key=f"s_{l_name}_{top}")
                                    d_cnt = t_c2.number_input("Doğru", min_value=0, max_value=s_cnt, value=s_cnt, key=f"d_{l_name}_{top}")
                                    y_cnt = t_c3.number_input("Yanlış", min_value=0, max_value=s_cnt - d_cnt, value=0, key=f"y_{l_name}_{top}")
                                    b_cnt = s_cnt - (d_cnt + y_cnt)
                                    
                                    t_dogru_sum += d_cnt
                                    t_yanlis_sum += y_cnt
                                    t_soru_sum += s_cnt
                                    
                                    topic_items.append({
                                        "konu": top, "soru": s_cnt, "dogru": d_cnt, "yanlis": y_cnt, "bos": b_cnt
                                    })
                                
                                if selected_topics:
                                    def_d = t_dogru_sum
                                    def_y = t_yanlis_sum
                                else:
                                    def_d = max_s
                                    def_y = 0
                                    
                                d_c1, d_c2, d_c3 = st.columns(3)
                                d_val = d_c1.number_input(f"{l_name} Toplam Doğru", min_value=0, max_value=max_s, value=min(max_s, def_d), key=f"tot_d_{l_name}")
                                y_val = d_c2.number_input(f"{l_name} Toplam Yanlış", min_value=0, max_value=max_s - d_val, value=min(max_s - d_val, def_y), key=f"tot_y_{l_name}")
                                b_val = max(0, max_s - (d_val + y_val))
                                d_c3.markdown(f"<div style='margin-top:28px; font-weight:700; color:#880E4F;'>Boş: {b_val} | Net: {lm.calculate_net(d_val, y_val):.2f}</div>", unsafe_allow_html=True)
                                
                                dersler_payload[l_name] = {
                                    "dogru": d_val, "yanlis": y_val, "bos": b_val, "konular": topic_items
                                }
                            else:
                                d_c1, d_c2, d_c3 = st.columns(3)
                                d_val = d_c1.number_input(f"{l_name} Doğru", min_value=0, max_value=max_s, value=max_s, key=f"fast_d_{l_name}")
                                y_val = d_c2.number_input(f"{l_name} Yanlış", min_value=0, max_value=max_s - d_val, value=0, key=f"fast_y_{l_name}")
                                b_val = max(0, max_s - (d_val + y_val))
                                d_c3.markdown(f"<div style='margin-top:28px; font-weight:700; color:#880E4F;'>Boş: {b_val} | Net: {lm.calculate_net(d_val, y_val):.2f}</div>", unsafe_allow_html=True)
                                
                                dersler_payload[l_name] = {
                                    "dogru": d_val, "yanlis": y_val, "bos": b_val, "konular": []
                                }

                # SAYISAL BÖLÜM
                with col_sayisal:
                    st.markdown("### 🔬 Sayısal Bölüm (40 Soru)")
                    sayisal_lessons = ["Matematik", "Fen Bilimleri"]
                    
                    for l_name in sayisal_lessons:
                        l_info = lm.LGS_LESSONS[l_name]
                        max_s = l_info["soru_sayisi"]
                        
                        with st.expander(f"{l_info['icon']} **{l_name}** ({max_s} Soru)", expanded=True):
                            if is_detailed:
                                selected_topics = st.multiselect(
                                    f"{l_name} Çıkan Konular:",
                                    lm.LGS_CURRICULUM.get(l_name, []),
                                    key=f"top_sel_{l_name}"
                                )
                                
                                topic_items = []
                                t_dogru_sum = 0
                                t_yanlis_sum = 0
                                t_soru_sum = 0
                                
                                for top in selected_topics:
                                    st.markdown(f"**🔹 {top}**")
                                    t_c1, t_c2, t_c3 = st.columns(3)
                                    s_cnt = t_c1.number_input("Soru", min_value=1, max_value=max_s, value=1, key=f"s_{l_name}_{top}")
                                    d_cnt = t_c2.number_input("Doğru", min_value=0, max_value=s_cnt, value=s_cnt, key=f"d_{l_name}_{top}")
                                    y_cnt = t_c3.number_input("Yanlış", min_value=0, max_value=s_cnt - d_cnt, value=0, key=f"y_{l_name}_{top}")
                                    b_cnt = s_cnt - (d_cnt + y_cnt)
                                    
                                    t_dogru_sum += d_cnt
                                    t_yanlis_sum += y_cnt
                                    t_soru_sum += s_cnt
                                    
                                    topic_items.append({
                                        "konu": top, "soru": s_cnt, "dogru": d_cnt, "yanlis": y_cnt, "bos": b_cnt
                                    })
                                
                                if selected_topics:
                                    def_d = t_dogru_sum
                                    def_y = t_yanlis_sum
                                else:
                                    def_d = max_s
                                    def_y = 0
                                    
                                d_c1, d_c2, d_c3 = st.columns(3)
                                d_val = d_c1.number_input(f"{l_name} Toplam Doğru", min_value=0, max_value=max_s, value=min(max_s, def_d), key=f"tot_d_{l_name}")
                                y_val = d_c2.number_input(f"{l_name} Toplam Yanlış", min_value=0, max_value=max_s - d_val, value=min(max_s - d_val, def_y), key=f"tot_y_{l_name}")
                                b_val = max(0, max_s - (d_val + y_val))
                                d_c3.markdown(f"<div style='margin-top:28px; font-weight:700; color:#880E4F;'>Boş: {b_val} | Net: {lm.calculate_net(d_val, y_val):.2f}</div>", unsafe_allow_html=True)
                                
                                dersler_payload[l_name] = {
                                    "dogru": d_val, "yanlis": y_val, "bos": b_val, "konular": topic_items
                                }
                            else:
                                d_c1, d_c2, d_c3 = st.columns(3)
                                d_val = d_c1.number_input(f"{l_name} Doğru", min_value=0, max_value=max_s, value=max_s, key=f"fast_d_{l_name}")
                                y_val = d_c2.number_input(f"{l_name} Yanlış", min_value=0, max_value=max_s - d_val, value=0, key=f"fast_y_{l_name}")
                                b_val = max(0, max_s - (d_val + y_val))
                                d_c3.markdown(f"<div style='margin-top:28px; font-weight:700; color:#880E4F;'>Boş: {b_val} | Net: {lm.calculate_net(d_val, y_val):.2f}</div>", unsafe_allow_html=True)
                                
                                dersler_payload[l_name] = {
                                    "dogru": d_val, "yanlis": y_val, "bos": b_val, "konular": []
                                }

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Anlık Önizleme
                calc_sozel_net = sum(lm.calculate_net(dersler_payload[l]["dogru"], dersler_payload[l]["yanlis"]) for l in sozel_lessons)
                calc_sayisal_net = sum(lm.calculate_net(dersler_payload[l]["dogru"], dersler_payload[l]["yanlis"]) for l in sayisal_lessons)
                calc_toplam_net = round(calc_sozel_net + calc_sayisal_net, 2)
                
                net_dict = {l: lm.calculate_net(dersler_payload[l]["dogru"], dersler_payload[l]["yanlis"]) for l in lm.LGS_LESSONS.keys()}
                calc_puan = lm.calculate_lgs_score(net_dict)
                
                st.markdown(f"""
                <div style='background: #FFF0F5; border: 2px solid #F48FB1; border-radius: 14px; padding: 14px 20px; text-align: center; margin-bottom: 15px;'>
                    <span style='font-size: 1.15rem; font-weight: 800; color: #880E4F;'>
                        🎯 Hesaplanan Toplam Net: <span style='color:#D81B60;'>{calc_toplam_net:.2f} / 90</span> &nbsp;|&nbsp; 
                        Sözel: {calc_sozel_net:.2f} &nbsp;|&nbsp; Sayısal: {calc_sayisal_net:.2f} &nbsp;|&nbsp; 
                        Tahmini LGS Puanı: <span style='color:#8E24AA;'>{calc_puan:.1f} Puan</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("💾 LGS Deneme Sınavını Kaydet", type="primary", use_container_width=True):
                    final_name = exam_name.strip() if exam_name.strip() else f"LGS Deneme ({exam_date})"
                    new_exam = lm.create_exam_record(
                        ogrenci=exam_student,
                        deneme_adi=final_name,
                        yayin=exam_publisher,
                        tarih=exam_date,
                        sure_dk=exam_duration,
                        zorluk=exam_difficulty,
                        notlar=exam_notes,
                        dersler_data=dersler_payload
                    )
                    lm.add_exam(new_exam, api_url=webapp_url)
                    st.balloons()
                    st.success(f"🎉 '{final_name}' deneme sınavı başarıyla kaydedildi!")
                    time.sleep(1.5)
                    st.rerun()

        # --- SUB-TAB 5: TÜM DENEMELER ---
        with lgs_sub5:
            st.subheader("📋 Tüm LGS Denemeleri")
            if not exams:
                st.info("ℹ️ Kayıtlı deneme bulunmuyor.")
            else:
                for idx, ex in enumerate(exams):
                    with st.container(border=True):
                        c_card1, c_card2 = st.columns([3, 1])
                        with c_card1:
                            st.markdown(f"**🏆 {ex.get('deneme_adi')}** ({ex.get('yayin')}) &nbsp;|&nbsp; 📅 {ex.get('tarih')} &nbsp;|&nbsp; ⏱️ {ex.get('sure_dk')} dk &nbsp;|&nbsp; 🎯 Zorluk: {ex.get('zorluk')}")
                            st.markdown(f"**Toplam Net:** `{ex.get('toplam_net', 0):.2f}` &nbsp;|&nbsp; **Tahmini Puan:** `{ex.get('tahmini_puan', 0):.1f}` &nbsp;|&nbsp; **D/Y/B:** `{ex.get('toplam_dogru', 0)}D / {ex.get('toplam_yanlis', 0)}Y / {ex.get('toplam_bos', 0)}B`")
                        with c_card2:
                            if is_admin:
                                if st.button("🗑️ Sil", key=f"del_ex_{ex.get('id')}", use_container_width=True):
                                    lm.delete_exam(ex.get('id'), api_url=webapp_url)
                                    st.success("Deneme silindi.")
                                    time.sleep(1)
                                    st.rerun()
                                    
                        with st.expander("🔍 Ders ve Konu Detaylarını Görüntüle"):
                            d_rows = []
                            for l_name, l_info in lm.LGS_LESSONS.items():
                                ld = ex.get("dersler", {}).get(l_name, {})
                                d_rows.append({
                                    "Ders": f"{l_info['icon']} {l_name}",
                                    "Doğru": ld.get("dogru", 0),
                                    "Yanlış": ld.get("yanlis", 0),
                                    "Boş": ld.get("bos", 0),
                                    "Net": f"{ld.get('net', 0):.2f}",
                                    "Başarı %": f"%{ld.get('basari_yuzdesi', 0):.1f}"
                                })
                            st.dataframe(pd.DataFrame(d_rows), use_container_width=True, hide_index=True)
                            
                            all_topics_in_ex = []
                            for l_name, ld in ex.get("dersler", {}).items():
                                for top in ld.get("konular", []):
                                    all_topics_in_ex.append({
                                        "Ders": l_name,
                                        "Konu": top.get("konu"),
                                        "Soru": top.get("soru"),
                                        "Doğru": top.get("dogru"),
                                        "Yanlış": top.get("yanlis"),
                                        "Boş": top.get("bos")
                                    })
                            if all_topics_in_ex:
                                st.markdown("##### 📝 Konu / Madde Analizi:")
                                st.dataframe(pd.DataFrame(all_topics_in_ex), use_container_width=True, hide_index=True)

    if user in parents:
        # --- ADMIN GÖRÜNÜMÜ ---
        tab1, tab_lgs, tab2 = st.tabs(["⚙️ Görev Yönetimi", "🎯 LGS Deneme Takibi", "➕ Yeni Ekle"])
        
        with tab1:
            student_title = active_student_filter if active_student_filter else "Tüm Öğrenciler"
            # Ribbon style title for Admin
            st.markdown(f"<div class='ribbon-title'>{student_title} - {format_date_tr(dashboard_date)}</div>", unsafe_allow_html=True)

            table_data = filtered_df[filtered_df["Tarih"] == dashboard_date]
            show_task_table(table_data, is_admin=True)

        with tab_lgs:
            render_lgs_tab(user, is_admin=True, active_student_filter=active_student_filter)

        with tab2:
            admin_add_task_fragment(dashboard_date, active_student_filter)

    else:
        # --- ÖĞRENCİ GÖRÜNÜMÜ ---
        tab1, tab2, tab_lgs, tab3, tab4, tab5 = st.tabs(["📝 Görevlerim", "📚 Kitaplığım", "🎯 LGS Denemeleri", "➕ Serbest Çalışma", "⏳ Süreli Soru", "📈 İstatistiklerim"])
        
        with tab1:
            # Ribbon style title for Student
            st.markdown(f"<div class='ribbon-title'>{format_date_tr(dashboard_date)}</div>", unsafe_allow_html=True)

            my_tasks = df[(df["Kullanıcı"] == user) & (df["Tarih"] == dashboard_date)].copy()
            status_map = {"Çalışılıyor": 0, "Beklemede": 0, "Planlandı": 1, "Tamamlandı": 2}
            my_tasks["sort"] = my_tasks["Durum"].map(status_map).fillna(1)
            my_tasks = my_tasks.sort_values("sort")

            show_task_table(my_tasks, is_admin=False)
        
        with tab2:
            st.subheader("📚 Kitaplığım")
            
            # --- LIBRARY LOGIC ---
            all_reading = df[(df["Kullanıcı"] == user) & (df["Ders"] == "Kitap Okuma")]
            
            # Find unique books and their status
            # We group by 'Konu' (Book Name) and see the last entry
            if not all_reading.empty:
                # Sort by Index to get latest first
                all_reading_sorted = all_reading.sort_values("rowIndex", ascending=False)
                unique_books = all_reading_sorted["Konu"].unique()
                
                active_books = []
                finished_books = []
                
                for book in unique_books:
                    book_entries = all_reading_sorted[all_reading_sorted["Konu"] == book]
                    last_status = book_entries.iloc[0]["Durum"]
                    total_time_read = book_entries[book_entries["Durum"] != "Kitap Bitti"]["Sure"].sum()
                    
                    book_data = {"name": book, "time": total_time_read}
                    
                    if last_status == "Kitap Bitti":
                        finished_books.append(book_data)
                    else:
                        active_books.append(book_data)
                        
                # --- ACTIVE BOOKS SECTION ---
                st.markdown("### 📖 Okumaya Devam Et")
                if active_books:
                    for ab in active_books:
                        with st.container(border=True):
                            c_b_1, c_b_2, c_b_3 = st.columns([1, 3, 2])
                            with c_b_1:
                                st.markdown("<div style='font-size: 2.5rem; text-align:center;'>📘</div>", unsafe_allow_html=True)
                            with c_b_2:
                                st.markdown(f"**{ab['name']}**")
                                st.caption(f"Toplam Okunan: **{format_text_duration(ab['time'])}**")
                            with c_b_3:
                                b_start, b_finish = st.columns(2)
                                if b_start.button("Oku", key=f"read_{ab['name']}", type="primary", use_container_width=True):
                                     st.session_state.timer_active = True
                                     st.session_state.timer_running = False # Wait for user to start in focus screen
                                     st.session_state.timer_start_time = None
                                     st.session_state.timer_accumulated = 0
                                     # Special Flag for Reading Session
                                     st.session_state.current_task_info = {
                                         "ders": "Kitap Okuma", 
                                         "konu": ab['name'], 
                                         "is_reading_session": True
                                     }
                                     st.rerun()
                                     
                                if b_finish.button("Bitir", key=f"fin_{ab['name']}", use_container_width=True):
                                    # Log "Kitap Bitti" status
                                    # We use 'add_task' but with status 'Kitap Bitti' and time 0
                                    url = st.secrets["connections"]["webapp_url"]
                                    payload = {"action": "add", "tarih": str(today), "kullanici": user, "ders": "Kitap Okuma", "konu": ab['name'], "durum": "Kitap Bitti", "notlar": "Tebrikler!", "sure": 0}
                                    try: requests.post(url, json=payload)
                                    except: pass
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                else:
                    st.info("Şu an okuduğun bir kitap yok. Aşağıdan yeni bir kitap ekle!")
                
                st.divider()
                
                # --- FINISHED BOOKS SECTION ---
                if finished_books:
                    with st.expander(f"🏆 Biten Kitaplar ({len(finished_books)})"):
                        for fb in finished_books:
                            st.write(f"✅ **{fb['name']}** - {format_text_duration(fb['time'])} okundu.")

            # --- ADD NEW BOOK ---
            with st.form("add_book_form"):
                st.markdown("#### ➕ Yeni Kitap Ekle")
                new_book_name = st.text_input("Kitap Adı")
                if st.form_submit_button("Başla", use_container_width=True, type="primary"):
                    if new_book_name:
                         st.session_state.timer_active = True
                         st.session_state.timer_running = False
                         st.session_state.timer_start_time = None
                         st.session_state.timer_accumulated = 0
                         st.session_state.current_task_info = {
                             "ders": "Kitap Okuma", 
                             "konu": new_book_name, 
                             "is_reading_session": True
                         }
                         st.rerun()
                    else:
                        st.warning("Lütfen bir kitap adı giriniz.")

        with tab_lgs:
            render_lgs_tab(user, is_admin=False)

        with tab3:
            st.subheader("➕ Serbest Çalışma")
            st.markdown("Canın ekstra çalışmak mı istiyor? Harikasın! 👇")
            student_free_study_fragment(today, user)

        with tab4:
            st.subheader("⏳ Süreli Soru Çözümü")
            st.markdown("Hedef bir süre belirle ve geri sayım ile teste başla! 🎯")
            student_countdown_fragment()

        with tab5:
            st.subheader("🎯 Hedefim")
            user_settings = load_settings()
            my_settings = user_settings.get(user, {"type": "Haftalık", "target": 500})
            
            with st.container(border=True):
                with st.form("goal_form"):
                    g_type = st.radio("Hedef Türü", ["Haftalık", "Aylık"], index=0 if my_settings["type"] == "Haftalık" else 1, horizontal=True)
                    g_target = st.number_input("Soru Sayısı Hedefi", min_value=10, max_value=10000, value=my_settings["target"], step=50)
                    if st.form_submit_button("💾 Hedefi Kaydet", type="primary", use_container_width=True):
                        user_settings[user] = {"type": g_type, "target": g_target}
                        save_settings(user_settings)
                        st.success("Hedefin başarıyla kaydedildi! 🎯")
                        time.sleep(1)
                        st.rerun()
            
            if my_settings["type"] == "Haftalık":
                start_date = today - timedelta(days=today.weekday())
                end_date = start_date + timedelta(days=6)
                goal_data = df[(df["Kullanıcı"] == user) & (df["Ders"] != "Kitap Okuma") & (pd.to_datetime(df["Tarih"]).dt.date >= start_date) & (pd.to_datetime(df["Tarih"]).dt.date <= end_date)]
            else:
                goal_data = df[(df["Kullanıcı"] == user) & (df["Ders"] != "Kitap Okuma") & (pd.to_datetime(df["Tarih"]).dt.month == today.month) & (pd.to_datetime(df["Tarih"]).dt.year == today.year)]
            
            current_total = (goal_data["Dogru"].sum() + goal_data["Yanlis"].sum() + goal_data["Bos"].sum()) if not goal_data.empty else 0
            target = my_settings["target"]
            progress_ratio = min(current_total / target, 1.0) if target > 0 else 0
            
            st.markdown(f"**{my_settings['type']} Hedef Durumu:** {current_total} / {target} Soru")
            st.progress(progress_ratio)
            if current_total >= target:
                 st.success("🎉 Hedefine ulaştın! Harikasın!")
            else:
                 st.info(f"Hedefine ulaşmak için {target - current_total} soru kaldı. Yapabilirsin! 💪")

            st.write("---")
            st.subheader("📚 Okuma İstatistikleri")
            reading_df = df[(df["Kullanıcı"] == user) & (df["Ders"] == "Kitap Okuma")]
            
            if not reading_df.empty:
                col_stat1, col_stat2 = st.columns(2)
                
                # Total Reading Time
                total_reading_seconds = reading_df["Sure"].sum()
                col_stat1.metric("Toplam Okuma Süresi", format_text_duration(total_reading_seconds))
                
                # Books Finished
                books_finished = len(reading_df[reading_df["Durum"] == "Kitap Bitti"])
                col_stat2.metric("Bitirilen Kitap Sayısı", f"{books_finished} 📘")
                
                st.write("---")
                
            st.subheader(f"📊 {my_settings['type']} Soru Performansı")
            
            import calendar
            if my_settings["type"] == "Haftalık":
                start_date = today - timedelta(days=today.weekday())
                end_date = start_date + timedelta(days=6)
                chart_data = df[(df["Kullanıcı"] == user) & (pd.to_datetime(df["Tarih"]).dt.date >= start_date) & (pd.to_datetime(df["Tarih"]).dt.date <= end_date)].copy()
                idx = pd.date_range(start=start_date, end=end_date).date
            else:
                chart_data = df[(df["Kullanıcı"] == user) & (pd.to_datetime(df["Tarih"]).dt.month == today.month) & (pd.to_datetime(df["Tarih"]).dt.year == today.year)].copy()
                start_date = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_date = today.replace(day=last_day)
                idx = pd.date_range(start=start_date, end=end_date).date
            
            # Filter out Reading tasks for question stats
            chart_data = chart_data[chart_data["Ders"] != "Kitap Okuma"]
            
            # Use Dogru + Yanlis + Bos to chart actual solved questions, since Toplam is the target
            chart_data["Cozulen"] = chart_data["Dogru"] + chart_data["Yanlis"] + chart_data["Bos"]
            daily_sums = chart_data.groupby("Tarih")["Cozulen"].sum()
            
            # Reindex to ensure the chart shows the full week (Mon-Sun) or full month (1st-Last)
            daily_sums = daily_sums.reindex(idx, fill_value=0)
            
            # Format index for better display
            if my_settings["type"] == "Haftalık":
                daily_sums.index = [format_date_tr(d).split(" ")[-1] for d in daily_sums.index] # Just day name
            else:
                daily_sums.index = [f"{d.day} {format_date_tr(d).split(' ')[1]}" for d in daily_sums.index] # Day and Month name
                
            st.bar_chart(daily_sums)
            st.caption(f"Günlük çözdüğün toplam soru sayısı ({my_settings['type']} görünüm)")
            
            st.write("---")
            st.subheader("🏷️ Konulara Göre Dağılım")
            if not chart_data.empty:
                import plotly.express as px
                topic_data = chart_data.groupby(["Ders", "Konu"])["Cozulen"].sum().reset_index()
                topic_data = topic_data[topic_data["Cozulen"] > 0]
                
                if not topic_data.empty:
                    topic_data.rename(columns={"Cozulen": "Çözülen Soru"}, inplace=True)
                    # For topics without a name, label them as 'Belirtilmedi'
                    topic_data["Konu"] = topic_data["Konu"].replace("", "Belirtilmedi")
                    
                    fig_topic = px.sunburst(topic_data, path=["Ders", "Konu"], values="Çözülen Soru",
                                            color="Ders", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_topic.update_layout(margin=dict(t=10, l=10, r=10, b=10))
                    st.plotly_chart(fig_topic, use_container_width=True)
                else:
                    st.info("Bu dönemde hiç soru çözümü kaydedilmemiş.")
            else:
                st.info("Bu dönemde veri bulunmuyor.")

if st.session_state["authenticated_user"] is None:
    login_screen()
else:
    main_app()