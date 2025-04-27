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
    # Navigation sidebar with improved styling
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        
        # Add some space
        st.write("---")
        
        # Define menu items with icons
        menu_items = {
            "Dashboard": "📊",
            "Gatebook Entry": "📝",
            "Ledger": "📒",
            "Party Ledger": "👥",
            "Item Ledger": "📦",
            "Balance Sheet": "💰",
            "Party Management": "🤝",
            "Item Management": "🏷️",
            "Inventory Management": "🗃️"
        }
        
        # Menu section title
        st.markdown("<h3 style='text-align: center; color: #4169E1;'>Navigation Menu</h3>", unsafe_allow_html=True)
        
        # Custom CSS for the menu buttons
        st.markdown("""
        <style>
        div.stButton > button {
            width: 100%;
            background-color: #f0f2f6;
            color: #0e1117;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            padding: 10px;
            margin-bottom: 10px;
            text-align: left;
            transition: background-color 0.3s, border-color 0.3s;
        }
        div.stButton > button:hover {
            background-color: #4169E1;
            color: white;
            border-color: #4169E1;
        }
        div.stButton > button:focus {
            background-color: #4169E1;
            color: white;
            border-color: #4169E1;
            box-shadow: none;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Current page highlighting style
        for page, icon in menu_items.items():
            if page == st.session_state.current_page:
                button_style = f"""
                <style>
                div[data-testid="stButton"] button[kind="secondary"]:nth-of-type({list(menu_items.keys()).index(page) + 1}) {{
                    background-color: #4169E1;
                    color: white;
                    border-color: #4169E1;
                }}
                </style>
                """
                st.markdown(button_style, unsafe_allow_html=True)
        
        # Create a button for each menu item
        for page, icon in menu_items.items():
            if st.button(f"{icon} {page}", key=page):
                st.session_state.current_page = page
                st.rerun()
        
        # Add some space before logout
        st.write("---")
        
        # Styled logout button
        st.markdown("""
        <style>
        div[data-testid="stButton"] button[kind="secondary"]:last-child {
            background-color: #ff4b4b;
            color: white;
            border-color: #ff4b4b;
            font-weight: bold;
        }
        div[data-testid="stButton"] button[kind="secondary"]:last-child:hover {
            background-color: #ff0000;
            border-color: #ff0000;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    # Main content - using session state to determine current page
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        dashboard.show_dashboard()
    
    elif current_page == "Gatebook Entry":
        gatebook.show_gatebook_entry()
    
    elif current_page == "Ledger":
        ledger.show_general_ledger()
    
    elif current_page == "Party Ledger":
        ledger.show_party_ledger()
    
    elif current_page == "Item Ledger":
        ledger.show_item_ledger()
    
    elif current_page == "Balance Sheet":
        balance_sheet.show_balance_sheet()
    
    elif current_page == "Party Management":
        party_management.show_party_management()
    
    elif current_page == "Item Management":
        item_management.show_item_management()
    
    elif current_page == "Inventory Management":
        inventory.show_inventory_management()
