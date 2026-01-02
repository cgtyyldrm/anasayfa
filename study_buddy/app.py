import streamlit as st
import pandas as pd
from datetime import date, timedelta
import requests
import time
import random

# --- 1. Sayfa ve Stil Ayarları ---
st.set_page_config(page_title="Study Buddy", page_icon="📚", layout="centered")

# CSS: Modern ve Temiz Görünüm
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        color: #4a4e69;
        text-align: center;
        margin-bottom: 5px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-title {
        font-size: 1rem;
        color: #9a8c98;
        text-align: center;
        margin-bottom: 25px;
        font-style: italic;
    }
    .timer-font {
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #22223b;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
    }
    /* Kartların (Container) kenarlarını yumuşat */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Session State ---
if "timer_active" not in st.session_state: st.session_state.timer_active = False  
if "timer_start_time" not in st.session_state: st.session_state.timer_start_time = None 
if "timer_accumulated" not in st.session_state: st.session_state.timer_accumulated = 0 
if "timer_running" not in st.session_state: st.session_state.timer_running = False 
if "current_task_info" not in st.session_state: st.session_state.current_task_info = {} 
if "temp_question_count" not in st.session_state: st.session_state.temp_question_count = 0
if "authenticated_user" not in st.session_state: st.session_state.authenticated_user = None

# --- 3. Motivasyon Sözleri ---
MOTIVATION_QUOTES = [
    "Başarı, her gün tekrarlanan küçük çabaların toplamıdır. 🌱",
    "Gelecek, bugün ne yaptığına bağlıdır. 🚀",
    "Zor yollar genellikle güzel yerlere çıkar. 🏔️",
    "İnanmak, başarmanın yarısıdır. Sen harikasın! ⭐",
    "Bir saatlik çalışma, hayallerine bir adım daha yaklaşmaktır. ⏳",
    "Bugünün çalışması, yarının zaferidir! 🏆",
    "Disiplin, hedeflerle başarı arasındaki köprüdür. 🌉"
]

# --- 4. Giriş Ekranı ---
def login_screen():
    st.markdown('<div class="main-title">📚 Study Buddy</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">"{random.choice(MOTIVATION_QUOTES)}"</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            st.subheader("Giriş Yap")
            with st.form("login_form"):
                username = st.text_input("Kullanıcı Adı")
                password = st.text_input("Şifre", type="password")
                
                if st.form_submit_button("🚀 Giriş Yap", use_container_width=True):
                    if username in st.secrets["passwords"] and \
                       password == st.secrets["passwords"][username]:
                        st.session_state["authenticated_user"] = username
                        st.toast(f"Hoş geldin {username}!", icon="👋")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Hatalı giriş bilgileri.")

# --- 5. Veri İşlemleri ---
def get_data():
    url = st.secrets["connections"]["webapp_url"]
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            expected = ["Tarih", "Kullanıcı", "Ders", "Konu", "Durum", "Notlar", "Sure", "SoruSayisi"]
            for col in expected:
                if col not in df.columns: df[col] = ""
            
            df["Sure"] = pd.to_numeric(df["Sure"], errors='coerce').fillna(0).astype(int)
            df["SoruSayisi"] = pd.to_numeric(df["SoruSayisi"], errors='coerce').fillna(0).astype(int)
            # Tarihi datetime objesine çevir
            df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').dt.date
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def add_task(tarih, kullanıcı, ders, konu, notlar):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "add", "tarih": str(tarih), "kullanici": kullanıcı, "ders": ders, "konu": konu, "durum": "Planlandı", "notlar": notlar, "sure": 0, "soru_sayisi": 0}
    try: requests.post(url, json=payload)
    except: pass

def update_task_progress(index, status, sure_saniye, soru_sayisi=0):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "complete", "rowIndex": index, "durum": status, "sure": sure_saniye, "soru_sayisi": soru_sayisi}
    try: requests.post(url, json=payload)
    except: pass

# --- 6. Yardımcı Fonksiyonlar ---
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

# --- 7. ANA UYGULAMA ---
def main_app():
    user = st.session_state["authenticated_user"]
    
    # YÖNETİCİLER LİSTESİ (Ebeveynler)
    parents = ["Baba", "Anne"]
    
    # Menü (Sidebar)
    with st.sidebar:
        st.title(f"Profil: {user}")
        
        # Profil Resimleri
        if user == "Berru": 
            st.image("https://cdn-icons-png.flaticon.com/512/4322/4322991.png", width=80)
        elif user == "Ela": 
            st.image("https://cdn-icons-png.flaticon.com/512/4322/4322992.png", width=80)
        elif user == "Anne":
            # Anne İkonu
            st.image("https://cdn-icons-png.flaticon.com/512/2942/2942802.png", width=80)
        else: 
            # Baba İkonu
            st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
            
        st.write("---")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state["authenticated_user"] = None
            st.rerun()

    # --- KRONOMETRE MODU ---
    if st.session_state.timer_active:
        task = st.session_state.current_task_info
        st.markdown(f"<div style='text-align:center; font-size: 2rem; font-weight:bold;'>🎯 {task['ders']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; color:gray;'>{task['konu']}</div>", unsafe_allow_html=True)
        st.divider()

        current_time = time.time()
        elapsed = st.session_state.timer_accumulated + (current_time - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated

        st.markdown(f"<div style='text-align: center; font-size: 80px; color: #4CAF50;' class='timer-font'>{format_timer_display(elapsed)}</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.write("")
            soru_input = st.number_input("✏️ Çözülen Soru", min_value=0, step=1, value=st.session_state.temp_question_count)
            st.session_state.temp_question_count = soru_input

        st.write("")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.session_state.timer_running:
                if st.button("⏸️ Mola Ver", use_container_width=True):
                    st.session_state.timer_accumulated += (time.time() - st.session_state.timer_start_time)
                    st.session_state.timer_running = False
                    st.rerun()
            else:
                if st.button("▶️ Devam Et", type="primary", use_container_width=True):
                    st.session_state.timer_start_time = time.time()
                    st.session_state.timer_running = True
                    st.rerun()
        
        with col_btn2:
            if st.button("🏁 Bitir", type="primary", use_container_width=True):
                final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                update_task_progress(task['index'], "Tamamlandı", int(final_sec), st.session_state.temp_question_count)
                st.session_state.timer_active = False
                st.session_state.timer_running = False
                st.session_state.timer_accumulated = 0
                st.session_state.temp_question_count = 0
                st.balloons()
                time.sleep(1.5)
                st.rerun()

        st.write("")
        if st.button("💾 Kaydet ve Çık (Bitmedi)", use_container_width=True):
            final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
            update_task_progress(task['index'], "Beklemede", int(final_sec), st.session_state.temp_question_count)
            st.session_state.timer_active = False
            st.session_state.timer_running = False
            st.session_state.timer_accumulated = 0
            st.session_state.temp_question_count = 0
            st.rerun()

        if st.session_state.timer_running: time.sleep(1); st.rerun()
        return

    # --- DASHBOARD (ÖZET EKRANI) ---
    st.markdown('<div class="main-title">Study Buddy</div>', unsafe_allow_html=True)
    df = get_data()
    today = date.today()

    if not df.empty:
        # Filtreleme: Eğer Ebeveyn ise (Anne/Baba) herkesi görür, Öğrenci kendini
        filter_user = None if user in parents else user
        
        if filter_user:
            user_df = df[df["Kullanıcı"] == filter_user]
        else:
            user_df = df

        # --- PERİYOT SEÇİCİ ---
        period = st.radio("", ["Günlük", "Haftalık", "Aylık"], horizontal=True, label_visibility="collapsed")
        
        # Filtreleme Mantığı
        filtered_df = pd.DataFrame()
        
        if period == "Günlük":
            filtered_df = user_df[user_df["Tarih"] == today]
            metric_label = "Bugün"
        
        elif period == "Haftalık":
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            filtered_df = user_df[(user_df["Tarih"] >= start_week) & (user_df["Tarih"] <= end_week)]
            metric_label = "Bu Hafta"
            
        elif period == "Aylık":
            filtered_df = user_df[pd.to_datetime(user_df["Tarih"]).apply(lambda x: x.month == today.month and x.year == today.year)]
            metric_label = "Bu Ay"

        # Özet Hesaplamaları
        total_time = format_text_duration(filtered_df["Sure"].sum())
        total_questions = filtered_df["SoruSayisi"].sum()
        completed_count = len(filtered_df[filtered_df["Durum"] == "Tamamlandı"])
        
        # Dashboard Kutucukları
        c1, c2, c3 = st.columns(3)
        with c1: st.metric(f"⏱️ Süre ({metric_label})", total_time)
        with c2: st.metric(f"✏️ Soru ({metric_label})", total_questions)
        with c3: st.metric(f"✅ Görev ({metric_label})", f"{completed_count} Adet")
        
        # --- GRAFİK ---
        if period != "Günlük" and not filtered_df.empty:
            with st.expander(f"📊 {metric_label} Performans Grafiği", expanded=True):
                chart_data = filtered_df.groupby("Ders")["SoruSayisi"].sum()
                st.bar_chart(chart_data)

    st.write("---")

    # --- SEKME YAPISI ---
    # Anne veya Baba (Admin) Görünümü
    if user in parents:
        tab1, tab2 = st.tabs(["📋 Bugünün Listesi", "➕ Görev Ekle"])
        with tab1:
            today_data = df[df["Tarih"] == today]
            if not today_data.empty: st.dataframe(today_data, use_container_width=True)
            else: st.info("Bugün için kayıt bulunamadı.")
        with tab2:
            with st.container(border=True):
                with st.form("new_task"):
                    c1, c2 = st.columns(2)
                    tarih_inp = c1.date_input("Tarih", date.today())
                    kisi_inp = c1.selectbox("Öğrenci", ["Berru", "Ela"])
                    ders_inp = c2.selectbox("Ders", ["Matematik", "Fen", "Türkçe", "Sosyal", "İngilizce", "Diğer"])
                    konu_inp = c2.text_input("Konu")
                    notlar_inp = st.text_area("Notlar")
                    if st.form_submit_button("Ekle", use_container_width=True):
                        add_task(tarih_inp, kisi_inp, ders_inp, konu_inp, notlar_inp)
                        st.success("Eklendi"); time.sleep(1); st.rerun()

    # Öğrenci Görünümü
    else:
        tab1, tab2 = st.tabs(["📝 Görevlerim", "📈 İstatistiklerim"])
        with tab1:
            my_tasks = df[(df["Kullanıcı"] == user) & (df["Tarih"] == today)].copy()
            status_map = {"Çalışılıyor": 0, "Beklemede": 0, "Planlandı": 1, "Tamamlandı": 2}
            my_tasks["sort"] = my_tasks["Durum"].map(status_map).fillna(1)
            my_tasks = my_tasks.sort_values("sort")

            if not my_tasks.empty:
                for idx, row in my_tasks.iterrows():
                    with st.container(border=True):
                        c_icon, c_info, c_act = st.columns([1, 4, 2])
                        
                        icon = "✅" if row["Durum"] == "Tamamlandı" else ("⏸️" if row["Durum"] == "Beklemede" else "📌")
                        c_icon.markdown(f"<div style='font-size:28px; text-align:center;'>{icon}</div>", unsafe_allow_html=True)
                        
                        with c_info:
                            st.markdown(f"**{row['Ders']}**")
                            st.write(f"{row['Konu']}")
                            inf = []
                            if row["Sure"] > 0: inf.append(f"⏱️ {format_text_duration(row['Sure'])}")
                            if row["SoruSayisi"] > 0: inf.append(f"✏️ {row['SoruSayisi']}")
                            if inf: st.caption(" | ".join(inf))
                        
                        with c_act:
                            if row["Durum"] != "Tamamlandı":
                                btn_txt = "DEVAM ET" if row["Sure"] > 0 else "BAŞLA"
                                btn_style = "primary" if row["Sure"] > 0 else "secondary"
                                if st.button(btn_txt, key=f"b_{idx}", type=btn_style, use_container_width=True):
                                    st.session_state.timer_active = True
                                    st.session_state.timer_running = True
                                    st.session_state.timer_start_time = time.time()
                                    st.session_state.timer_accumulated = row["Sure"]
                                    st.session_state.temp_question_count = int(row["SoruSayisi"])
                                    st.session_state.current_task_info = {"index": idx, "ders": row["Ders"], "konu": row["Konu"]}
                                    update_task_progress(idx, "Çalışılıyor", row["Sure"], row["SoruSayisi"])
                                    st.rerun()
                            else:
                                st.button("Tamamlandı", disabled=True, key=f"d_{idx}", use_container_width=True)
            else:
                st.info("Bugün boşsun! 🥳")

        with tab2:
            st.subheader("Aylık Başarı Tablosu")
            monthly_data = df[(df["Kullanıcı"] == user) & (pd.to_datetime(df["Tarih"]).dt.month == today.month)]
            if not monthly_data.empty:
                chart_data = monthly_data.groupby("Tarih")["SoruSayisi"].sum()
                st.line_chart(chart_data)
                st.caption("Günlük çözdüğün soru sayısı grafiği")

if st.session_state["authenticated_user"] is None:
    login_screen()
else:
    main_app()