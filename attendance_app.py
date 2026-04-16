import streamlit as st
from zk import ZK
import pandas as pd
import sqlite3

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Nidaamka Maamulka Shaqaalaha", layout="wide")

# --- 2. DATABASE FUNCTIONS ---
def get_db_connection():
    conn = sqlite3.connect('xafiis.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inaan hubino in jadwalka attendance-ku jiro
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS attendance_logs 
                    (User_ID TEXT, Waqtiga TEXT, Nooca TEXT, Xarunta TEXT)''')
    conn.close()

init_db()

# --- 3. BIOMETRIC SYNC FUNCTION (ZeroTier Ready) ---
XARUMAHA_IP = {
    "Xarunta Dhaxe": "10.31.176.115",
    "Xarunta Barwaaqo": "10.31.176.X",
    "Xarunta 26 Juun": "10.31.176.X",
}

def get_attendance_from_machine(ip_address):
    conn = None
    zk = ZK(ip_address, port=4370, timeout=15, force_tcp=True)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        data = []
        for entry in attendance:
            data.append({
                "User_ID": entry.user_id,
                "Waqtiga": entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "Nooca": entry.punch
            })
        return pd.DataFrame(data)
    except Exception as e:
        return f"Error: {e}"
    finally:
        if conn: conn.disconnect()

# --- 4. NAVIGATION MENU (SIDEBAR) ---
st.sidebar.title("📌 Menu-ga Guud")
choice = st.sidebar.radio("U gudub:", [
    "🏠 Dashboard", 
    "👥 Maamulka Shaqaalaha", 
    "🔄 Sync Xogta Xarumaha", 
    "💬 WhatsApp Messaging",
    "⚙️ Settings"
])

# --- 5. PAGES LOGIC ---

if choice == "🏠 Dashboard":
    st.title("🏠 Warbixinta Guud")
    # Halkan geli koodhka Dashboard-kaaga (Tirooyinka guud)
    st.write("Ku soo dhawoow nidaamka maamulka shaqaalaha ee Berbera.")

elif choice == "👥 Maamulka Shaqaalaha":
    st.title("👥 Maamulka iyo Wax ka badalka")
    # Halkan geli koodhkii aad horay u haysatay ee Edit/Delete
    st.info("Halkan waxaad ka maamuli kartaa macluumaadka shaqaalaha.")

elif choice == "🔄 Sync Xogta Xarumaha":
    st.title("🔄 Sync Xogta Faraha (ZeroTier)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_office = st.selectbox("Dooro Xarunta:", list(XARUMAHA_IP.keys()))
        if st.button(f"Sync Now: {selected_office}"):
            with st.spinner("Lala xiriirayaa mishiinka..."):
                res = get_attendance_from_machine(XARUMAHA_IP[selected_office])
                if isinstance(res, pd.DataFrame):
                    conn = get_db_connection()
                    res['Xarunta'] = selected_office
                    res.to_sql('attendance_logs', conn, if_exists='append', index=False)
                    conn.close()
                    st.success(f"✅ La soo xiray {len(res)} xogood!")
                else:
                    st.error(res)

    with col2:
        st.subheader("Xogta u dambaysay")
        conn = get_db_connection()
        logs = pd.read_sql("SELECT * FROM attendance_logs ORDER BY Waqtiga DESC LIMIT 10", conn)
        st.table(logs)
        conn.close()

elif choice == "💬 WhatsApp Messaging":
    st.title("💬 Dirista Farriimaha WhatsApp")
    # Halkan geli koodhkii WhatsApp-ka ee PyWhatKit
    st.write("Farriimaha ogeysiinta halkan ka dir.")

elif choice == "⚙️ Settings":
    st.title("⚙️ Settings-ka System-ka")
    st.write("Habaynta nidaamka iyo xiriirka ZeroTier.")