import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import time
import random
import pytz
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
LOGO_URL = "https://raw.githubusercontent.com/cgtyyldrm/anasayfa/main/assets/logo.PNG" 
# --- 1. Sayfa ve Stil Ayarları ---
st.set_page_config(page_title="Study Buddy", page_icon="LOGO_URL", layout="wide")
# --- 1. Sayfa ve Stil Ayarları ---

# --- IOS ANA EKRAN LOGOSU İÇİN ÖZEL KOD ---
st.markdown(
    f"""
    <style>
    </style>
    <link rel="apple-touch-icon" sizes="180x180" href="{LOGO_URL}">
    <link rel="icon" type="image/png" href="{LOGO_URL}">
    <link rel="shortcut icon" type="image/png" href="{LOGO_URL}">
    <meta name="apple-mobile-web-app-title" content="Study Buddy">
    <meta name="application-name" content="Study Buddy">
    """,
    unsafe_allow_html=True
)
# -------------------------------------------


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

# --- 5. Veri İşlemleri (API) ---
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

            expected = ["Tarih", "Kullanıcı", "Ders", "Konu", "Durum", "Notlar", "Sure", "Dogru", "Yanlis", "Toplam", "rowIndex"]
            for col in expected:
                if col not in df.columns: df[col] = ""
            
            for col in ["Sure", "Dogru", "Yanlis", "Toplam", "rowIndex"]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            # Boş sayısını hesapla (Toplam - (Doğru + Yanlış))
            df["Bos"] = df["Toplam"] - (df["Dogru"] + df["Yanlis"])
            # Negatif koruma (olur da manuel veri girilirse)
            df["Bos"] = df["Bos"].apply(lambda x: x if x >= 0 else 0)

            df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').dt.date
            return df
        return pd.DataFrame()
    except Exception as e: 
        print(f"Hata: {e}")
        return pd.DataFrame()

def add_task(tarih, kullanıcı, ders, konu):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "add", "tarih": str(tarih), "kullanici": kullanıcı, "ders": ders, "konu": konu, "durum": "Planlandı", "notlar": ""}
    try: requests.post(url, json=payload)
    except: pass

def delete_task(row_index):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "delete", "rowIndex": row_index}
    try: requests.post(url, json=payload)
    except: pass

def edit_task(row_index, tarih, ders, konu):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "edit", "rowIndex": row_index, "tarih": str(tarih), "ders": ders, "konu": konu}
    try: requests.post(url, json=payload)
    except: pass

def update_task_progress(index, status, sure_saniye, dogru, yanlis, bos=0):
    url = st.secrets["connections"]["webapp_url"]
    toplam = dogru + yanlis + bos
    payload = {
        "action": "complete", "rowIndex": index, "durum": status, 
        "sure": sure_saniye, "dogru": dogru, "yanlis": yanlis, "bos": bos, "toplam": toplam
    }
    try: requests.post(url, json=payload)
    except: pass

def log_task(tarih, kullanıcı, ders, konu, sure_saniye):
    url = st.secrets["connections"]["webapp_url"]
    # Log directly as "Tamamlandı" with duration
    payload = {
        "action": "add", 
        "tarih": str(tarih), 
        "kullanici": kullanıcı, 
        "ders": ders, 
        "konu": konu, 
        "durum": "Tamamlandı", 
        "notlar": "Okuma Seansı",
        "sure": sure_saniye,
        "dogru": 0, "yanlis": 0, "bos": 0, "toplam": 0
    }
    try: requests.post(url, json=payload)
    except: pass

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
            
            # --- READING MODE SPECIFIC LOGIC ---
            if is_reading_mode:
                # Initialize Reading Duration Selection if not set
                if "reading_duration" not in st.session_state:
                    st.session_state.reading_duration = 15 # Default
                
                if not st.session_state.timer_running and st.session_state.timer_accumulated == 0:
                     st.info("Ne kadar kitap okuyacaksın?")
                     dur = st.slider("Süre (Dakika)", 10, 60, 15, step=5)
                     st.session_state.reading_duration = dur
                     # We use 'timer_accumulated' to store duration in seconds effectively or just logic below
                
                # Logic: Timer counts DOWN from Target
                # elapsed is how much time passed since start
                elapsed_since_start = (current_time - st.session_state.timer_start_time) if st.session_state.timer_running else 0
                total_elapsed = st.session_state.timer_accumulated + elapsed_since_start
                
                # But for reading, we want countdown. 
                # Let's say target is X mins. Remaining = X*60 - total_elapsed
                target_seconds = st.session_state.get("reading_duration", 15) * 60
                remaining = max(0, target_seconds - total_elapsed)
                
                # Check Completion
                if remaining == 0 and st.session_state.timer_running:
                     st.session_state.timer_running = False
                     st.session_state.timer_accumulated = total_elapsed
                     # AUDIO ALERT
                     st.markdown("""
                        <audio autoplay>
                        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                        </audio>
                        """, unsafe_allow_html=True)
                     st.success("Süre Doldu! 📚 Harika bir okuma saatiydi!")
                     st.balloons()
                
                st.markdown(f"<div style='text-align: center; font-size: 80px; color: #D81B60;' class='timer-font'>{format_timer_display(remaining)}</div>", unsafe_allow_html=True)
                
                # Reading Mode doesn't use Dogru/Yanlis usually, just Time.
                # Assuming simple completion.
                
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
                    if remaining == 0 and is_reading_mode and st.session_state.timer_accumulated > 0:
                         pass # Completed, don't show Resume
                    else:
                        if st.button(btn_text, type="primary", use_container_width=True):
                            st.session_state.timer_start_time = time.time()
                            st.session_state.timer_running = True
                            st.rerun()
            
            with col_btn2:
                # Finish Logic
                finish_label = "🏁 Bitir"
                if is_reading_mode: finish_label = "✅ Okumayı Bitir"
                
                if st.button(finish_label, type="primary", use_container_width=True):
                    final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                    
                    if task.get("is_reading_session", False):
                         # Direct Log for Library Session
                         log_task(today, user, task['ders'], task['konu'], int(final_sec))
                    else:
                        # Update Task Progress for Normal Tasks
                        update_task_progress(task['index'], "Tamamlandı", int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis, st.session_state.temp_bos)
                    
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
            if not is_reading_mode and st.button("💾 Kaydet ve Çık (Bitmedi)", use_container_width=True):
                final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                update_task_progress(task['index'], "Beklemede", int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis, st.session_state.temp_bos)
                st.session_state.timer_active = False
                st.session_state.timer_running = False
                st.session_state.timer_accumulated = 0
                st.session_state.temp_dogru = 0
                st.session_state.temp_yanlis = 0
                st.session_state.temp_bos = 0
                st.rerun()
            elif is_reading_mode and st.button("🔙 İptal / Çık", use_container_width=True):
                 st.session_state.timer_active = False
                 st.session_state.timer_running = False
                 if "reading_duration" in st.session_state: del st.session_state.reading_duration
                 st.rerun()

        if st.session_state.timer_running: time.sleep(1); st.rerun()
        return

    # --- ANA SAYFA ---
    st.markdown('<div class="main-title">Study Buddy</div>', unsafe_allow_html=True)
    df = get_data()

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
            dashboard_data = filtered_df[pd.to_datetime(filtered_df["Tarih"]).apply(lambda x: x.month == dashboard_date.month and x.year == dashboard_date.year)]
            metric_label = "Seçilen Ay"

        total_time = format_text_duration(dashboard_data["Sure"].sum())
        total_questions = dashboard_data["Toplam"].sum()
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

    if user in parents:
        # --- ADMIN GÖRÜNÜMÜ ---
        tab1, tab2 = st.tabs(["⚙️ Görev Yönetimi", "➕ Yeni Ekle"])
        
        with tab1:
            student_title = active_student_filter if active_student_filter else "Tüm Öğrenciler"
            # Ribbon style title for Admin
            st.markdown(f"<div class='ribbon-title'>{student_title} - {format_date_tr(dashboard_date)}</div>", unsafe_allow_html=True)

            table_data = filtered_df[filtered_df["Tarih"] == dashboard_date]
            show_task_table(table_data, is_admin=True)

        with tab2:
            with st.container(border=True):
                with st.form("new_task"):
                    c1, c2 = st.columns(2)
                    tarih_inp = c1.date_input("Tarih", dashboard_date)
                    
                    default_student_idx = 0
                    student_options = ["Berru", "Ela"]
                    if active_student_filter in student_options:
                        default_student_idx = student_options.index(active_student_filter)
                        
                    kisi_inp = c1.selectbox("Öğrenci", student_options, index=default_student_idx)
                    ders_inp = c2.selectbox("Ders", ["Matematik", "Fen", "Türkçe", "Sosyal", "Hayat Bilgisi", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Kitap Okuma", "Diğer"])
                    konu_inp = c2.text_input("Konu")
                    
                    if st.form_submit_button("Ekle", use_container_width=True):
                        add_task(tarih_inp, kisi_inp, ders_inp, konu_inp)
                        st.success("Eklendi"); time.sleep(1); st.rerun()

    else:
        # --- ÖĞRENCİ GÖRÜNÜMÜ ---
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Görevlerim", "📚 Kitaplığım", "➕ Serbest Çalışma", "📈 İstatistiklerim"])
        
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

        with tab3:
            st.subheader("➕ Serbest Çalışma")
            st.markdown("Canın ekstra çalışmak mı istiyor? Harikasın! 👇")
            
            with st.container(border=True):
                with st.form("free_study_form"):
                    
                    fs_ders = st.selectbox("Hangi Derse Çalışacaksın?", 
                                           ["Matematik", "Fen", "Türkçe", "Sosyal", "Hayat Bilgisi", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Diğer"])
                    fs_konu = st.text_input("Konu (İsteğe Bağlı)", placeholder="Örn: Kesirler Test Çözümü")
                    
                    if not fs_konu:
                        fs_konu = "Serbest Çalışma"
                    
                    submitted = st.form_submit_button("🚀 Listeme Ekle ve Başla", type="primary", use_container_width=True)
                    
                    if submitted:
                        # Bugünün tarihine ekle
                        add_task(today, user, fs_ders, fs_konu)
                        st.balloons()
                        st.success("Harikasın! Görev listene eklendi. 'Görevlerim' sekmesinden BAŞLA diyebilirsin. 🏃‍♀️")
                        time.sleep(2)
                        st.rerun()

        with tab4:
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
                
            st.subheader("📊 Aylık Soru Performansı")
            monthly_data = df[(df["Kullanıcı"] == user) & (pd.to_datetime(df["Tarih"]).dt.month == today.month)]
            # Filter out Reading tasks for question stats
            monthly_data = monthly_data[monthly_data["Ders"] != "Kitap Okuma"]
            
            if not monthly_data.empty:
                st.bar_chart(monthly_data.groupby("Tarih")["Toplam"].sum())
                st.caption("Günlük çözdüğün toplam soru sayısı")

if st.session_state["authenticated_user"] is None:
    login_screen()
else:
    main_app()