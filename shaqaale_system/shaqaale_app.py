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

def delete_data(id_number):
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('DELETE FROM shaqalaha WHERE id=?', (id_number,))
    conn.commit()
    conn.close()

def edit_data(id_number, magaca, xafiiska, sababta, bixid, soo_labo, status):
    conn = sqlite3.connect('xafiis.db')
    c = conn.cursor()
    c.execute('''UPDATE shaqalaha 
                 SET magaca=?, xafiiska=?, sababta=?, waqtiga_bixida=?, waqtiga_soo_labashada=?, status=? 
                 WHERE id=?''', (magaca, xafiiska, sababta, bixid, soo_labo, status, id_number))
    conn.commit()
    conn.close()

# Interface
st.set_page_config(page_title="Maamulka Shaqaalaha", layout="wide")

st.sidebar.title("Menu-ga")
menu = ["Dashboard", "Diiwaangeli Maqnaanshaha", "Raadi iyo Maamul"]
choice = st.sidebar.selectbox("Dooro Qaybta", menu)

# DB Connection for views
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
        
        st.write("### Xogta Shaqaalaha")
        st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)

        st.divider()
        st.subheader("Soo Deji Warbixinta")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Shaqaalaha')
            
        st.download_button(
            label="Download Excel",
            data=buffer.getvalue(),
            file_name=f"warbixinta_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("Weli wax xog ah laguma darin.")

elif choice == "Diiwaangeli Maqnaanshaha":
    st.title("Diiwaangeli Shaqada Dibadda")
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

elif choice == "Raadi iyo Maamul":
    st.title("Maamulka iyo Tirtirista Xogta")
    search_term = st.text_input("Ku raadi Magac ama Xafiis:")
    if search_term:
        display_df = df[df['magaca'].str.contains(search_term, case=False) | df['xafiiska'].str.contains(search_term, case=False)]
    else:
        display_df = df
    st.dataframe(display_df, use_container_width=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Wax ka beddel xogta")
        edit_id = st.number_input("Geli ID-ga qofka aad wax ka beddelayso", min_value=1, step=1, key="edit_id")
        if edit_id in df['id'].values:
            user_data = df[df['id'] == edit_id].iloc[0]
            with st.expander("Furi foomka wax ka beddelka"):
                new_magaca = st.text_input("Magaca", value=user_data['magaca'])
                new_xafiiska = st.selectbox("Xafiiska", ["IT Department", "HR", "Finance", "Administration", "Logistics"], 
                                            index=["IT Department", "HR", "Finance", "Administration", "Logistics"].index(user_data['xafiiska']))
                new_sababta = st.text_area("Sababta", value=user_data['sababta'])
                new_bixid = st.text_input("Bixidda", value=user_data['waqtiga_bixida'])
                new_soo_labo = st.text_input("Soo laabashada", value=user_data['waqtiga_soo_labashada'])
                new_status = st.selectbox("Status", ["Maqan", "Wuu soo Laabtay"], 
                                          index=["Maqan", "Wuu soo Laabtay"].index(user_data['status']))
                if st.button("Update Xogta"):
                    edit_data(edit_id, new_magaca, new_xafiiska, new_sababta, new_bixid, new_soo_labo, new_status)
                    st.success("Xogta waa la cusboonaysiiyey!")
                    st.rerun()

    with col2:
        st.subheader("Tirtir Xogta")
        id_to_delete = st.number_input("Geli ID-ga qofka la tirtirayo", min_value=1, step=1, key="delete_id")
        if st.button("Xogta Tirtir", type="primary"):
            if id_to_delete in df['id'].values:
                delete_data(id_to_delete)
                st.warning("Xogta waa la tirtiray!")
                st.rerun()
            else:
                st.error("ID-gan laguma helin database-ka!")