import streamlit as st
import pandas as pd
from datetime import datetime
import database

def show_gatebook_entry():
    """Display the gatebook entry form for adding transactions"""
    st.title("Gatebook Entry")
    
    # Get parties and items for dropdowns
    parties = database.get_all_parties()
    items = database.get_all_items()
    
    # Check if we have parties and items
    if parties.empty:
        st.warning("No parties found. Please add a party first.")
        if st.button("Go to Party Management"):
            st.session_state.current_page = "Party Management"
            st.rerun()
        return
    
    if items.empty:
        st.warning("No items found. Please add an item first.")
        if st.button("Go to Item Management"):
            st.session_state.current_page = "Item Management"
            st.rerun()
        return
    
    # Create the form
    with st.form("gatebook_entry_form"):
        st.subheader("Add New Transaction")
        
        # Date selector
        transaction_date = st.date_input(
            "Transaction Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
        
        # Party selector
        party_id = st.selectbox(
            "Select Party",
            options=parties["id"].tolist(),
            format_func=lambda x: parties.loc[parties["id"] == x, "name"].iloc[0]
        )
        
        # Item selector
        item_id = st.selectbox(
            "Select Item",
            options=items["id"].tolist(),
            format_func=lambda x: items.loc[items["id"] == x, "name"].iloc[0]
        )
        
        # Transaction details
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=0.01, step=0.01)
        with col2:
            rate = st.number_input("Rate (Rs.)", min_value=0.01, step=0.01)
        
        # Show calculated amount
        amount = quantity * rate
        st.info(f"Total Amount: Rs. {amount:.2f}")
        
        # Transaction type
        transaction_type = st.radio(
            "Transaction Type",
            ["incoming", "outgoing"],
            format_func=lambda x: "Incoming (Purchase)" if x == "incoming" else "Outgoing (Sale)"
        )
        
        # Description (optional)
        description = st.text_area("Description (Optional)")
        
        # Submit button
        submit_button = st.form_submit_button("Add Transaction")
    
    # Process form submission
    if submit_button:
        # Validate inputs
        if quantity <= 0:
            st.error("Quantity must be greater than zero.")
            return
        
        if rate <= 0:
            st.error("Rate must be greater than zero.")
            return
        
        # Check inventory for outgoing transactions
        if transaction_type == "outgoing":
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
            current_stock = cursor.fetchone()[0]
            conn.close()
            
            if quantity > current_stock:
                st.error(f"Insufficient stock. Available: {current_stock}")
                return
        
        # Add transaction to database
        success, message = database.add_transaction(
            transaction_date.strftime("%Y-%m-%d"),
            party_id,
            item_id,
            quantity,
            rate,
            description,
            transaction_type
        )
        
        if success:
            st.success(message)
            
            # Display transaction details
            st.subheader("Transaction Details")
            
            party_name = parties.loc[parties["id"] == party_id, "name"].iloc[0]
            item_name = items.loc[items["id"] == item_id, "name"].iloc[0]
            
            details = {
                "Date": transaction_date.strftime("%Y-%m-%d"),
                "Party": party_name,
                "Item": item_name,
                "Quantity": f"{quantity}",
                "Rate": f"Rs. {rate:.2f}",
                "Amount": f"Rs. {amount:.2f}",
                "Type": "Incoming (Purchase)" if transaction_type == "incoming" else "Outgoing (Sale)",
                "Description": description or "N/A"
            }
            
            for key, value in details.items():
                st.text(f"{key}: {value}")
        else:
            st.error(message)
    
    # Recent transactions
    st.subheader("Recent Transactions")
    recent_transactions = database.get_transactions()
    
    if not recent_transactions.empty:
        # Format the dataframe for display
        display_df = recent_transactions.copy()
        display_df["amount"] = display_df["amount"].apply(lambda x: f"Rs. {x:.2f}")
        display_df["transaction_type"] = display_df["transaction_type"].apply(
            lambda x: "⬆️ " + x.capitalize() if x == "incoming" else "⬇️ " + x.capitalize()
        )
        
        # Rename columns for better display
        display_df.columns = ["ID", "Date", "Party", "Item", "Quantity", "Unit", "Rate", "Amount", "Description", "Type"]
        
        # Select columns to display
        display_cols = ["Date", "Party", "Item", "Quantity", "Unit", "Amount", "Type"]
        st.dataframe(display_df[display_cols].head(10), use_container_width=True)
    else:
        st.info("No transactions to display")
