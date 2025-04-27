import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def show_inventory_management():
    """Display the inventory management page"""
    st.title("Inventory Management")
    
    # Get current inventory status
    inventory_data = database.get_inventory_status()
    
    if inventory_data.empty:
        st.info("No items found in inventory. Please add items first.")
        return
    
    # Display inventory summary
    st.subheader("Inventory Summary")
    
    # Stats
    total_items = len(inventory_data)
    items_in_stock = len(inventory_data[inventory_data["quantity"] > 0])
    zero_stock_items = len(inventory_data[inventory_data["quantity"] == 0])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Items", total_items)
    
    with col2:
        st.metric("Items in Stock", items_in_stock)
    
    with col3:
        st.metric("Items Out of Stock", zero_stock_items)
    
    # Visualization of inventory levels
    if not inventory_data.empty:
        # Filter for items with stock
        stock_data = inventory_data[inventory_data["quantity"] > 0].sort_values(by="quantity", ascending=False)
        
        if not stock_data.empty:
            st.subheader("Current Inventory Levels")
            
            fig = px.bar(
                stock_data.head(10),  # Show top 10 items by quantity
                x="item_name",
                y="quantity",
                labels={"item_name": "Item", "quantity": "Quantity"},
                title="Top 10 Items by Stock Level",
                color="quantity",
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Editable inventory grid
    st.subheader("Update Inventory")
    st.info("Edit the quantity field and click on the 'Update' button to save changes.")
    
    # Create a copy for display
    display_df = inventory_data.copy()
    display_df.columns = ["Item ID", "Item Name", "Description", "Unit", "Current Stock", "Last Updated"]
    
    # Convert quantity to numeric to avoid issues with AgGrid
    display_df["Current Stock"] = pd.to_numeric(display_df["Current Stock"])
    
    # Create editable grid
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(resizable=True, sortable=True)
    gb.configure_column(
        "Current Stock",
        editable=True,
        type=["numericColumn", "numberColumnFilter"],
        cellStyle={"color": "white", "backgroundColor": "#2c7fb8"}
    )
    gb.configure_column("Item ID", hide=True)
    gb.configure_column("Last Updated", hide=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    
    grid_options = gb.build()
    
    # Display the grid
    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        height=500,
        theme="streamlit",
        allow_unsafe_jscode=True,
        update_mode="model"
    )
    
    # Get updated data
    updated_df = grid_response["data"]
    
    # Create a button to save changes
    if st.button("Update Inventory"):
        update_count = 0
        error_count = 0
        
        for _, row in updated_df.iterrows():
            item_id = row["Item ID"]
            new_quantity = row["Current Stock"]
            
            # Ensure quantity is not negative
            if new_quantity < 0:
                st.error(f"Quantity for {row['Item Name']} cannot be negative. Updates for this item were skipped.")
                error_count += 1
                continue
            
            success, message = database.update_inventory(item_id, new_quantity)
            
            if success:
                update_count += 1
            else:
                st.error(f"Error updating {row['Item Name']}: {message}")
                error_count += 1
        
        if update_count > 0:
            st.success(f"Successfully updated {update_count} item(s)")
            
            if error_count > 0:
                st.warning(f"Failed to update {error_count} item(s)")
            
            # Refresh the page to show updated data
            st.rerun()
        elif error_count == 0:
            st.info("No changes were made to inventory")
