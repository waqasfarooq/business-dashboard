import streamlit as st
import pandas as pd
from datetime import datetime
import database
from st_aggrid import AgGrid, GridOptionsBuilder

def show_party_management():
    """Display the party management page"""
    st.title("Party Management")
    
    # Get all parties
    conn = database.get_connection()
    parties_query = "SELECT * FROM parties ORDER BY name"
    parties = pd.read_sql_query(parties_query, conn)
    conn.close()
    
    # Create tabs for Add Party and View/Edit Parties
    tab1, tab2 = st.tabs(["Add New Party", "View/Edit Parties"])
    
    # Add New Party tab
    with tab1:
        st.subheader("Add New Party")
        
        with st.form("add_party_form"):
            name = st.text_input("Party Name*")
            contact_person = st.text_input("Contact Person")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email")
            address = st.text_area("Address")
            
            submit_button = st.form_submit_button("Add Party")
        
        if submit_button:
            if not name:
                st.error("Party name is required")
            else:
                success, message = database.add_party(name, contact_person, phone, email, address)
                
                if success:
                    st.success(message)
                    # Refresh the party list
                    conn = database.get_connection()
                    parties = pd.read_sql_query(parties_query, conn)
                    conn.close()
                else:
                    st.error(message)
    
    # View/Edit Parties tab
    with tab2:
        st.subheader("All Parties")
        
        if parties.empty:
            st.info("No parties found. Add a party using the 'Add New Party' tab.")
        else:
            # Create the aggrid
            gb = GridOptionsBuilder.from_dataframe(parties)
            gb.configure_default_column(resizable=True, filterable=True, sortable=True)
            gb.configure_selection(selection_mode="single", use_checkbox=False)
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
            grid_options = gb.build()
            
            # Rename columns for display
            display_df = parties.copy()
            display_df.columns = ["ID", "Name", "Contact Person", "Phone", "Email", "Address", "Created At"]
            
            # Display the grid
            grid_response = AgGrid(
                display_df,
                gridOptions=grid_options,
                height=400,
                theme="streamlit",
                allow_unsafe_jscode=True,
                update_mode="selection_changed"
            )
            
            # Check if a row is selected for editing
            selected_row = grid_response["selected_rows"]
            
            if selected_row:
                st.subheader("Edit Party")
                party_id = selected_row[0]["ID"]
                
                # Get the selected party details
                party_details = database.get_party_details(party_id)
                
                if party_details is not None:
                    with st.form("edit_party_form"):
                        name = st.text_input("Party Name*", value=party_details["name"])
                        contact_person = st.text_input("Contact Person", value=party_details["contact_person"] if party_details["contact_person"] else "")
                        phone = st.text_input("Phone Number", value=party_details["phone"] if party_details["phone"] else "")
                        email = st.text_input("Email", value=party_details["email"] if party_details["email"] else "")
                        address = st.text_area("Address", value=party_details["address"] if party_details["address"] else "")
                        
                        update_button = st.form_submit_button("Update Party")
                    
                    if update_button:
                        if not name:
                            st.error("Party name is required")
                        else:
                            success, message = database.update_party(party_id, name, contact_person, phone, email, address)
                            
                            if success:
                                st.success(message)
                                # Refresh the page to show updated data
                                st.rerun()
                            else:
                                st.error(message)
