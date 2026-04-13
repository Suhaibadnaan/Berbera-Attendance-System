import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
# --- 1. CUSBOONAYSIIN: Hubinta haddii uu Server yahay ---
try:
    import pywhatkit as kit
    WIKIT_AVAILABLE = True
except Exception:
    WIKIT_AVAILABLE = False
    
import time
from fpdf import FPDF

# --- 1. DATABASE CONFIG ---
def init_db():
    conn = sqlite3.connect('berbera_hr_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shaqaale (id INTEGER PRIMARY KEY, magaca TEXT, tel TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (shaqaale_id INTEGER, taariikh DATE, soo_galis TEXT, bixitaan TEXT, status TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'Admin')")
    conn.commit()
    conn.close()

# --- 2. PDF REPORT GENERATOR ---
def create_pdf(df, report_title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="DAWLADA HOOSE EE BERBERA", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Warbixinta: {report_title}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    cols = ["Magaca", "Taariikh", "In", "Out", "Status"]
    for col in cols: pdf.cell(38, 10, col, 1)
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(38, 10, str(row['magaca']), 1)
        pdf.cell(38, 10, str(row['taariikh']), 1)
        pdf.cell(38, 10, str(row['soo_galis']), 1)
        pdf.cell(38, 10, str(row['bixitaan']), 1)
        pdf.cell(38, 10, str(row['status']), 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGIN PAGE ---
def login_page():
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(to bottom, #f0f2f6, #ffffff); }
        .login-card {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 10px solid #0056b3;
        }
        .header-text { color: #0056b3; font-weight: bold; }
        </style>
        <div class="login-card">
            <h1 class="header-text">🏛️ DAWLADA HOOSE EE BERBERA</h1>
            <h3 style="color: #555;">QAYBTA MAAMULKA SHAQAALAHA (HR)</h3>
            <p>Nidaamka Xadiiriska ee UA300 Smart System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("Login Form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            submit = st.form_submit_button("LOGIN", use_container_width=True)
            if submit:
                conn = sqlite3.connect('berbera_hr_system.db')
                c = conn.cursor()
                c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p))
                user = c.fetchone()
                conn.close()
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = user[0]
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Macluumaad khaldan!")

# --- 4. MAIN SYSTEM ---
init_db()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
else:
    st.sidebar.title("🏢 BERBERA HR")
    st.sidebar.info(f"User: {st.session_state['user']} ({st.session_state['role']})")
    menu = ["📊 Dashboard", "➕ Diiwaanka Cusub", "⏱️ Xadiiriska (ZKT)", "📂 Maareynta & Printing", "📩 WhatsApp", "⚙️ Settings"]
    choice = st.sidebar.selectbox("Menu", menu)

    # (A, B, C, D isku mid bay ahaanayaan...)
    if choice == "📊 Dashboard":
        st.title("📊 Dashboard-ka Guud")
        conn = sqlite3.connect('berbera_hr_system.db')
        c1, c2, c3 = st.columns(3)
        total = pd.read_sql_query("SELECT COUNT(*) FROM shaqaale", conn).iloc[0,0]
        c1.metric("Wadar Shaqaale", total)
        maanta = datetime.now().strftime("%Y-%m-%d")
        jooga = pd.read_sql_query(f"SELECT COUNT(*) FROM attendance WHERE taariikh='{maanta}'", conn).iloc[0,0]
        c2.metric("Jooga Maanta", jooga)
        c3.metric("Maqan", total - jooga)
        st.divider()
        st.subheader("🔍 Baadhitaan Degdeg ah")
        search = st.text_input("Ku baadh Magaca ama ID...")
        if search:
            res = pd.read_sql_query(f"SELECT * FROM shaqaale WHERE magaca LIKE '%{search}%' OR id LIKE '%{search}%'", conn)
            st.table(res)
        conn.close()

    elif choice == "➕ Diiwaanka Cusub":
        st.subheader("📝 Diiwaangali Shaqaale Cusub")
        with st.form("Reg Form"):
            m = st.text_input("Magaca oo buuxa")
            t = st.text_input("Taleefanka (25263...)")
            if st.form_submit_button("Keydi"):
                conn = sqlite3.connect('berbera_hr_system.db')
                conn.execute("INSERT INTO shaqaale (magaca, tel) VALUES (?,?)", (m, t))
                conn.commit()
                conn.close()
                st.success("Shaqaalaha waa la keydiyey!")

    elif choice == "⏱️ Xadiiriska (ZKT)":
        st.subheader("⏱️ Xadiiriska UA300 - 7:00 AM / 12:00 PM")
        conn = sqlite3.connect('berbera_hr_system.db')
        df_s = pd.read_sql_query("SELECT * FROM shaqaale", conn)
        maanta = datetime.now().strftime("%Y-%m-%d")
        for i, row in df_s.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"👤 **{row['magaca']}**")
            if col2.button(f"IN (Fingerprint)", key=f"i{row['id']}"):
                t = datetime.now().strftime("%H:%M:%S")
                conn.execute("INSERT INTO attendance (shaqaale_id, taariikh, soo_galis, status) VALUES (?,?,?,?)", (row['id'], maanta, t, 'Present'))
                conn.commit()
                st.success(f"Galay: {t}")
            if col3.button(f"OUT (Fingerprint)", key=f"o{row['id']}"):
                t = datetime.now().strftime("%H:%M:%S")
                conn.execute("UPDATE attendance SET bixitaan=? WHERE shaqaale_id=? AND taariikh=?", (t, row['id'], maanta))
                conn.commit()
                st.error(f"Baxay: {t}")
        conn.close()

    elif choice == "📂 Maareynta & Printing":
        st.header("📂 Maareynta Xogta & PDF")
        conn = sqlite3.connect('berbera_hr_system.db')
        df_all = pd.read_sql_query("SELECT s.id, s.magaca, a.taariikh, a.soo_galis, a.bixitaan, a.status FROM shaqaale s LEFT JOIN attendance a ON s.id = a.shaqaale_id", conn)
        st.dataframe(df_all)
        if st.session_state['role'] == "Admin":
            st.divider()
            target = st.number_input("ID-ga Shaqaalaha ee la wax ka badalayo", step=1)
            cA, cB, cC = st.columns(3)
            with cA:
                st.write("### Edit Profile")
                n_m = st.text_input("Magac Cusub")
                if st.button("Update Profile"):
                    conn.execute("UPDATE shaqaale SET magaca=? WHERE id=?", (n_m, target))
                    conn.commit()
                    st.rerun()
            with cB:
                st.write("### Sax Habsanka")
                n_d = st.date_input("Taariikhda")
                n_i = st.text_input("Saacadda saxda ah")
                if st.button("Update Xadiiris"):
                    conn.execute("UPDATE attendance SET soo_galis=? WHERE shaqaale_id=? AND taariikh=?", (n_i, target, n_d.strftime("%Y-%m-%d")))
                    conn.commit()
                    st.rerun()
            with cC:
                st.write("### Delete")
                if st.button("🗑️ Tirtir Shaqaalaha"):
                    conn.execute("DELETE FROM shaqaale WHERE id=?", (target,))
                    conn.commit()
                    st.rerun()
            if st.button("📥 Download PDF Report"):
                pdf_bytes = create_pdf(df_all, "Warbixinta Guud ee HR Berbera")
                st.download_button("Riix halkan si aad u dejiso", pdf_bytes, "Berbera_HR_Report.pdf")
        conn.close()

    # --- 📩 QAYBTA WHATSAPP-KA (OO LA SAXAY) ---
    elif choice == "📩 WhatsApp":
        st.subheader("📩 Dirista Fariimaha WhatsApp")
        if not WIKIT_AVAILABLE:
            st.error("⚠️ Fariimaha WhatsApp waxaa laga diri karaa oo kaliya laptop-kaaga (Localhost). Streamlit Cloud ma diri karo WhatsApp sababtoo ah ma laha screen.")
        else:
            m_day = st.number_input("Maalmaha shaqada bishii", value=26)
            if st.button("Dir Fariimaha Dhammaan"):
                conn = sqlite3.connect('berbera_hr_system.db')
                df_s = pd.read_sql_query("SELECT * FROM shaqaale", conn)
                for _, row in df_s.iterrows():
                    yimid = pd.read_sql_query(f"SELECT COUNT(*) FROM attendance WHERE shaqaale_id={row['id']} AND status='Present'", conn).iloc[0,0]
                    fariin = f"Asalaamu Calaykum {row['magaca']}, waxaa kuu diiwaangashan {m_day - yimid} maalmood oo maqnaansho ah."
                    kit.sendwhatmsg_instantly(f"+{row['tel']}", fariin, 15, True)
                    st.toast(f"Loo diray {row['magaca']}")
                conn.close()

    elif choice == "⚙️ Settings":
        st.header("⚙️ Maamulka User-ada")
        conn = sqlite3.connect('berbera_hr_system.db')
        df_users = pd.read_sql_query("SELECT username, role FROM users", conn)
        st.table(df_users)
        if st.session_state['role'] == "Admin":
            with st.expander("Ku dar User Cusub"):
                new_u = st.text_input("Username")
                new_p = st.text_input("Password", type='password')
                new_r = st.selectbox("Role", ["Admin", "User"])
                if st.button("Keydi User"):
                    conn.execute("INSERT INTO users VALUES (?,?,?)", (new_u, new_p, new_r))
                    conn.commit()
                    st.rerun()
            del_u = st.text_input("Username-ka la tirtirayo")
            if st.button("Tirtir User"):
                conn.execute("DELETE FROM users WHERE username=?", (del_u,))
                conn.commit()
                st.rerun()
        conn.close()

    if st.sidebar.button("LOGOUT"):
        st.session_state['logged_in'] = False
        st.rerun()