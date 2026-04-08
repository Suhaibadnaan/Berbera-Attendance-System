# 1. Ku dar Functions-kan cusub meesha functions-ka kale ay ku jiraan
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

# 2. Qaybta Interface-ka ee " Raadi & Maamul" ku beddel koodhkan:
elif choice == "Raadi & Maamul":
    st.title("Maamulka & Tirtirista Xogta")
    
    # Raadinta
    search_term = st.text_input("Ku raadi Magac ama Xafiis:")
    if search_term:
        display_df = df[df['magaca'].str.contains(search_term, case=False) | df['xafiiska'].str.contains(search_term, case=False)]
    else:
        display_df = df
        
    st.dataframe(display_df, use_container_width=True)

    st.divider()
    
    # Labada tiir ee Maamulka
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Wax ka beddel xogta")
        edit_id = st.number_input("Geli ID-ga qofka aad wax ka beddelayso", min_value=1, step=1, key="edit_id")
        
        # Marka ID la geliyo, soo saar xogtii hore si loo beddelo
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
                    st.success(f"ID {edit_id} waa la cusboonaysiiyey!")
                    st.rerun()

    with col2:
        st.subheader("🗑️ Tirtir Xogta")
        id_to_delete = st.number_input("Geli ID-ga qofka la tirtirayo", min_value=1, step=1, key="delete_id")
        
        # Badhanka tirtirista oo leh digniin
        if st.button("Xogta Tirtir", type="primary"):
            if id_to_delete in df['id'].values:
                delete_data(id_to_delete)
                st.warning(f"ID {id_to_delete} waa la tirtiray!")
                st.rerun()
            else:
                st.error("ID-gan laguma helin database-ka!")