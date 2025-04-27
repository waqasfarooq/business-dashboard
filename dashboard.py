import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database
from datetime import datetime, timedelta

def format_currency(value):
    """Format a value as currency"""
    return f"₹{value:,.2f}"

def show_dashboard():
    """Display the dashboard with widgets and charts"""
    st.title("Business Dashboard")
    
    # Get dashboard data
    dashboard_data = database.get_dashboard_data()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Parties", dashboard_data["parties_count"])
    
    with col2:
        st.metric("Total Items", dashboard_data["items_count"])
    
    with col3:
        st.metric("Total Transactions", dashboard_data["transactions_count"])
    
    with col4:
        st.metric("Inventory Value", format_currency(dashboard_data["total_inventory_value"]))
    
    # Row for charts
    st.subheader("Analytics")
    
    # Monthly transactions chart
    if not dashboard_data["monthly_transactions"].empty:
        monthly_fig = go.Figure()
        monthly_fig.add_trace(go.Bar(
            x=dashboard_data["monthly_transactions"]["month"],
            y=dashboard_data["monthly_transactions"]["incoming"],
            name="Incoming",
            marker_color='green'
        ))
        monthly_fig.add_trace(go.Bar(
            x=dashboard_data["monthly_transactions"]["month"],
            y=dashboard_data["monthly_transactions"]["outgoing"],
            name="Outgoing",
            marker_color='red'
        ))
        monthly_fig.update_layout(
            title="Monthly Transactions (Last 6 Months)",
            xaxis_title="Month",
            yaxis_title="Amount (₹)",
            barmode='group',
            height=400
        )
        st.plotly_chart(monthly_fig, use_container_width=True)
    else:
        st.info("No transaction data available for chart")
    
    # Two charts side by side
    col1, col2 = st.columns(2)
    
    # Top items chart
    with col1:
        if not dashboard_data["top_items"].empty:
            items_fig = px.bar(
                dashboard_data["top_items"],
                x="item_name",
                y="total_value",
                title="Top 5 Items by Value",
                labels={"item_name": "Item", "total_value": "Total Value (₹)"},
                color_discrete_sequence=['#1f77b4']
            )
            items_fig.update_layout(height=350)
            st.plotly_chart(items_fig, use_container_width=True)
        else:
            st.info("No item data available for chart")
    
    # Top parties chart
    with col2:
        if not dashboard_data["top_parties"].empty:
            parties_fig = px.bar(
                dashboard_data["top_parties"],
                x="party_name",
                y="total_value",
                title="Top 5 Parties by Value",
                labels={"party_name": "Party", "total_value": "Total Value (₹)"},
                color_discrete_sequence=['#2ca02c']
            )
            parties_fig.update_layout(height=350)
            st.plotly_chart(parties_fig, use_container_width=True)
        else:
            st.info("No party data available for chart")
    
    # Two more charts side by side
    col1, col2 = st.columns(2)
    
    # Transaction types pie chart
    with col1:
        if not dashboard_data["transaction_types"].empty:
            types_fig = px.pie(
                dashboard_data["transaction_types"],
                values="count",
                names="transaction_type",
                title="Transaction Types Distribution",
                color_discrete_sequence=px.colors.sequential.Blugrn
            )
            types_fig.update_layout(height=350)
            st.plotly_chart(types_fig, use_container_width=True)
        else:
            st.info("No transaction type data available for chart")
    
    # Low stock items chart
    with col2:
        if not dashboard_data["low_stock_items"].empty:
            stock_fig = px.bar(
                dashboard_data["low_stock_items"],
                x="item_name",
                y="quantity",
                title="Items with Low Stock",
                labels={"item_name": "Item", "quantity": "Quantity"},
                color_discrete_sequence=['#d62728']
            )
            stock_fig.update_layout(height=350)
            st.plotly_chart(stock_fig, use_container_width=True)
        else:
            st.info("All items have sufficient stock")
    
    # Recent transactions
    st.subheader("Recent Transactions")
    
    if not dashboard_data["recent_transactions"].empty:
        # Format the dataframe for display
        display_df = dashboard_data["recent_transactions"].copy()
        display_df["amount"] = display_df["amount"].apply(lambda x: format_currency(x))
        display_df["transaction_type"] = display_df["transaction_type"].apply(
            lambda x: "⬆️ " + x.capitalize() if x == "incoming" else "⬇️ " + x.capitalize()
        )
        
        # Rename columns for better display
        display_df.columns = ["Date", "Party", "Item", "Quantity", "Rate", "Amount", "Type"]
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No recent transactions to display")
