import streamlit as st
import pandas as pd
import io
import re
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="OMÜ Times Higher Education Dinamik FTE Simülasyonu",
    page_icon="🧪",
    layout="wide"
)

# --- Constants & Defaults ---
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzLuDZwaGzYM-6SsYGvgWop8ZUSHfM9Efysy5kCkNh1sk0Bn-kRgD2hPQutQHp7-NlS3Q/exec"

REQUIRED_COLS = [
    "Ad Soyad", "Unvan", "İdari Görev", "Yayın Sayısı",
    "Uyruk", "Cinsiyet", "Birim"
]

DEFAULT_PENALTIES = [
    {"Anahtar Kelime": "Bölüm Başkanı", "Kesinti": 0.2},
    {"Anahtar Kelime": "Dekan", "Kesinti": 0.4},
    {"Anahtar Kelime": "Müdür", "Kesinti": 0.4},
    {"Anahtar Kelime": "Rektör", "Kesinti": 0.5},
]

DEFAULT_TITLES = [
    {"Ünvan": "Prof. Dr.", "Katsayı": 1.0},
    {"Ünvan": "Doç. Dr.", "Katsayı": 1.0},
    {"Ünvan": "Dr. Öğr. Üyesi", "Katsayı": 1.0},
    {"Ünvan": "Öğr. Gör.", "Katsayı": 1.0},
    {"Ünvan": "Arş. Gör.", "Katsayı": 1.0},
]

def clean_data(df):
    """Clean and normalize column names."""
    # Normalize headers: Strip, Title Case
    df.columns = [c.strip().title() for c in df.columns]
    
    # Map expected columns loosely (Case Insensitive)
    # Mapping Dict: {Internal_Name: [Potential User Names]}
    col_mapping = {
        "Ad Soyad": ["Ad Soyad", "Name", "Ad", "Soyad"],
        "Unvan": ["Unvan", "Ünvan", "Title", "Rank"],
        "İdari Görev": ["İdari Görev", "Admin Role", "Gorev", "Rol"],
        "Yayın Sayısı": ["Yayın Sayısı", "Yayin Sayisi", "Pubs", "Publication Count", "Papers"],
        "Uyruk": ["Uyruk", "Milliyet", "Nationality"],
        "Cinsiyet": ["Cinsiyet", "Gender", "Sex"],
        "Birim": ["Birim", "Department", "Faculty", "Görev Yeri"]
    }
    
    found_cols = df.columns
    rename_map = {}
    
    for standard, alternatives in col_mapping.items():
        for alt in alternatives:
            # Case insensitive match
            match = next((c for c in found_cols if c.lower() == alt.lower()), None)
            if match:
                rename_map[match] = standard
                break # Found one match for this standard col
    
    df = df.rename(columns=rename_map)
    
    # Check missing mandatory for logic (Optional ones can be filled empty)
    # Critical: Yayin, Idari - others can be inferred or left blank
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = None # Fill missing as None to prevent KeyError
            
    return df

# --- Cloud Sync Manager ---
class SyncManager:
    @staticmethod
    def load_from_cloud(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
            return None

    @staticmethod
    def save_to_cloud(url, titles_df, penalties_df):
        # Sanitize NaNs which break JSON serialization
        # Titles: Fill text with empty, numbers with 1.0 (default)
        t_clean = titles_df.copy()
        t_clean["Ünvan"] = t_clean["Ünvan"].fillna("")
        t_clean["Katsayı"] = t_clean["Katsayı"].fillna(1.0)
        # Rename to safe key (Unvan) to avoid encoding issues
        t_clean = t_clean.rename(columns={"Ünvan": "Unvan", "Katsayı": "Katsayi"})
        
        # Penalties: Fill text with empty, numbers with 0.0
        p_clean = penalties_df.copy()
        p_clean["Anahtar Kelime"] = p_clean["Anahtar Kelime"].fillna("")
        p_clean["Kesinti"] = p_clean["Kesinti"].fillna(0.0)
        # Rename to safe key (Anahtar_Kelime) to avoid space issues
        p_clean = p_clean.rename(columns={"Anahtar Kelime": "Anahtar_Kelime"})
        
        payload = {
            "action": "save",
            "titles": t_clean.to_dict(orient="records"),
            "penalties": p_clean.to_dict(orient="records")
        }
        try:
            # Using requests.post to send JSON data
            # Ensure utf-8? requests handles it, but explicit ensure_ascii=False in json dump might be safer if we did it manually.
            # Here letting requests handle it.
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            st.error(f"Kaydetme Hatası: {e}")
            return False

    @staticmethod
    def delete_from_cloud(url):
        payload = {"action": "delete"}
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            st.error(f"Silme Hatası: {e}")
            return False

def calculate_dynamic_fte(df, params, penalty_df, title_df):
    """
    Core Simulation Engine.
    """
    results = df.copy()
    
    # Fill NAs
    results["İdari Görev"] = results["İdari Görev"].fillna("Yok")
    results["Yayın Sayısı"] = pd.to_numeric(results["Yayın Sayısı"], errors='coerce').fillna(0)
    results["Birim"] = results["Birim"].fillna("")
    results["Unvan"] = results["Unvan"].fillna("")
    
    # Create Title Map
    title_map = pd.Series(title_df.Katsayı.values, index=title_df["Ünvan"]).to_dict()
    
    results["FTE_Final"] = 0.0
    results["Hesaplama Detayı"] = ""
    results["Etki_Turu"] = "Normal"
    
    def calc_row(row):
        birim = str(row["Birim"]).upper()
        if "MYO" in birim or "MESLEK YÜKSEK" in birim:
            return 0.0, "MYO Filtresi (0.0)", "MYO"
        
        title = str(row["Unvan"]).strip()
        base_fte = title_map.get(title, 1.0)
        
        log_parts = [f"{base_fte:.2f} ({title if title else 'Baz'})"]
        running_fte = base_fte
        effect = "Normal"
        
        idari = str(row["İdari Görev"]).lower()
        penalty = 0.0
        
        matched_penalty = 0.0
        matched_keyword = ""
        
        for _, rule in penalty_df.iterrows():
            keyword = str(rule["Anahtar Kelime"]).lower()
            val = float(rule["Kesinti"])
            if keyword in idari and val > matched_penalty:
                matched_penalty = val
                matched_keyword = rule["Anahtar Kelime"]
        
        if matched_penalty > 0:
            penalty = matched_penalty
            log_parts.append(f"- {penalty} ({matched_keyword})")
            running_fte -= penalty
            effect = "Kesintili"
            
            pubs = row["Yayın Sayısı"]
            bonus = 0.0
            if pubs >= params["bonus_threshold"]:
                bonus = params["bonus_val"]
                log_parts.append(f"+ {bonus} (Bonus)")
                running_fte += bonus
                effect = "Kesinti+Bonus"

        else:
            pubs = row["Yayın Sayısı"]
            if pubs < params["low_pub_threshold"]:
                low_pen = params["low_pub_penalty"]
                if low_pen > 0:
                    running_fte -= low_pen
                    log_parts.append(f"- {low_pen} (Düşük Yayın)")
                    effect = "Düşük Perf."

        final_fte = max(0.0, min(1.0, running_fte))
        
        if final_fte != running_fte:
             log_parts.append(f"= {running_fte:.2f} -> {final_fte:.1f} (Limit)")
        else:
             log_parts.append(f"= {final_fte:.2f}")
             
        log_str = " ".join(log_parts)
        return final_fte, log_str, effect

    for idx, row in results.iterrows():
        f, l, e = calc_row(row)
        results.at[idx, "FTE_Final"] = f
        results.at[idx, "Hesaplama Detayı"] = l
        results.at[idx, "Etki_Turu"] = e
        
    return results

# --- Student Module Logic ---
STUDENT_COLS = [
    "Ogrenci No", "Statu", "Yariyil", "Asama", "Uyruk", "Seviye"
]

def calculate_student_fte(df, level_params):
    """
    Calculates Student FTE based on level-specific rules.
    """
    results = df.copy()
    
    results["Statu"] = results["Statu"].fillna("").astype(str).str.strip().str.title()
    results["Asama"] = results["Asama"].fillna("").astype(str).str.strip().str.title()
    results["Seviye"] = results["Seviye"].fillna("").astype(str).str.strip().str.title()
    results["Yariyil"] = pd.to_numeric(results["Yariyil"], errors='coerce').fillna(0)
    
    results["FTE_Final"] = 0.0
    results["Kesinti Nedeni"] = "Normal"
    
    def calc_student_row(row):
        statu = row["Statu"]
        yariyil = row["Yariyil"]
        asama = row["Asama"]
        seviye = row["Seviye"]
        
        if "Mezun" in statu:
            return 0.0, "Mezun (Dahil Değil)"
            
        passive_keywords = ["Pasif", "Dondur", "İzinli", "Izinli", "Kaydı Silinmiş"]
        if any(k in statu for k in passive_keywords):
            return 0.0, "Pasif/Dondurmuş"
            
        current_fte = 1.0
        reasons = []
        
        p = None
        if "Lisans" in seviye and "Yüksek" not in seviye:
            p = level_params.get("Lisans")
        elif "Yüksek" in seviye or "Master" in seviye:
            p = level_params.get("Yüksek Lisans")
        elif "Doktora" in seviye or "Phd" in seviye:
            p = level_params.get("Doktora")
            
        if not p:
            return 1.0, "Aktif (Seviye Belirsiz)"
            
        if "limit" in p and yariyil > p["limit"]:
            current_fte = min(current_fte, p["ext_coef"])
            reasons.append(f"Uzatmalı (>{p['limit']})")
            
        if "thesis_coef" in p and "Tez" in asama:
            current_fte = min(current_fte, p["thesis_coef"])
            reasons.append("Tez Dönemi")
            
        final_reason = " + ".join(reasons) if reasons else "Aktif (Tam)"
        return current_fte, final_reason

    for idx, row in results.iterrows():
        f, r = calc_student_row(row)
        results.at[idx, "FTE_Final"] = f
        results.at[idx, "Kesinti Nedeni"] = r
        
    return results

def create_template(columns):
    df = pd.DataFrame(columns=columns)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Main App ---
def main():
    st.title("🧪 OMÜ Times Higher Education Dinamik FTE Simülasyonu")
    st.markdown("İdari yükleri, akademik performansı ve öğrenci ağırlıklarını simüle ederek **Gerçekçi FTE** değerini hesaplayın.")
    
    # --- Auto Load from Cloud ---
    if "data_loaded" not in st.session_state:
        # Initial Load
        data = SyncManager.load_from_cloud(GOOGLE_SHEET_URL)
        if data:
            if "titles" in data and data["titles"]:
                st.session_state.title_rules = pd.DataFrame(data["titles"])
            if "penalties" in data and data["penalties"]:
                st.session_state.penalty_rules = pd.DataFrame(data["penalties"])
            st.toast("Ayarlar Buluttan Yüklendi!", icon="☁️")
        st.session_state.data_loaded = True
        
    tab_staff, tab_student = st.tabs(["👨‍🏫 Personel Analizi", "🎓 Öğrenci Analizi"])
    
    # ---------------- STAFF TAB ----------------
    with tab_staff:
        st.header("Akademik Personel Hesaplama")
        
        # Sidebar Config for Staff
        with st.sidebar:
            st.header("🔧 Personel Ayarları")
            
            # Helper for Data Editor Callbacks
            def sync_data():
                # Get latest from session state (which is updated by data_editor before callback)
                # Note: st.session_state["title_editor"] return the edited dataframe directly in recent streamlit versions?
                # Actually, data_editor returns the DF, but doesn't auto-update a key in a way we can grab in callback EASILY without using 'key' binding to a specialized session state object or just using the 'on_change' to trigger a rerun where we save?
                # Best approach for "on_change":
                # The callback runs. We need access to the NEW data.
                # However, streamlit data_editor with `key` stores the *changes* in session state, not the full DF usually? 
                # Wait, data_editor returns the full DF. 
                # Let's simplify: We don't need a callback. We check state diff.
                pass 
                
            # Actually, simpler Real-Time Sync pattern in Streamlit:
            # 1. Load data from session state.
            # 2. Editor modifies it.
            # 3. If modification detected (return val != session_state val), Save & Update.
            
            with st.expander("Ünvan Katsayıları (Baz)", expanded=False):
                st.info("Değişiklikler otomatik olarak Google Sheet'e kaydedilir.")
                
                if "title_rules" not in st.session_state:
                    st.session_state.title_rules = pd.DataFrame(DEFAULT_TITLES)
                
                new_titles = st.data_editor(
                    st.session_state.title_rules,
                    num_rows="dynamic",
                    key="title_editor_widget",
                    use_container_width=True
                )
                
                # Auto-Save Check
                if not new_titles.equals(st.session_state.title_rules):
                    st.session_state.title_rules = new_titles
                    # Save both (we need penalties too)
                    curr_penalties = st.session_state.get("penalty_rules", pd.DataFrame(DEFAULT_PENALTIES))
                    SyncManager.save_to_cloud(GOOGLE_SHEET_URL, new_titles, curr_penalties)
                    st.toast("Ünvanlar Kaydedildi!", icon="💾")
                    
            with st.expander("İdari Kesintiler (Tablo)", expanded=False):
                st.info("Değişiklikler otomatik olarak Google Sheet'e kaydedilir.")
                
                if "penalty_rules" not in st.session_state:
                    st.session_state.penalty_rules = pd.DataFrame(DEFAULT_PENALTIES)
                    
                new_penalties = st.data_editor(
                    st.session_state.penalty_rules, 
                    num_rows="dynamic",
                    key="penalty_editor_widget",
                    column_config={
                        "Anahtar Kelime": st.column_config.TextColumn("Rol / Kelime"),
                        "Kesinti": st.column_config.NumberColumn("Eksilecek Puan", min_value=0.0, max_value=1.0, step=0.05, format="%.2f")
                    },
                    use_container_width=True
                )
                
                # Auto-Save Check
                if not new_penalties.equals(st.session_state.penalty_rules):
                    st.session_state.penalty_rules = new_penalties
                    # Save both
                    curr_titles = st.session_state.get("title_rules", pd.DataFrame(DEFAULT_TITLES))
                    SyncManager.save_to_cloud(GOOGLE_SHEET_URL, curr_titles, new_penalties)
                    st.toast("Kesintiler Kaydedildi!", icon="💾")
            
            with st.expander("Düşük Performans Kesintisi", expanded=False):
                st.warning("İdari görevi OLMAYAN ancak yayını az olanlar için.")
                low_pub_threshold = st.number_input("Min. Yayın Limiti", 0, 20, 2)
                low_pub_penalty = st.slider("Düşük Perf. Cezası", 0.0, 0.5, 0.1, 0.05)
                
            with st.expander("Performans Bonusu", expanded=False):
                st.success("İdari görevi OLAN ve Yüksek yayın yapanlara eklenecek telafi puanı.")
                bonus_threshold = st.number_input("Yayın Eşik Değeri (Adet)", 1, 50, 5)
                bonus_val = st.slider("Bonus Katsayısı", 0.0, 0.5, 0.2, 0.05)
                
            # Staff Params Dict
            staff_params = {
                "bonus_threshold": bonus_threshold, "bonus_val": bonus_val,
                "low_pub_threshold": low_pub_threshold, "low_pub_penalty": low_pub_penalty
            }
            
            # Staff Template
            st.markdown("---")
            staff_template = create_template(REQUIRED_COLS)
            st.download_button("📥 Personel Şablonu", staff_template, "Personel_Sablon.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.markdown("---")

        # Staff Input & Calc
        staff_file = st.file_uploader("Personel Dosyası (.xlsx)", type=["xlsx"], key="staff_up")
        
        if staff_file:
            df_staff = pd.read_excel(staff_file)
            df_staff = clean_data(df_staff)
            res_staff = calculate_dynamic_fte(df_staff, staff_params, st.session_state.penalty_rules, st.session_state.title_rules)
            
            if res_staff is not None:
                # Metrics
                total_fte = res_staff["FTE_Final"].sum()
                avg_fte = res_staff["FTE_Final"].mean()
                mask_int = (res_staff["Uyruk"].astype(str).str.strip().str.upper() != "TC") & (res_staff["Uyruk"].notna())
                mask_fem = res_staff["Cinsiyet"].astype(str).str.lower().isin(["kadın", "female", "k"])
                int_fte = res_staff[mask_int]["FTE_Final"].sum()
                fem_fte = res_staff[mask_fem]["FTE_Final"].sum()
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Staff FTE", f"{total_fte:.2f}")
                c2.metric("Average FTE", f"{avg_fte:.2f}")
                c3.metric("International Staff FTE", f"{int_fte:.2f}")
                c4.metric("Female Staff FTE", f"{fem_fte:.2f}")
                
                # Impact Analysis
                st.subheader("Simülasyon Etkisi")
                count_reduced = len(res_staff[res_staff["Etki_Turu"].isin(["Kesintili", "Kesinti+Bonus"])])
                count_bonus = len(res_staff[res_staff["Etki_Turu"].isin(["Bonuslu", "Kesinti+Bonus"])])
                
                ic1, ic2 = st.columns(2)
                ic1.metric("Kesinti Uygulanan", count_reduced)
                ic1.metric("Bonus Kazanan", count_bonus)
                
                dist_df = res_staff["Etki_Turu"].value_counts().reset_index()
                dist_df.columns = ["Durum", "Kişi Sayısı"]
                ic2.bar_chart(dist_df, x="Durum", y="Kişi Sayısı", color="Durum")
                
                # Table
                st.subheader("Detaylı Tablo")
                display_cols = ["Ad Soyad", "Unvan", "İdari Görev", "Yayın Sayısı", "FTE_Final", "Hesaplama Detayı"]
                st.dataframe(res_staff[[c for c in display_cols if c in res_staff.columns]], use_container_width=True)
                st.download_button("📥 Personel Sonuç İndir", to_excel(res_staff), "FTE_Personel_Sonuc.xlsx")

    # ---------------- STUDENT TAB ----------------
    with tab_student:
        st.header("Öğrenci Hesaplama")
        
        # Sidebar Config for Student
        with st.sidebar:
            st.header("🎓 Öğrenci Ayarları")
            
            # Level Tabs in Sidebar
            lst1, lst2, lst3 = st.tabs(["Lisans", "Yüksek Lisans", "Doktora"])
            
            student_params = {}
            
            with lst1:
                st.caption("Lisans Kuralları")
                ug_limit = st.number_input("Lisans Uzatmalı Sınırı", 1, 12, 8, key="ug_lim")
                ug_coeff = st.slider("Lisans Uzatmalı Katsayısı", 0.0, 1.0, 0.5, 0.1, key="ug_coef")
                student_params["Lisans"] = {"limit": ug_limit, "ext_coef": ug_coeff}
                
            with lst2:
                st.caption("Yüksek Lisans Kuralları")
                # User requested removal of Extended logic for Master
                master_thesis_coef = st.slider("YL Tez Dönemi Katsayısı", 0.0, 1.0, 0.5, 0.1, key="mas_the")
                student_params["Yüksek Lisans"] = {"thesis_coef": master_thesis_coef}
                
            with lst3:
                st.caption("Doktora Kuralları")
                # User requested removal of Extended logic for PhD
                phd_thesis_coef = st.slider("Doktora Tez Dönemi Katsayısı", 0.0, 1.0, 0.5, 0.1, key="phd_the")
                student_params["Doktora"] = {"thesis_coef": phd_thesis_coef}
            
            st.markdown("---")
            student_template = create_template(STUDENT_COLS)
            st.download_button("📥 Öğrenci Şablonu", student_template, "Ogrenci_Sablon.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
        student_file = st.file_uploader("Öğrenci Dosyası (.xlsx)", type=["xlsx"], key="student_up")
        
        if student_file:
            df_student = pd.read_excel(student_file)
            
            res_student = calculate_student_fte(df_student, student_params)
            
            # Metrics
            total_student_fte = res_student["FTE_Final"].sum()
            
            # Breakdown by Level
            # Using simple string matching on "Seviye"
            mask_ug = res_student["Seviye"].str.contains("Lisans") & ~res_student["Seviye"].str.contains("Yüksek")
            mask_master = res_student["Seviye"].str.contains("Yüksek") | res_student["Seviye"].str.contains("Master")
            mask_phd = res_student["Seviye"].str.contains("Doktora") | res_student["Seviye"].str.contains("Phd")
            
            ug_fte = res_student[mask_ug]["FTE_Final"].sum()
            master_fte = res_student[mask_master]["FTE_Final"].sum()
            phd_fte = res_student[mask_phd]["FTE_Final"].sum()
            
            # International
            u_series = res_student["Uyruk"].astype(str).str.upper().fillna("")
            int_student_fte = res_student[u_series != "TC"]["FTE_Final"].sum()
            
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Total Students (FTE)", f"{total_student_fte:.2f}")
            sc2.metric("Lisans (FTE)", f"{ug_fte:.2f}")
            sc3.metric("Yüksek Lisans (FTE)", f"{master_fte:.2f}")
            sc4.metric("Doktora (FTE)", f"{phd_fte:.2f}")
            
            st.metric("International Students (FTE)", f"{int_student_fte:.2f}")

            # Chart: Headcount vs FTE
            st.subheader("Kayıtlı vs Ağırlıklı (FTE)")
            raw_count = len(res_student)
            chart_data = pd.DataFrame({
                "Tip": ["Kayıtlı (Kafa Sayısı)", "FTE (Ağırlıklı)"],
                "Değer": [raw_count, total_student_fte]
            })
            st.bar_chart(chart_data, x="Tip", y="Değer")
            
            # Table
            st.subheader("Öğrenci Analiz Tablosu")
            st.dataframe(res_student, use_container_width=True)
            st.download_button("📥 Öğrenci Sonuç İndir", to_excel(res_student), "FTE_Ogrenci_Sonuc.xlsx")

    # Developer Footer in Sidebar
    # Using markdown with unsafe_allow_html to style a card-like footer
    st.sidebar.markdown("""
    <style>
    .footer-card {
        margin-top: 50px;
        padding: 15px;
        background-color: rgba(150, 150, 150, 0.1);
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(150, 150, 150, 0.2);
    }
    .footer-card p {
        margin: 0;
    }
    .footer-sub {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-bottom: 5px !important;
    }
    .footer-name {
        font-weight: bold;
        font-size: 1.0rem;
        margin-bottom: 8px !important;
    }
    .footer-icons a {
        text-decoration: none;
        font-size: 1.2rem;
        margin: 0 8px;
        opacity: 0.8;
        transition: opacity 0.3s;
    }
    .footer-icons a:hover {
        opacity: 1.0;
    }
    </style>
    <div class="footer-card">
        <p class="footer-sub">Developed by</p>
        <p class="footer-name">Çağatay YILDIRIM</p>
        <div class="footer-icons">
            <a href="www.cagatayyildirim.com" target="_blank" title="">🎓</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

