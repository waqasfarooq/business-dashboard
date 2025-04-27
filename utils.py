import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

def format_currency(value):
    """Format a value as currency"""
    if pd.isna(value):
        return "₹0.00"
    return f"₹{value:,.2f}"

def format_quantity(value, unit=""):
    """Format a quantity value with optional unit"""
    if pd.isna(value):
        return "0"
    
    formatted = f"{value:,.2f}"
    
    # Remove trailing zeros after decimal
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    
    if unit:
        formatted = f"{formatted} {unit}"
    
    return formatted

def get_date_range_options():
    """Return common date range options"""
    today = datetime.now().date()
    
    return [
        {"label": "Today", "start": today, "end": today},
        {"label": "Yesterday", "start": today - timedelta(days=1), "end": today - timedelta(days=1)},
        {"label": "Last 7 Days", "start": today - timedelta(days=6), "end": today},
        {"label": "Last 30 Days", "start": today - timedelta(days=29), "end": today},
        {"label": "This Month", "start": today.replace(day=1), "end": today},
        {"label": "Last Month", "start": (today.replace(day=1) - timedelta(days=1)).replace(day=1), 
         "end": today.replace(day=1) - timedelta(days=1)},
        {"label": "Custom", "start": None, "end": None}
    ]

def create_or_get_key(key):
    """Create a session state key if it doesn't exist"""
    if key not in st.session_state:
        st.session_state[key] = None
    return st.session_state[key]

def handle_exception(func):
    """Decorator to handle exceptions and display appropriate messages"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    return wrapper
