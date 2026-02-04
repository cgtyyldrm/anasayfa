import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import time
import random
import pytz
import extra_streamlit_components as stx # YENİ EKLENDİ

# --- 1. Sayfa ve Stil Ayarları ---
st.set_page_config(page_title="Study Buddy", page_icon="📚", layout="wide")

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
    <style>
    .main-title { font-size: 2.2rem !important; font-weight: 800; color: #4a4e69; text-align: center; margin-bottom: 5px; font-family: 'Helvetica Neue', sans-serif; }
    .sub-title { font-size: 0.9rem; color: #9a8c98; text-align: center; margin-bottom: 20px; font-style: italic; }
    div[data-testid="column"] { align-items: center; }
    div[data-testid="column"] p { font-size: 15px !important; margin-bottom: 0px !important; }
    .stButton button { font-size: 13px !important; padding: 4px 12px !important; border-radius: 8px !important; height: auto !important; min-height: 0px !important; white-space: nowrap !important; }
    img { border-radius: 50%; transition: transform .2s; max-width: 100%; }
    img:hover { transform: scale(1.1); }
    @media (min-width: 640px) { div[data-testid="column"] { display: flex; justify-content: flex-start; } }
    .timer-font { font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #22223b; }
    div[data-testid="stAlert"] { padding: 0.5rem 0.5rem !important; }
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
if "authenticated_user" not in st.session_state: st.session_state.authenticated_user = None
if "edit_mode_index" not in st.session_state: st.session_state.edit_mode_index = None
if "global_student_selection" not in st.session_state: st.session_state.global_student_selection = "Tümü"

# --- OTURUM KONTROLÜ (COOKIE) ---
# Sayfa yüklendiğinde çerez var mı diye bakıyoruz
cookie_user = cookie_manager.get(cookie="study_buddy_user")

# Eğer çerez varsa ve session boşsa, session'ı doldur (Otomatik Giriş)
if cookie_user and st.session_state.authenticated_user is None:
    st.session_state.authenticated_user = cookie_user

MOTIVATION_QUOTES = [
    "Başarı, her gün tekrarlanan küçük çabaların toplamıdır. 🌱",
    "Gelecek, bugün ne yaptığına bağlıdır. 🚀",
    "Zor yollar genellikle güzel yerlere çıkar. 🏔️",
    "İnanmak, başarmanın yarısıdır. Sen harikasın! ⭐"
]

# --- 4. Giriş Ekranı ---
def login_screen():
    st.markdown('<div class="main-title">📚 Study Buddy</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">"{random.choice(MOTIVATION_QUOTES)}"</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.container(border=True):
            st.subheader("Giriş Yap")
            with st.form("login_form"):
                username = st.text_input("Kullanıcı Adı")
                password = st.text_input("Şifre", type="password")
                
                if st.form_submit_button("🚀 Giriş Yap", use_container_width=True):
                    if "passwords" in st.secrets and username in st.secrets["passwords"] and \
                       password == st.secrets["passwords"][username]:
                        
                        # Session'a kaydet
                        st.session_state["authenticated_user"] = username
                        
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

def update_task_progress(index, status, sure_saniye, dogru, yanlis):
    url = st.secrets["connections"]["webapp_url"]
    toplam = dogru + yanlis
    payload = {
        "action": "complete", "rowIndex": index, "durum": status, 
        "sure": sure_saniye, "dogru": dogru, "yanlis": yanlis, "toplam": toplam
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

# --- 7. ANA UYGULAMA ---
def main_app():
    user = st.session_state["authenticated_user"]
    parents = ["Baba", "Anne"]
    
    with st.sidebar:
        st.title(f"Profil: {user}")
        
        current_berru_img = st.session_state.get("img_berru", "https://cdn-icons-png.flaticon.com/512/4322/4322991.png")
        current_ela_img = st.session_state.get("img_ela", "https://cdn-icons-png.flaticon.com/512/4322/4322992.png")
        
        if user == "Berru": st.image(current_berru_img, width=80)
        elif user == "Ela": st.image(current_ela_img, width=80)
        elif user == "Anne": st.image("https://cdn-icons-png.flaticon.com/512/2942/2942802.png", width=80)
        else: st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
            
        st.write("---")
        
        if user in parents:
            with st.expander("📸 Profil Fotoğrafı Linki"):
                url_berru = st.text_input("Berru Link", key="url_berru_in")
                if url_berru: st.session_state["img_berru"] = url_berru
                url_ela = st.text_input("Ela Link", key="url_ela_in")
                if url_ela: st.session_state["img_ela"] = url_ela

        st.write("---")
        
        # --- GÜNCELLENMİŞ ÇIKIŞ YAP BUTONU ---
        if st.button("Çıkış Yap", use_container_width=True):
            # 1. Session state'i temizle
            st.session_state["authenticated_user"] = None
            # 2. Çerezi sil
            cookie_manager.delete("study_buddy_user")
            # 3. Sayfayı yenile
            st.rerun()

    # --- ODAK EKRANI ---
    if st.session_state.timer_active:
        c_focus_1, c_focus_2, c_focus_3 = st.columns([1, 2, 1])
        with c_focus_2:
            task = st.session_state.current_task_info
            st.markdown(f"<div style='text-align:center; font-size: 2rem; font-weight:bold;'>🎯 {task['ders']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; color:gray;'>{task['konu']}</div>", unsafe_allow_html=True)
            st.divider()

            current_time = time.time()
            elapsed = st.session_state.timer_accumulated + (current_time - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
            
            st.markdown(f"<div style='text-align: center; font-size: 80px; color: #4CAF50;' class='timer-font'>{format_timer_display(elapsed)}</div>", unsafe_allow_html=True)

            c_input1, c_input2 = st.columns(2)
            with c_input1:
                d_input = st.number_input("✅ Doğru Sayısı", min_value=0, step=1, value=st.session_state.temp_dogru)
                st.session_state.temp_dogru = d_input
            with c_input2:
                y_input = st.number_input("❌ Yanlış Sayısı", min_value=0, step=1, value=st.session_state.temp_yanlis)
                st.session_state.temp_yanlis = y_input
            
            st.caption(f"Toplam Çözülen Soru: **{st.session_state.temp_dogru + st.session_state.temp_yanlis}**")

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
                    update_task_progress(task['index'], "Tamamlandı", int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis)
                    st.session_state.timer_active = False
                    st.session_state.timer_running = False
                    st.session_state.timer_accumulated = 0
                    st.session_state.temp_dogru = 0
                    st.session_state.temp_yanlis = 0
                    st.balloons(); time.sleep(1.5); st.rerun()

            st.write("")
            if st.button("💾 Kaydet ve Çık (Bitmedi)", use_container_width=True):
                final_sec = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time) if st.session_state.timer_running else st.session_state.timer_accumulated
                update_task_progress(task['index'], "Beklemede", int(final_sec), st.session_state.temp_dogru, st.session_state.temp_yanlis)
                st.session_state.timer_active = False
                st.session_state.timer_running = False
                st.session_state.timer_accumulated = 0
                st.session_state.temp_dogru = 0
                st.session_state.temp_yanlis = 0
                st.rerun()

        if st.session_state.timer_running: time.sleep(1); st.rerun()
        return

    # --- ANA SAYFA ---
    st.markdown('<div class="main-title">Study Buddy</div>', unsafe_allow_html=True)
    df = get_data()
    today = get_turkey_time()

    active_student_filter = user 
    
    if user in parents:
        img_berru_src = st.session_state.get("img_berru", "https://cdn-icons-png.flaticon.com/512/4322/4322991.png")
        img_ela_src = st.session_state.get("img_ela", "https://cdn-icons-png.flaticon.com/512/4322/4322992.png")
        img_all_src = "https://cdn-icons-png.flaticon.com/512/681/681494.png"

        c_space1, c_sel_all, c_sel_berru, c_sel_ela, c_space2 = st.columns([2, 1, 1, 1, 2])
        
        with c_sel_all:
            st.image(img_all_src, width=60)
            btn_type = "primary" if st.session_state.global_student_selection == "Tümü" else "secondary"
            if st.button("Tümü", key="btn_all", type=btn_type, use_container_width=True):
                st.session_state.global_student_selection = "Tümü"
                st.rerun()

        with c_sel_berru:
            st.image(img_berru_src, width=60)
            btn_type = "primary" if st.session_state.global_student_selection == "Berru" else "secondary"
            if st.button("Berru", key="btn_berru", type=btn_type, use_container_width=True):
                st.session_state.global_student_selection = "Berru"
                st.rerun()
                
        with c_sel_ela:
            st.image(img_ela_src, width=60)
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

        period = st.radio("", ["Günlük", "Haftalık", "Aylık"], horizontal=True, label_visibility="collapsed")
        
        dashboard_data = pd.DataFrame()
        if period == "Günlük":
            dashboard_data = filtered_df[filtered_df["Tarih"] == today]
            metric_label = "Bugün"
        elif period == "Haftalık":
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            dashboard_data = filtered_df[(filtered_df["Tarih"] >= start_week) & (filtered_df["Tarih"] <= end_week)]
            metric_label = "Bu Hafta"
        elif period == "Aylık":
            dashboard_data = filtered_df[pd.to_datetime(filtered_df["Tarih"]).apply(lambda x: x.month == today.month and x.year == today.year)]
            metric_label = "Bu Ay"

        total_time = format_text_duration(dashboard_data["Sure"].sum())
        total_questions = dashboard_data["Toplam"].sum()
        total_correct = dashboard_data["Dogru"].sum()
        total_wrong = dashboard_data["Yanlis"].sum()
        completed_count = len(dashboard_data[dashboard_data["Durum"] == "Tamamlandı"])
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric(f"⏱️ Süre", total_time)
        with c2: st.metric(f"📝 Toplam Soru", total_questions)
        with c3: st.metric(f"✅ Doğru", total_correct)
        with c4: st.metric(f"❌ Yanlış", total_wrong)
        
        if period != "Günlük" and not dashboard_data.empty:
            with st.expander(f"📊 {metric_label} Performans Grafiği", expanded=True):
                st.bar_chart(dashboard_data.groupby("Ders")["Dogru"].sum())

    st.write("---")

    col_ratios = [0.4, 0.8, 1.2, 3.0, 1.2, 0.8, 0.6, 0.6, 0.6, 1.5]
    
    def show_task_table(data, is_admin=False):
        if data.empty:
            st.info("Bu tarihte kayıtlı görev yok.", icon=":material/info:")
            return

        header_cols = st.columns(col_ratios)
        titles = ["#", "Öğrenci", "Ders", "Konu", "Durum", "Süre", "D", "Y", "T", "İşlemler"]
        
        for col, title in zip(header_cols, titles):
            col.markdown(f"**{title}**")
        
        st.markdown("---") 

        for index, row in enumerate(data.itertuples(), start=1):
            if is_admin and st.session_state.edit_mode_index == row.rowIndex:
                with st.container(border=True):
                    st.info(f"Düzenleniyor: {row.Kullanıcı} - {row.Ders}")
                    with st.form(f"edit_form_{index}"):
                        c_edit1, c_edit2, c_edit3 = st.columns(3)
                        ders_list = ["Matematik", "Fen", "Türkçe", "Sosyal", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Diğer"]
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
                    if row.Durum == "Tamamlandı":
                        st.markdown(f"<span style='color:#2e7d32; font-weight:bold;'>Tamamlandı</span>", unsafe_allow_html=True)
                    elif row.Durum == "Planlandı":
                        st.markdown(f"<span style='color:#0288d1; font-weight:bold;'>Planlandı</span>", unsafe_allow_html=True)
                    elif row.Durum == "Beklemede":
                        st.markdown(f"<span style='color:#ed6c02; font-weight:bold;'>Beklemede</span>", unsafe_allow_html=True)
                    elif row.Durum == "Çalışılıyor":
                        st.markdown(f"<span style='color:#ed6c02; font-weight:bold;'>Çalışılıyor</span>", unsafe_allow_html=True)
                    else:
                        st.write(row.Durum)
                
                row_cols[5].write(format_text_duration(row.Sure))
                row_cols[6].write(f"{row.Dogru}")
                row_cols[7].write(f"{row.Yanlis}")
                row_cols[8].write(f"{row.Toplam}")
                
                with row_cols[9]:
                    if is_admin:
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("Düz.", icon=":material/edit:", key=f"btn_edit_{row.rowIndex}", use_container_width=True):
                                st.session_state.edit_mode_index = row.rowIndex
                                st.rerun()
                        with b2:
                            if st.button("Sil", icon=":material/delete:", key=f"btn_del_{row.rowIndex}", type="primary", use_container_width=True):
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
                                st.session_state.current_task_info = {"index": row.rowIndex, "ders": row.Ders, "konu": row.Konu}
                                update_task_progress(row.rowIndex, "Çalışılıyor", row.Sure, row.Dogru, row.Yanlis)
                                st.rerun()
                        else:
                            st.button("Bitti", disabled=True, key=f"d_{index}", use_container_width=True)
                
                st.divider()

    if user in parents:
        # --- ADMIN GÖRÜNÜMÜ ---
        tab1, tab2 = st.tabs(["⚙️ Görev Yönetimi", "➕ Yeni Ekle"])
        
        with tab1:
            c_filter1, c_filter2 = st.columns([1, 4])
            with c_filter1:
                selected_date = st.date_input("Tarih Seçin:", value=today, key="admin_date_picker")
            
            with c_filter2:
                 student_title = active_student_filter if active_student_filter else "Tüm Öğrenciler"
                 st.subheader(f"{student_title} - {selected_date.strftime('%d.%m.%Y')}")

            table_data = filtered_df[filtered_df["Tarih"] == selected_date]
            show_task_table(table_data, is_admin=True)

        with tab2:
            with st.container(border=True):
                with st.form("new_task"):
                    c1, c2 = st.columns(2)
                    tarih_inp = c1.date_input("Tarih", today)
                    
                    default_student_idx = 0
                    student_options = ["Berru", "Ela"]
                    if active_student_filter in student_options:
                        default_student_idx = student_options.index(active_student_filter)
                        
                    kisi_inp = c1.selectbox("Öğrenci", student_options, index=default_student_idx)
                    ders_inp = c2.selectbox("Ders", ["Matematik", "Fen", "Türkçe", "Sosyal", "İngilizce", "Diğer"])
                    konu_inp = c2.text_input("Konu")
                    
                    if st.form_submit_button("Ekle", use_container_width=True):
                        add_task(tarih_inp, kisi_inp, ders_inp, konu_inp)
                        st.success("Eklendi"); time.sleep(1); st.rerun()

    else:
        # --- ÖĞRENCİ GÖRÜNÜMÜ ---
        tab1, tab2 = st.tabs(["📝 Görevlerim", "📈 İstatistiklerim"])
        with tab1:
            c_s_filter1, c_s_filter2 = st.columns([1, 4])
            with c_s_filter1:
                selected_student_date = st.date_input("Tarih Seç:", value=today, key="student_date_picker")
            
            with c_s_filter2:
                st.subheader(f"{selected_student_date.strftime('%d.%m.%Y')} Görevleri")

            my_tasks = df[(df["Kullanıcı"] == user) & (df["Tarih"] == selected_student_date)].copy()
            status_map = {"Çalışılıyor": 0, "Beklemede": 0, "Planlandı": 1, "Tamamlandı": 2}
            my_tasks["sort"] = my_tasks["Durum"].map(status_map).fillna(1)
            my_tasks = my_tasks.sort_values("sort")

            show_task_table(my_tasks, is_admin=False)

        with tab2:
            st.subheader("Aylık Performans")
            monthly_data = df[(df["Kullanıcı"] == user) & (pd.to_datetime(df["Tarih"]).dt.month == today.month)]
            if not monthly_data.empty:
                st.bar_chart(monthly_data.groupby("Tarih")["Toplam"].sum())
                st.caption("Günlük çözdüğün toplam soru sayısı")

if st.session_state["authenticated_user"] is None:
    login_screen()
else:
    main_app()