import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# 1. SETUP DATABASE
def init_db():
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS shaqalaha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            magaca TEXT,
            xafiiska TEXT,
            sababta TEXT,
            waqtiga_bixida TEXT,
            waqtiga_soo_labashada TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Functions
def add_data(magaca, xafiiska, sababta, bixid, soo_labo, status):
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('INSERT INTO shaqalaha (magaca, xafiiska, sababta, waqtiga_bixida, waqtiga_soo_labashada, status) VALUES (?,?,?,?,?,?)',
              (magaca, xafiiska, sababta, bixid, soo_labo, status))
    conn.commit()
    conn.close()

def update_status(id_number):
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('UPDATE shaqalaha SET status="Wuu soo Laabtay" WHERE id=?', (id_number,))
    conn.commit()
    conn.close()

# Interface
st.set_page_config(page_title="Maamulka Shaqaalaha", layout="wide")

st.sidebar.title("🛠 Menu-ga")
menu = ["🏠 Dashboard", "📝 Diiwaangeli Maqnaanshaha", "🔍 Raadi & Maamul"]
choice = st.sidebar.selectbox("Dooro Qaybta", menu)

# DB Connection for views
conn = sqlite3.connect('xafiis.db')
df = pd.read_sql_query("SELECT * FROM shaqalaha", conn)
conn.close()

if choice == "🏠 Dashboard":
    st.title("📊 Dulmarka Guud ee Xafiiska")
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Wadar Guud", len(df))
        col2.metric("Hadda Maqan 🔴", len(df[df['status'] == 'Maqan']))
        col3.metric("Soo Laabtay ✅", len(df[df['status'] == 'Wuu soo Laabtay']))
        
        st.write("### Xogta Shaqaalaha")
        st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)

        # --- QAYBTA EXCEL DOWNLOAD ---
        st.divider()
        st.subheader("📥 Soo Deji Warbixinta")
        
        # U beddel xogta Excel (Buffer)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Shaqaalaha')
            
        st.download_button(
            label="Ka soo deji Excel ahaan (Download Excel)",
            data=buffer.getvalue(),
            file_name=f"warbixinta_shaqaalaha_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("Weli wax xog ah laguma darin.")

elif choice == "📝 Diiwaangeli Maqnaanshaha":
    st.title("📝 Diiwaangeli Shaqada Dibadda")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            magaca = st.text_input("Magaca Shaqaalaha")
            xafiiska = st.selectbox("Xafiiska", ["IT Department", "HR", "Finance", "Administration", "Logistics"])
            sababta = st.text_area("Sababta uu u baxayo")
        with col2:
            bixid = st.text_input("Waqtiga Bixidda", datetime.now().strftime("%I:%M %p"))
            soo_labo = st.text_input("Waqtiga soo Labashada", "02:00 PM")
            status = st.selectbox("Status-ka", ["Maqan", "Wuu soo Laabtay"])
        if st.form_submit_button("Keydi Macluumaadka"):
            if magaca:
                add_data(magaca, xafiiska, sababta, bixid, soo_labo, status)
                st.success(f"Xogta {magaca} waa la keydiyey!")
                st.rerun()

elif choice == "🔍 Raadi & Maamul":
    st.title("🔍 Raadi xogta shaqaalaha")
    search_term = st.text_input("Ku raadi Magac ama Xafiis:")
    if search_term:
        result_df = df[df['magaca'].str.contains(search_term, case=False) | df['xafiiska'].str.contains(search_term, case=False)]
        st.dataframe(result_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
        
    st.divider()
    st.subheader("Cusboonaysii Status-ka")
    id_to_update = st.number_input("Geli ID-ga qofka soo laabtay", min_value=1, step=1)
    if st.button("U beddel: Wuu soo Laabtay"):
        update_status(id_to_update)
        st.rerun()