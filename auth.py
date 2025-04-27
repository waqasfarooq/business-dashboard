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
    st.title("Business Management System - Login")
    
    # Create tabs for Login and Register
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    # Login Tab
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            login_button = st.button("Login")
        
        if login_button:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                # Check credentials
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                user_data = cursor.fetchone()
                conn.close()
                
                if user_data and verify_password(user_data[0], password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    # Register Tab
    with tab2:
        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            register_button = st.button("Register")
        
        if register_button:
            if not new_username or not new_password or not confirm_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Check if username exists
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username = ?", (new_username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    st.error("Username already exists. Please choose a different one.")
                else:
                    # Create new user
                    hashed_password = hash_password(new_password)
                    cursor.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)",
                        (new_username, hashed_password)
                    )
                    conn.commit()
                    conn.close()
                    st.success("Registration successful! You can now login.")
