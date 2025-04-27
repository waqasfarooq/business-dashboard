import streamlit as st
import pandas as pd
from datetime import datetime
import database
from st_aggrid import AgGrid, GridOptionsBuilder

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
            # Create the aggrid
            gb = GridOptionsBuilder.from_dataframe(items)
            gb.configure_default_column(resizable=True, filterable=True, sortable=True)
            gb.configure_selection(selection_mode="single", use_checkbox=False)
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
            grid_options = gb.build()
            
            # Rename columns for display
            display_df = items.copy()
            display_df.columns = ["ID", "Name", "Description", "Unit", "Created At", "Current Stock"]
            
            # Display the grid
            grid_response = AgGrid(
                display_df,
                gridOptions=grid_options,
                height=400,
                theme="streamlit",
                allow_unsafe_jscode=True,
                update_mode="selection_changed"
            )
            
            # Check if a row is selected for editing
            selected_row = grid_response["selected_rows"]
            
            if selected_row:
                st.subheader("Edit Item")
                item_id = selected_row[0]["ID"]
                
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
