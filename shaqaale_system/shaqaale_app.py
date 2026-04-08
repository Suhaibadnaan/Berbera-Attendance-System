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
            status TEXT,
            taariikh DATE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- SECURITY: LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("Gali Aqoonsigaaga")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        if username == "admin" and password == "Berbera2026":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Username ama Password-ka waa khalad!")

if not st.session_state['logged_in']:
    login()
    st.stop()

# Functions
def add_data(magaca, xafiiska, sababta, bixid, soo_labo, status):
    taariikh = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('INSERT INTO shaqalaha (magaca, xafiiska, sababta, waqtiga_bixida, waqtiga_soo_labashada, status, taariikh) VALUES (?,?,?,?,?,?,?)',
              (magaca, xafiiska, sababta, bixid, soo_labo, status, taariikh))
    conn.commit()
    conn.close()

def delete_data(id_number):
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('DELETE FROM shaqalaha WHERE id=?', (id_number,))
    conn.commit()
    conn.close()

def edit_data(id_number, magaca, xafiiska, sababta, bixid, soo_labo, status):
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('''UPDATE shaqalaha SET magaca=?, xafiiska=?, sababta=?, waqtiga_bixida=?, waqtiga_soo_labashada=?, status=? WHERE id=?''', 
              (magaca, xafiiska, sababta, bixid, soo_labo, status, id_number))
    conn.commit()
    conn.close()

# Interface
st.set_page_config(page_title="Maamulka Shaqaalaha", layout="wide")

st.sidebar.title("Menu-ga")
menu = ["Dashboard", "Diiwaangeli Maqnaanshaha", "Raadi iyo Maamul"]
choice = st.sidebar.selectbox("Dooro Qaybta", menu)

conn = sqlite3.connect('xafiis.db')
df = pd.read_sql_query("SELECT * FROM shaqalaha", conn)
conn.close()

if choice == "Dashboard":
    st.title("Dulmarka Guud ee Xafiiska")
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Wadar Guud", len(df))
        col2.metric("Hadda Maqan", len(df[df['status'] == 'Maqan']))
        col3.metric("Soo Laabtay", len(df[df['status'] == 'Wuu soo Laabtay']))
        
        st.write("### Garaafka Shaqada")
        st.bar_chart(df['xafiiska'].value_counts())
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Weli xog laguma darin.")

elif choice == "Diiwaangeli Maqnaanshaha":
    st.title("Diiwaangeli Shaqada Dibadda")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            magaca = st.text_input("Magaca Shaqaalaha")
            xafiiska = st.selectbox("Xafiiska", ["IT Department", "HR", "Finance", "Administration", "Logistics"])
        with col2:
            sababta = st.text_input("Sababta")
            bixid = st.text_input("Waqtiga Bixidda", datetime.now().strftime("%I:%M %p"))
            soo_labo = st.text_input("Waqtiga soo Labashada", "02:00 PM")
        
        if st.form_submit_button("Keydi"):
            add_data(magaca, xafiiska, sababta, bixid, soo_labo, "Maqan")
            st.success("Waa la keydiyey!")
            st.rerun()

elif choice == "Raadi iyo Maamul":
    st.title("Maamulka iyo Tirtirista")
    
    # Date filter
    start_date = st.date_input("Laga bilaabo")
    search_df = df[pd.to_datetime(df['taariikh']) >= pd.Timestamp(start_date)]
    
    st.dataframe(search_df, use_container_width=True)
    
    edit_id = st.number_input("ID-ga wax ka beddel", step=1)
    if st.button("Tirtir"):
        delete_data(edit_id)
        st.rerun()