import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import database


def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_password, provided_password):
    """Verify a stored password against a provided password"""
    return stored_password == hash_password(provided_password)


def show_login_page():
    """Display login page with registration option"""
    # Custom CSS for the login page
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        background-color: #f0f2f6;
        color: #4169E1;
        font-weight: 600;
        border-left: 1px solid #e0e0e0;
        border-right: 1px solid #e0e0e0;
        border-top: 1px solid #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4169E1 !important;
        color: white !important;
    }
    div[data-testid="stForm"] {
        border: 1px solid #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button {
        width: 100%;
        background-color: #4169E1;
        color: white;
        border-radius: 5px;
        border: 1px solid #4169E1;
        padding: 10px 15px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #3151b5;
        border-color: #3151b5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create an attractive header with icon and better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #4169E1;">📊 Business Management System</h1>
            <p style="font-size: 18px; color: #555;">Please log in to access your account</p>
        </div>
        """, unsafe_allow_html=True)

    # Create tabs for Login and Register
    tab1, tab2 = st.tabs(["🔑 Login", "✨ Register New Account"])

    # Login Tab
    with tab1:
        with st.form(key="login_form"):
            st.markdown("<h3 style='text-align: center; color: #333;'>Account Login</h3>", unsafe_allow_html=True)
            
            username = st.text_input("👤 Username", key="login_username")
            password = st.text_input("🔒 Password", type="password", key="login_password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_button = st.form_submit_button("Login")
            
            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    # Create a loading animation
                    with st.spinner("Authenticating..."):
                        # Check credentials
                        conn = database.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT password FROM users WHERE username = ?", (username, ))
                        user_data = cursor.fetchone()
                        conn.close()

                        if user_data and verify_password(user_data[0], password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")

        # Display a note about default login
        st.markdown("""
        <div style="text-align: center; padding-top: 20px; color: #666; font-size: 14px;">
            Default login: Username <b>admin</b> with password <b>admin123</b>
        </div>
        """, unsafe_allow_html=True)

    # Register Tab
    with tab2:
        with st.form(key="register_form"):
            st.markdown("<h3 style='text-align: center; color: #333;'>Create New Account</h3>", unsafe_allow_html=True)
            
            new_username = st.text_input("👤 Choose Username", key="register_username")
            
            # Password field with strength meter
            new_password = st.text_input("🔒 Choose Password", type="password", key="register_password")
            
            # Simple password strength indicator
            if new_password:
                strength = min(len(new_password) * 10, 100)
                color = "red" if strength < 40 else "orange" if strength < 70 else "green"
                st.markdown(f"""
                <div style="margin-bottom: 20px;">
                    <div style="height: 5px; width: {strength}%; background-color: {color}; border-radius: 5px;"></div>
                    <p style="color: {color}; font-size: 12px; margin-top: 5px;">
                        {"Weak" if strength < 40 else "Medium" if strength < 70 else "Strong"} password
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            confirm_password = st.text_input("🔄 Confirm Password", type="password", key="confirm_password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                register_button = st.form_submit_button("Register")
            
            if register_button:
                if not new_username or not new_password or not confirm_password:
                    st.error("Please fill in all fields")
                elif len(new_password) < 6:
                    st.error("Password should be at least 6 characters long")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Create a loading animation
                    with st.spinner("Creating account..."):
                        # Check if username exists
                        conn = database.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT username FROM users WHERE username = ?", (new_username, ))
                        existing_user = cursor.fetchone()

                        if existing_user:
                            st.error("Username already exists. Please choose a different one.")
                        else:
                            # Create new user
                            hashed_password = hash_password(new_password)
                            cursor.execute(
                                "INSERT INTO users (username, password) VALUES (?, ?)",
                                (new_username, hashed_password))
                            conn.commit()
                            conn.close()
                            st.success("Registration successful! You can now login.")
        
        # Display terms and privacy note
        st.markdown("""
        <div style="text-align: center; padding-top: 20px; color: #666; font-size: 14px;">
            By registering, you agree to our Terms of Service and Privacy Policy
        </div>
        """, unsafe_allow_html=True)
