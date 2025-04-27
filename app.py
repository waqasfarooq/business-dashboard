import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

# Import application modules
import auth
import database
import dashboard
import gatebook
import ledger
import balance_sheet
import party_management
import item_management
import inventory
import utils

# Page configuration
st.set_page_config(
    page_title="Business Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database if it doesn't exist
if not os.path.exists('business_management.db'):
    database.initialize_database()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Login page
if not st.session_state.logged_in:
    auth.show_login_page()
else:
    # Navigation sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        
        st.subheader("Navigation")
        
        selected_page = st.radio(
            "Select a page",
            ["Dashboard", "Gatebook Entry", "Ledger", "Party Ledger", 
             "Item Ledger", "Balance Sheet", "Party Management", 
             "Item Management", "Inventory Management"],
            index=["Dashboard", "Gatebook Entry", "Ledger", "Party Ledger", 
                  "Item Ledger", "Balance Sheet", "Party Management", 
                  "Item Management", "Inventory Management"].index(st.session_state.current_page)
        )
        
        st.session_state.current_page = selected_page
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    # Main content
    if selected_page == "Dashboard":
        dashboard.show_dashboard()
    
    elif selected_page == "Gatebook Entry":
        gatebook.show_gatebook_entry()
    
    elif selected_page == "Ledger":
        ledger.show_general_ledger()
    
    elif selected_page == "Party Ledger":
        ledger.show_party_ledger()
    
    elif selected_page == "Item Ledger":
        ledger.show_item_ledger()
    
    elif selected_page == "Balance Sheet":
        balance_sheet.show_balance_sheet()
    
    elif selected_page == "Party Management":
        party_management.show_party_management()
    
    elif selected_page == "Item Management":
        item_management.show_item_management()
    
    elif selected_page == "Inventory Management":
        inventory.show_inventory_management()
