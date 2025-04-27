import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database

def format_currency(value):
    """Format a value as currency"""
    return f"₹{value:,.2f}"

def create_ag_grid(df, height=400):
    """Create an AgGrid component with the given dataframe"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        min_column_width=80
    )
    
    # Configure specific columns
    if 'amount' in df.columns:
        gb.configure_column(
            "amount",
            type=["numericColumn", "numberColumnFilter"],
            valueFormatter="data.amount ? '₹' + Number(data.amount).toLocaleString('en-IN', {minimumFractionDigits: 2}) : ''",
            width=120
        )
    
    if 'debit' in df.columns:
        gb.configure_column(
            "debit",
            type=["numericColumn", "numberColumnFilter"],
            valueFormatter="data.debit ? '₹' + Number(data.debit).toLocaleString('en-IN', {minimumFractionDigits: 2}) : ''",
            width=120
        )
    
    if 'credit' in df.columns:
        gb.configure_column(
            "credit",
            type=["numericColumn", "numberColumnFilter"],
            valueFormatter="data.credit ? '₹' + Number(data.credit).toLocaleString('en-IN', {minimumFractionDigits: 2}) : ''",
            width=120
        )
    
    if 'balance' in df.columns:
        gb.configure_column(
            "balance",
            type=["numericColumn", "numberColumnFilter"],
            valueFormatter="data.balance ? '₹' + Number(data.balance).toLocaleString('en-IN', {minimumFractionDigits: 2}) : ''",
            width=120
        )
    
    # Enable pagination for better performance with large datasets
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=15
    )
    
    grid_options = gb.build()
    
    # Display the grid
    return AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        theme="streamlit",
        allow_unsafe_jscode=True,
        update_mode="model",
        fit_columns_on_grid_load=False
    )

def date_filter_ui():
    """Common date filter UI component"""
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=30),
            max_value=datetime.now().date()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            min_value=start_date,
            max_value=datetime.now().date()
        )
    
    return start_date, end_date

def show_general_ledger():
    """Display the general ledger with all transactions"""
    st.title("General Ledger")
    
    # Date filters
    st.subheader("Filter Transactions")
    start_date, end_date = date_filter_ui()
    
    # Get transactions
    transactions = database.get_transactions(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    # Display data
    st.subheader(f"Transactions from {start_date} to {end_date}")
    
    if transactions.empty:
        st.info("No transactions found for the selected period.")
        return
    
    # Display transaction summary
    total_incoming = transactions[transactions['transaction_type'] == 'incoming']['amount'].sum()
    total_outgoing = transactions[transactions['transaction_type'] == 'outgoing']['amount'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Incoming", format_currency(total_incoming))
    
    with col2:
        st.metric("Total Outgoing", format_currency(total_outgoing))
    
    with col3:
        st.metric("Net Amount", format_currency(total_incoming - total_outgoing))
    
    # Prepare data for ag-grid
    display_df = transactions.copy()
    
    # Rename columns for better display
    display_df.columns = ["ID", "Date", "Party", "Item", "Quantity", "Unit", "Rate", "Amount", "Description", "Type"]
    
    # Display the ag-grid
    st.subheader("Transaction Details")
    grid_response = create_ag_grid(display_df, height=500)

def show_party_ledger():
    """Display the ledger for a specific party"""
    st.title("Party Ledger")
    
    # Get parties for dropdown
    parties = database.get_all_parties()
    
    if parties.empty:
        st.warning("No parties found. Please add a party first.")
        return
    
    # Party selector and date filters
    st.subheader("Select Party and Date Range")
    
    party_id = st.selectbox(
        "Select Party",
        options=parties["id"].tolist(),
        format_func=lambda x: parties.loc[parties["id"] == x, "name"].iloc[0]
    )
    
    start_date, end_date = date_filter_ui()
    
    # Get party ledger data
    ledger_data = database.get_party_ledger(
        party_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    # Display party info
    party_name = parties.loc[parties["id"] == party_id, "name"].iloc[0]
    st.subheader(f"Ledger for {party_name}")
    
    if ledger_data.empty:
        st.info(f"No transactions found for {party_name} in the selected period.")
        return
    
    # Summary metrics
    total_debit = ledger_data['debit'].sum()
    total_credit = ledger_data['credit'].sum()
    balance = ledger_data['balance'].iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Debit", format_currency(total_debit))
    
    with col2:
        st.metric("Total Credit", format_currency(total_credit))
    
    with col3:
        st.metric("Current Balance", format_currency(balance))
    
    # Prepare data for ag-grid
    display_df = ledger_data.copy()
    
    # Rename columns for better display
    display_df.columns = ["ID", "Date", "Item", "Quantity", "Unit", "Rate", "Amount", 
                          "Debit", "Credit", "Description", "Type", "Balance"]
    
    # Display columns
    display_cols = ["Date", "Item", "Quantity", "Rate", "Debit", "Credit", "Balance", "Description"]
    
    # Display the ag-grid
    st.subheader("Transaction Details")
    grid_response = create_ag_grid(display_df[display_cols], height=500)

def show_item_ledger():
    """Display the ledger for a specific item"""
    st.title("Item Ledger")
    
    # Get items for dropdown
    items = database.get_all_items()
    
    if items.empty:
        st.warning("No items found. Please add an item first.")
        return
    
    # Item selector and date filters
    st.subheader("Select Item and Date Range")
    
    item_id = st.selectbox(
        "Select Item",
        options=items["id"].tolist(),
        format_func=lambda x: items.loc[items["id"] == x, "name"].iloc[0]
    )
    
    start_date, end_date = date_filter_ui()
    
    # Get item ledger data
    ledger_data = database.get_item_ledger(
        item_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    # Display item info
    item_name = items.loc[items["id"] == item_id, "name"].iloc[0]
    st.subheader(f"Ledger for {item_name}")
    
    if ledger_data.empty:
        st.info(f"No transactions found for {item_name} in the selected period.")
        return
    
    # Summary metrics
    total_in = ledger_data['quantity_in'].sum()
    total_out = ledger_data['quantity_out'].sum()
    current_stock = ledger_data['balance'].iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total In", f"{total_in:,.2f}")
    
    with col2:
        st.metric("Total Out", f"{total_out:,.2f}")
    
    with col3:
        st.metric("Current Stock", f"{current_stock:,.2f}")
    
    # Prepare data for ag-grid
    display_df = ledger_data.copy()
    
    # Rename columns for better display
    display_df.columns = ["ID", "Date", "Party", "Quantity", "Rate", "Amount", "Type",
                          "Quantity In", "Quantity Out", "Description", "Balance"]
    
    # Display columns
    display_cols = ["Date", "Party", "Quantity", "Rate", "Amount", "Quantity In", "Quantity Out", "Balance", "Description"]
    
    # Display the ag-grid
    st.subheader("Transaction Details")
    grid_response = create_ag_grid(display_df[display_cols], height=500)
