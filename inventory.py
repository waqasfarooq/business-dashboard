import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database

def show_inventory_management():
    """Display the inventory management page"""
    st.title("Inventory Management")
    
    # Get current inventory status
    inventory_data = database.get_inventory_status()
    
    if inventory_data.empty:
        st.warning("No inventory data found. Please add items and transactions first.")
        return
    
    # Display inventory summary
    st.subheader("Inventory Summary")
    
    # Calculate total inventory value
    total_value = (inventory_data['quantity'] * inventory_data['avg_rate']).sum()
    
    st.metric("Total Inventory Value", f"₹{total_value:,.2f}")
    
    # Display inventory data
    st.subheader("Current Stock Levels")
    
    # Create a copy for display
    display_df = inventory_data.copy()
    
    # Rename columns
    display_df.columns = ["ID", "Item", "Unit", "Quantity", "Average Rate", "Value"]
    
    # Format the value column
    display_df["Value"] = display_df["Value"].apply(lambda x: f"Rs. {x:,.2f}")
    
    # Display as interactive table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        column_config={
            "Quantity": st.column_config.NumberColumn(format="%.2f"),
            "Average Rate": st.column_config.NumberColumn(format="Rs. %.2f")
        }
    )
    
    # Create inventory visualization
    if len(inventory_data) > 0:
        st.subheader("Inventory Visualization")
        
        # Create bar chart for quantities
        fig = px.bar(
            inventory_data,
            x='item_name',
            y='quantity',
            title="Current Stock by Item",
            labels={'item_name': 'Item', 'quantity': 'Quantity'},
            color='value',
            color_continuous_scale='Viridis',
            text_auto=True
        )
        
        fig.update_layout(
            xaxis_title="Item",
            yaxis_title="Quantity",
            coloraxis_colorbar_title="Value (Rs.)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create pie chart for inventory value distribution
        fig_pie = px.pie(
            inventory_data,
            names='item_name',
            values='value',
            title="Inventory Value Distribution",
            hole=0.4
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Add stock update section
    st.subheader("Update Stock Quantity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        item_id = st.selectbox(
            "Select Item",
            options=inventory_data['item_id'].tolist(),
            format_func=lambda x: inventory_data.loc[inventory_data['item_id'] == x, 'item_name'].iloc[0]
        )
    
    with col2:
        current_qty = inventory_data.loc[inventory_data['item_id'] == item_id, 'quantity'].iloc[0]
        new_qty = st.number_input(
            f"New Quantity (Current: {current_qty})",
            min_value=0.0,
            value=float(current_qty),
            step=0.01
        )
    
    update_button = st.button("Update Stock")
    
    if update_button:
        if new_qty == current_qty:
            st.info("No change in quantity")
        else:
            success, message = database.update_inventory(item_id, new_qty)
            
            if success:
                st.success(message)
                # Refresh the page
                st.rerun()
            else:
                st.error(message)