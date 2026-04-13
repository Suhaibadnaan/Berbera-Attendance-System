import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
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
            background-color: #ffffff; padding: 40px; border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 10px solid #0056b3;
        }
        .header-text { color: #0056b3; font-weight: bold; }
        </style>
        <div class="login-card">
            <h1 class="header-text">🏛️ DAWLADA HOOSE EE BERBERA</h1>
            <h3 style="color: #555;">HR MANAGEMENT SYSTEM</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("Login Form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.form_submit_button("LOGIN", use_container_width=True):
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

# --- MAIN ---
init_db()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
else:
    st.sidebar.title("🏢 BERBERA HR")
    menu = ["📊 Dashboard", "➕ Diiwaanka Cusub", "⏱️ Xadiiriska (ZKT)", "📂 Maareynta & Printing", "📩 WhatsApp", "⚙️ Settings"]
    choice = st.sidebar.selectbox("Menu", menu)

    # A. DASHBOARD
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
        conn.close()

    # B. DIIWAANGALINTA
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

    # C. XADIIRISKA (HAGAAGINTA BIXITAANKA)
    elif choice == "⏱️ Xadiiriska (ZKT)":
        st.subheader("⏱️ Xadiiriska Maalinlaha ah")
        conn = sqlite3.connect('berbera_hr_system.db')
        df_s = pd.read_sql_query("SELECT * FROM shaqaale", conn)
        maanta = datetime.now().strftime("%Y-%m-%d")
        
        for i, row in df_s.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"👤 **{row['magaca']}**")
            
            # Button-ka Soo Gelista (Ma taban)
            if col2.button(f"IN", key=f"i{row['id']}"):
                t = datetime.now().strftime("%H:%M:%S")
                conn.execute("INSERT INTO attendance (shaqaale_id, taariikh, soo_galis, status) VALUES (?,?,?,?)", (row['id'], maanta, t, 'Present'))
                conn.commit()
                st.success(f"Galay: {t}")
            
            # Button-ka Bixitaanka (Haddii la ilaawo waa la riixi karaa mar kale)
            if col3.button(f"OUT", key=f"o{row['id']}"):
                t = datetime.now().strftime("%H:%M:%S")
                conn.execute("UPDATE attendance SET bixitaan=? WHERE shaqaale_id=? AND taariikh=?", (t, row['id'], maanta))
                conn.commit()
                st.error(f"Baxay: {t}")
        conn.close()

    # D. MAAREYNTA & PDF (SAXIDDA XOGTA HADDA KA HOR)
    elif choice == "📂 Maareynta & Printing":
        st.header("📂 Maareynta & Saxidda Xogta")
        conn = sqlite3.connect('berbera_hr_system.db')
        df_all = pd.read_sql_query("SELECT s.id, s.magaca, a.taariikh, a.soo_galis, a.bixitaan, a.status FROM shaqaale s LEFT JOIN attendance a ON s.id = a.shaqaale_id", conn)
        st.dataframe(df_all)
        
        if st.session_state['role'] == "Admin":
            st.divider()
            st.write("### 🛠️ Saxidda Xogta Bixitaanka (Out Time Update)")
            target = st.number_input("ID-ga Shaqaalaha ee la saxayo", step=1)
            n_d = st.date_input("Taariikhda la saxayo")
            n_o = st.text_input("Saacadda bixitaanka saxda ah (00:00:00)")
            
            if st.button("Cusboonaysii Bixitaanka"):
                conn.execute("UPDATE attendance SET bixitaan=? WHERE shaqaale_id=? AND taariikh=?", (n_o, target, n_d.strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Waa la saxay saacadda bixitaanka!")
                st.rerun()
        conn.close()

    # E. WHATSAPP (XALKA INTERNET-KA TOOSKA AH)
    elif choice == "📩 WhatsApp":
        st.subheader("📩 Dirista Fariimaha (WhatsApp Link)")
        st.info("Riix badhanka 'Dir Fariinta' si aad toos ugu dirto WhatsApp-ka.")
        conn = sqlite3.connect('berbera_hr_system.db')
        df_s = pd.read_sql_query("SELECT * FROM shaqaale", conn)
        m_day = st.number_input("Maalmaha shaqada bishii", value=26)
        
        for _, row in df_s.iterrows():
            yimid = pd.read_sql_query(f"SELECT COUNT(*) FROM attendance WHERE shaqaale_id={row['id']} AND status='Present'", conn).iloc[0,0]
            maqnaansho = m_day - yimid
            fariin = f"Asalaamu Calaykum {row['magaca']}, waxaad bishan maqnayd {maqnaansho} maalmood."
            
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 {row['magaca']} ({row['tel']})")
            
            # Xidhiidhka WhatsApp-ka
            clean_tel = str(row['tel']).replace('+', '').strip()
            link = f"https://wa.me/{clean_tel}?text={fariin.replace(' ', '%20')}"
            col2.markdown(f'[💬 Dir Fariinta]({link})', unsafe_allow_html=True)
        conn.close()

    if st.sidebar.button("LOGOUT"):
        st.session_state['logged_in'] = False
        st.rerun()