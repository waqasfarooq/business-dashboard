import streamlit as st
import pandas as pd
from datetime import datetime
import database

def show_item_management():
    """Display the item management page"""
    st.title("Item Management")
    
    # Get all items
    conn = database.get_connection()
    items_query = """
    SELECT i.*, inv.quantity as current_stock
    FROM items i
    LEFT JOIN inventory inv ON i.id = inv.item_id
    ORDER BY i.name
    """
    items = pd.read_sql_query(items_query, conn)
    conn.close()
    
    # Create tabs for Add Item and View/Edit Items
    tab1, tab2 = st.tabs(["Add New Item", "View/Edit Items"])
    
    # Add New Item tab
    with tab1:
        st.subheader("Add New Item")
        
        with st.form("add_item_form"):
            name = st.text_input("Item Name*")
            description = st.text_area("Description")
            unit = st.text_input("Unit of Measurement (e.g., kg, pcs, etc.)*")
            
            submit_button = st.form_submit_button("Add Item")
        
        if submit_button:
            if not name:
                st.error("Item name is required")
            elif not unit:
                st.error("Unit of measurement is required")
            else:
                success, message = database.add_item(name, description, unit)
                
                if success:
                    st.success(message)
                    # Refresh the item list
                    conn = database.get_connection()
                    items = pd.read_sql_query(items_query, conn)
                    conn.close()
                else:
                    st.error(message)
    
    # View/Edit Items tab
    with tab2:
        st.subheader("All Items")
        
        if items.empty:
            st.info("No items found. Add an item using the 'Add New Item' tab.")
        else:
            # Rename columns for display
            display_df = items.copy()
            display_df.columns = ["ID", "Name", "Description", "Unit", "Created At", "Current Stock"]
            
            # Display the dataframe
            selected_row_index = None
            with st.container():
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Current Stock": st.column_config.NumberColumn(format="%.2f")
                    }
                )
                
                # Selection mechanism
                col1, col2 = st.columns([1, 3])
                with col1:
                    item_id = st.number_input("Select Item ID to Edit", 
                                          min_value=int(display_df["ID"].min()) if not display_df.empty else 1,
                                          max_value=int(display_df["ID"].max()) if not display_df.empty else 100,
                                          step=1)
            
            # Check if an ID is selected for editing
            if item_id:
                st.subheader("Edit Item")
                
                # Get the selected item details
                item_details = database.get_item_details(item_id)
                
                if item_details is not None:
                    with st.form("edit_item_form"):
                        name = st.text_input("Item Name*", value=item_details["name"])
                        description = st.text_area("Description", value=item_details["description"] if item_details["description"] else "")
                        unit = st.text_input("Unit of Measurement", value=item_details["unit"])
                        
                        update_button = st.form_submit_button("Update Item")
                    
                    if update_button:
                        if not name:
                            st.error("Item name is required")
                        elif not unit:
                            st.error("Unit of measurement is required")
                        else:
                            success, message = database.update_item(item_id, name, description, unit)
                            
                            if success:
                                st.success(message)
                                # Refresh the page to show updated data
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.error(f"No item found with ID {item_id}")