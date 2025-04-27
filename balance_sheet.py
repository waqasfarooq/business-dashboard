import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database

def format_currency(value):
    """Format a value as currency"""
    return f"₹{value:,.2f}"

def show_balance_sheet():
    """Display the balance sheet"""
    st.title("Balance Sheet")
    
    # Date selector
    as_of_date = st.date_input(
        "As of Date",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    
    # Get balance sheet data
    balance_data = database.get_balance_sheet_data(as_of_date.strftime("%Y-%m-%d"))
    
    # Display balance sheet
    st.subheader(f"Balance Sheet as of {as_of_date}")
    
    # Assets section
    st.markdown("### Assets")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Inventory")
        if not balance_data["inventory"].empty:
            inventory_df = balance_data["inventory"].copy()
            inventory_df["value"] = inventory_df["value"].apply(lambda x: format_currency(x))
            inventory_df.columns = ["Item", "Quantity", "Rate", "Value"]
            st.dataframe(inventory_df, use_container_width=True)
        else:
            st.info("No inventory assets")
        st.metric("Total Inventory", format_currency(balance_data["inventory_total"]))
    
    with col2:
        st.markdown("#### Receivables (Due from Parties)")
        if not balance_data["receivables"].empty:
            receivables_df = balance_data["receivables"].copy()
            receivables_df["balance"] = receivables_df["balance"].apply(lambda x: format_currency(x))
            receivables_df.columns = ["Party", "Amount Due"]
            st.dataframe(receivables_df, use_container_width=True)
        else:
            st.info("No receivables")
        st.metric("Total Receivables", format_currency(balance_data["receivables_total"]))
    
    # Total assets
    st.markdown("#### Total Assets")
    st.metric("", format_currency(balance_data["total_assets"]))
    
    # Liabilities and Equity
    st.markdown("### Liabilities and Equity")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Payables (Due to Parties)")
        if not balance_data["payables"].empty:
            payables_df = balance_data["payables"].copy()
            payables_df["balance"] = payables_df["balance"].apply(lambda x: format_currency(x))
            payables_df.columns = ["Party", "Amount Payable"]
            st.dataframe(payables_df, use_container_width=True)
        else:
            st.info("No payables")
        st.metric("Total Payables", format_currency(balance_data["payables_total"]))
    
    with col2:
        st.markdown("#### Equity")
        st.metric("Owner's Equity", format_currency(balance_data["equity"]))
    
    # Total liabilities and equity
    st.markdown("#### Total Liabilities and Equity")
    st.metric("", format_currency(balance_data["total_liabilities"] + balance_data["equity"]))
    
    # Visualization
    st.subheader("Asset Distribution")
    
    # Prepare data for pie chart
    if balance_data["inventory_total"] > 0 or balance_data["receivables_total"] > 0:
        asset_data = pd.DataFrame({
            "Category": ["Inventory", "Receivables"],
            "Value": [balance_data["inventory_total"], balance_data["receivables_total"]]
        })
        
        # Create pie chart
        fig = px.pie(
            asset_data,
            values="Value",
            names="Category",
            title="Asset Distribution",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No assets to display in chart")
    
    # Liabilities and Equity Distribution
    st.subheader("Liabilities and Equity Distribution")
    
    # Prepare data for pie chart
    if balance_data["payables_total"] > 0 or balance_data["equity"] > 0:
        liability_data = pd.DataFrame({
            "Category": ["Payables", "Equity"],
            "Value": [balance_data["payables_total"], balance_data["equity"]]
        })
        
        # Create pie chart
        fig = px.pie(
            liability_data,
            values="Value",
            names="Category",
            title="Liabilities and Equity Distribution",
            color_discrete_sequence=px.colors.sequential.Greens
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No liabilities or equity to display in chart")
