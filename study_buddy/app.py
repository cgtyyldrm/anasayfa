import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import time
import random
import pytz # Saat dilimi için gerekli

# --- 1. Sayfa ve Stil Ayarları ---
st.set_page_config(page_title="Study Buddy", page_icon="📚", layout="wide")

# --- Türkiye Saati Ayarı (Deploy Sorunu Çözümü) ---
def get_turkey_time():
    tz = pytz.timezone('Turkey')
    return datetime.now(tz).date()

# CSS: DAHA GÜVENLİ VE RESPONSIVE (Mobil/Deploy Uyumlu)
st.markdown("""
    <style>
    /* Başlıklar */
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 800;
        color: #4a4e69;
        text-align: center;
        margin-bottom: 5px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-title {
        font-size: 0.9rem;
        color: #9a8c98;
        text-align: center;
        margin-bottom: 20px;
        font-style: italic;
    }
    
    /* --- TABLO DÜZENLEMELERİ --- */
    /* Sadece tablo satırlarını hedeflemek zor olduğu için genel ayarları yumuşattık */
    div[data-testid="column"] {
        align-items: center; /* Dikey ortalama */
    }

    /* Yazı Boyutları - Çok küçük olmasın */
    div[data-testid="column"] p {
        font-size: 15px !important; 
        margin-bottom: 0px !important;
    }

    /* Butonları Güzelleştirme */
    .stButton button {
        font-size: 13px !important;
        padding: 4px 12px !important;
        border-radius: 8px !important;
        height: auto !important;
        min-height: 0px !important;
        white-space: nowrap !important; /* Yazı kaymasın */
    }

    /* Avatar Resimleri */
    img {
        border-radius: 50%;
        transition: transform .2s;
        max-width: 100%; 
    }
    img:hover {
        transform: scale(1.1);
    }

    /* Mobilde sütunların çökmesini engellemek için minimum genişlik ayarı (Opsiyonel) */
    @media (min-width: 640px) {
        div[data-testid="column"] {
            display: flex;
            justify-content: flex-start;
        }
    }
    
    .timer-font {
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #22223b;
    }
    
    /* Başarı/Bilgi mesajlarını sıkılaştır */
    div[data-testid="stAlert"] {
        padding: 0.5rem 0.5rem !important;
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
if "edit_mode_index" not in st.session_state: st.session_state.edit_mode_index = None
if "global_student_selection" not in st.session_state: st.session_state.global_student_selection = "Tümü"

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
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.container(border=True):
            st.subheader("Giriş Yap")
            with st.form("login_form"):
                username = st.text_input("Kullanıcı Adı")
                password = st.text_input("Şifre", type="password")
                
                if st.form_submit_button("🚀 Giriş Yap", use_container_width=True):
                    # secrets kontrolü - Hata almamak için
                    if "passwords" in st.secrets and username in st.secrets["passwords"] and \
                       password == st.secrets["passwords"][username]:
                        st.session_state["authenticated_user"] = username
                        st.toast(f"Hoş geldin {username}!", icon="👋")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Hatalı giriş bilgileri veya Secrets ayarlanmamış.")

# --- 5. Veri İşlemleri (API) ---
# Deploy hatasını önlemek için önbellek (Cache) ekleyebiliriz ama anlık veri için şimdilik kaldırıyoruz.
def get_data():
    if "connections" not in st.secrets:
        st.error("Secrets ayarları bulunamadı! Lütfen Streamlit Cloud paneline secrets ekleyin.")
        return pd.DataFrame()

    url = st.secrets["connections"]["webapp_url"]
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            expected = ["Tarih", "Kullanıcı", "Ders", "Konu", "Durum", "Notlar", "Sure", "SoruSayisi", "rowIndex"]
            for col in expected:
                if col not in df.columns: df[col] = ""
            
            df["Sure"] = pd.to_numeric(df["Sure"], errors='coerce').fillna(0).astype(int)
            df["SoruSayisi"] = pd.to_numeric(df["SoruSayisi"], errors='coerce').fillna(0).astype(int)
            df["rowIndex"] = pd.to_numeric(df["rowIndex"], errors='coerce').fillna(-1).astype(int)
            df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').dt.date
            return df
        return pd.DataFrame()
    except Exception as e: 
        # Hata ayıklama için (Deploy'da loglarda görünür)
        print(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

def add_task(tarih, kullanıcı, ders, konu):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "add", "tarih": str(tarih), "kullanici": kullanıcı, "ders": ders, "konu": konu, "durum": "Planlandı", "notlar": "", "sure": 0, "soru_sayisi": 0}
    try: requests.post(url, json=payload)
    except: pass

def delete_task(row_index):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "delete", "rowIndex": row_index}
    try: requests.post(url, json=payload)
    except: pass

def edit_task(row_index, ders, konu):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "edit", "rowIndex": row_index, "ders": ders, "konu": konu, "notlar": ""}
    try: requests.post(url, json=payload)
    except: pass

def update_task_progress(index, status, sure_saniye, soru_sayisi=0):
    url = st.secrets["connections"]["webapp_url"]
    payload = {"action": "complete", "rowIndex": index, "durum": status, "sure": sure_saniye, "soru_sayisi": soru_sayisi}
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
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"Profil: {user}")
        
        if user == "Berru": st.image("https://cdn-icons-png.flaticon.com/512/4322/4322991.png", width=80)
        elif user == "Ela": st.image("https://cdn-icons-png.flaticon.com/512/4322/4322992.png", width=80)
        elif user == "Anne": st.image("https://cdn-icons-png.flaticon.com/512/2942/2942802.png", width=80)
        else: st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
            
        st.write("---")
        
        if user in parents:
            with st.expander("📸 Profil Fotoğrafı Ayarla"):
                st.caption("Berru için resim yükle:")
                uploaded_berru = st.file_uploader("Berru", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key="up_berru")
                if uploaded_berru: st.session_state["img_berru"] = uploaded_berru
                
                st.write("")
                st.caption("Ela için resim yükle:")
                uploaded_ela = st.file_uploader("Ela", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key="up_ela")
                if uploaded_ela: st.session_state["img_ela"] = uploaded_ela

        st.write("---")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state["authenticated_user"] = None
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

            c_sub1, c_sub2, c_sub3 = st.columns([1, 2, 1])
            with c_sub2:
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
                    st.balloons(); time.sleep(1.5); st.rerun()

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

    # --- ANA SAYFA ---
    st.markdown('<div class="main-title">Study Buddy</div>', unsafe_allow_html=True)
    df = get_data()
    # BURASI KRİTİK: Sunucu saatini değil, Türkiye saatini alıyoruz.
    today = get_turkey_time()

    # --- GÖRSEL ÖĞRENCİ SEÇİMİ ---
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
        # VERİYİ FİLTRELE
        filtered_df = df if active_student_filter is None else df[df["Kullanıcı"] == active_student_filter]

        # --- DASHBOARD ---
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
        total_questions = dashboard_data["SoruSayisi"].sum()
        completed_count = len(dashboard_data[dashboard_data["Durum"] == "Tamamlandı"])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric(f"⏱️ Süre", total_time)
        with c2: st.metric(f"✏️ Soru", total_questions)
        with c3: st.metric(f"✅ Görev", f"{completed_count} Adet")
        
        if period != "Günlük" and not dashboard_data.empty:
            with st.expander(f"📊 {metric_label} Performans Grafiği", expanded=True):
                st.bar_chart(dashboard_data.groupby("Ders")["SoruSayisi"].sum())

    st.write("---")

    if user in parents:
        # --- ADMIN GÖRÜNÜMÜ ---
        tab1, tab2 = st.tabs(["⚙️ Görev Yönetimi", "➕ Yeni Ekle"])
        
        with tab1:
            c_filter1, c_filter2 = st.columns([1, 4])
            with c_filter1:
                selected_date = st.date_input("Tarih Seçin:", value=today)
            
            with c_filter2:
                 student_title = active_student_filter if active_student_filter else "Tüm Öğrenciler"
                 st.subheader(f"{student_title} - {selected_date.strftime('%d.%m.%Y')}")

            table_data = filtered_df[filtered_df["Tarih"] == selected_date]
            
            if not table_data.empty:
                col_ratios = [0.4, 0.8, 1.2, 3.0, 1.2, 0.8, 0.6, 1.5]
                header_cols = st.columns(col_ratios)
                titles = ["#", "Öğrenci", "Ders", "Konu", "Durum", "Süre", "Soru", "İşlemler"]
                
                for col, title in zip(header_cols, titles):
                    col.markdown(f"**{title}**")
                
                st.markdown("---") 

                for index, row in enumerate(table_data.itertuples(), start=1):
                    if st.session_state.edit_mode_index == row.rowIndex:
                        with st.container(border=True):
                            st.info(f"Düzenleniyor: {row.Kullanıcı} - {row.Ders}")
                            with st.form(f"edit_form_{index}"):
                                c_edit1, c_edit2 = st.columns(2)
                                ders_list = ["Matematik", "Fen", "Türkçe", "Sosyal", "İngilizce", "Din Kültürü ve Ahlak Bilgisi", "Diğer"]
                                current_ders_idx = ders_list.index(row.Ders) if row.Ders in ders_list else 0
                                
                                new_ders = c_edit1.selectbox("Ders", ders_list, index=current_ders_idx)
                                new_konu = c_edit2.text_input("Konu", value=row.Konu)
                                
                                c_save, c_cancel = st.columns([1, 1])
                                if c_save.form_submit_button("Kaydet", icon=":material/save:", use_container_width=True, type="primary"):
                                    edit_task(row.rowIndex, new_ders, new_konu)
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
                        
                        row_cols[5].write(f"{row.Sure} dk")
                        row_cols[6].write(f"{row.SoruSayisi}")
                        
                        with row_cols[7]:
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
                        
                        st.divider() 
            else:
                st.info(f"{selected_date.strftime('%d.%m.%Y')} tarihinde kayıtlı görev yok.", icon=":material/info:")

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
                                    st.session_state.current_task_info = {"index": row["rowIndex"], "ders": row["Ders"], "konu": row["Konu"]}
                                    update_task_progress(row["rowIndex"], "Çalışılıyor", row["Sure"], row["SoruSayisi"])
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