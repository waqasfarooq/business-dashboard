import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

def get_connection():
    """Establish a connection to the SQLite database"""
    return sqlite3.connect('business_management.db')

def initialize_database():
    """Create the database schema if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create default admin user if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Create default admin user with password 'admin123'
        import hashlib
        default_username = "admin"
        default_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (default_username, default_password)
        )
    
    # Create Parties table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        unit TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Inventory table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity REAL DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
    ''')
    
    # Create Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date DATE NOT NULL,
        party_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        rate REAL NOT NULL,
        description TEXT,
        transaction_type TEXT NOT NULL, -- 'incoming' or 'outgoing'
        amount REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (party_id) REFERENCES parties (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
    ''')
    
    # Default admin user is created above
    
    conn.commit()
    conn.close()

def get_all_parties():
    """Retrieve all parties from the database"""
    conn = get_connection()
    query = "SELECT id, name FROM parties ORDER BY name"
    parties = pd.read_sql_query(query, conn)
    conn.close()
    return parties

def get_all_items():
    """Retrieve all items from the database"""
    conn = get_connection()
    query = "SELECT id, name FROM items ORDER BY name"
    items = pd.read_sql_query(query, conn)
    conn.close()
    return items

def get_party_details(party_id):
    """Retrieve party details by ID"""
    conn = get_connection()
    query = "SELECT * FROM parties WHERE id = ?"
    party = pd.read_sql_query(query, conn, params=(party_id,))
    conn.close()
    return party.iloc[0] if not party.empty else None

def get_item_details(item_id):
    """Retrieve item details by ID"""
    conn = get_connection()
    query = "SELECT * FROM items WHERE id = ?"
    item = pd.read_sql_query(query, conn, params=(item_id,))
    conn.close()
    return item.iloc[0] if not item.empty else None

def add_party(name, contact_person, phone, email, address):
    """Add a new party to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO parties (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)",
            (name, contact_person, phone, email, address)
        )
        conn.commit()
        success = True
        message = "Party added successfully"
    except sqlite3.IntegrityError:
        success = False
        message = "Party name already exists"
    finally:
        conn.close()
    
    return success, message

def add_item(name, description, unit):
    """Add a new item to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO items (name, description, unit) VALUES (?, ?, ?)",
            (name, description, unit)
        )
        item_id = cursor.lastrowid
        
        # Initialize inventory entry for the item
        cursor.execute(
            "INSERT INTO inventory (item_id, quantity) VALUES (?, 0)",
            (item_id,)
        )
        
        conn.commit()
        success = True
        message = "Item added successfully"
    except sqlite3.IntegrityError:
        success = False
        message = "Item name already exists"
    finally:
        conn.close()
    
    return success, message

def update_item(item_id, name, description, unit):
    """Update an existing item in the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE items SET name = ?, description = ?, unit = ? WHERE id = ?",
            (name, description, unit, item_id)
        )
        conn.commit()
        success = True
        message = "Item updated successfully"
    except sqlite3.IntegrityError:
        success = False
        message = "Item name already exists"
    finally:
        conn.close()
    
    return success, message

def update_party(party_id, name, contact_person, phone, email, address):
    """Update an existing party in the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE parties SET name = ?, contact_person = ?, phone = ?, email = ?, address = ? WHERE id = ?",
            (name, contact_person, phone, email, address, party_id)
        )
        conn.commit()
        success = True
        message = "Party updated successfully"
    except sqlite3.IntegrityError:
        success = False
        message = "Party name already exists"
    finally:
        conn.close()
    
    return success, message

def add_transaction(transaction_date, party_id, item_id, quantity, rate, description, transaction_type):
    """Add a new transaction to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Calculate amount
        amount = quantity * rate
        
        # Insert transaction
        cursor.execute(
            """INSERT INTO transactions 
            (transaction_date, party_id, item_id, quantity, rate, description, transaction_type, amount) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (transaction_date, party_id, item_id, quantity, rate, description, transaction_type, amount)
        )
        
        # Update inventory
        if transaction_type == "incoming":
            cursor.execute(
                "UPDATE inventory SET quantity = quantity + ?, last_updated = CURRENT_TIMESTAMP WHERE item_id = ?",
                (quantity, item_id)
            )
        else:  # outgoing
            cursor.execute(
                "UPDATE inventory SET quantity = quantity - ?, last_updated = CURRENT_TIMESTAMP WHERE item_id = ?",
                (quantity, item_id)
            )
        
        conn.commit()
        success = True
        message = "Transaction added successfully"
    except Exception as e:
        conn.rollback()
        success = False
        message = f"Error adding transaction: {str(e)}"
    finally:
        conn.close()
    
    return success, message

def update_inventory(item_id, new_quantity):
    """Update inventory quantity for an item"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE inventory SET quantity = ?, last_updated = CURRENT_TIMESTAMP WHERE item_id = ?",
            (new_quantity, item_id)
        )
        conn.commit()
        success = True
        message = "Inventory updated successfully"
    except Exception as e:
        conn.rollback()
        success = False
        message = f"Error updating inventory: {str(e)}"
    finally:
        conn.close()
    
    return success, message

def get_transactions(start_date=None, end_date=None, party_id=None, item_id=None):
    """Retrieve transactions with optional filters"""
    conn = get_connection()
    
    # Base query
    query = """
    SELECT t.id, t.transaction_date, p.name as party_name, i.name as item_name, 
           t.quantity, i.unit, t.rate, t.amount, t.description, t.transaction_type
    FROM transactions t
    JOIN parties p ON t.party_id = p.id
    JOIN items i ON t.item_id = i.id
    WHERE 1=1
    """
    
    params = []
    
    # Add filters
    if start_date:
        query += " AND t.transaction_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND t.transaction_date <= ?"
        params.append(end_date)
    
    if party_id:
        query += " AND t.party_id = ?"
        params.append(party_id)
    
    if item_id:
        query += " AND t.item_id = ?"
        params.append(item_id)
    
    query += " ORDER BY t.transaction_date DESC, t.id DESC"
    
    # Execute query
    transactions = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return transactions

def get_inventory_status():
    """Get current inventory status for all items"""
    conn = get_connection()
    
    # Query to get inventory data with average rate calculation
    query = """
    SELECT i.id as item_id, i.name as item_name, i.unit, 
           COALESCE(inv.quantity, 0) as quantity,
           COALESCE(
               (SELECT AVG(rate) FROM transactions 
                WHERE item_id = i.id AND transaction_type = 'incoming'), 0
           ) as avg_rate,
           COALESCE(
               (SELECT AVG(rate) FROM transactions 
                WHERE item_id = i.id AND transaction_type = 'incoming'), 0
           ) * COALESCE(inv.quantity, 0) as value
    FROM items i
    LEFT JOIN inventory inv ON i.id = inv.item_id
    ORDER BY i.name
    """
    
    inventory_data = pd.read_sql_query(query, conn)
    conn.close()
    
    # Ensure we have all required columns, even if empty
    if 'avg_rate' not in inventory_data.columns:
        inventory_data['avg_rate'] = 0
    
    if 'value' not in inventory_data.columns:
        inventory_data['value'] = inventory_data['quantity'] * inventory_data['avg_rate']
    
    return inventory_data

def get_party_ledger(party_id, start_date=None, end_date=None):
    """Get ledger for a specific party"""
    conn = get_connection()
    
    query = """
    SELECT t.id, t.transaction_date, i.name as item_name, 
           t.quantity, i.unit, t.rate, t.amount, 
           CASE WHEN t.transaction_type = 'incoming' THEN t.amount ELSE 0 END as debit,
           CASE WHEN t.transaction_type = 'outgoing' THEN t.amount ELSE 0 END as credit,
           t.description, t.transaction_type
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    WHERE t.party_id = ?
    """
    
    params = [party_id]
    
    if start_date:
        query += " AND t.transaction_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND t.transaction_date <= ?"
        params.append(end_date)
    
    query += " ORDER BY t.transaction_date, t.id"
    
    ledger_data = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    # Calculate running balance
    if not ledger_data.empty:
        ledger_data['balance'] = (ledger_data['debit'] - ledger_data['credit']).cumsum()
    
    return ledger_data

def get_item_ledger(item_id, start_date=None, end_date=None):
    """Get ledger for a specific item"""
    conn = get_connection()
    
    query = """
    SELECT t.id, t.transaction_date, p.name as party_name, 
           t.quantity, t.rate, t.amount, t.transaction_type,
           CASE WHEN t.transaction_type = 'incoming' THEN t.quantity ELSE 0 END as quantity_in,
           CASE WHEN t.transaction_type = 'outgoing' THEN t.quantity ELSE 0 END as quantity_out,
           t.description
    FROM transactions t
    JOIN parties p ON t.party_id = p.id
    WHERE t.item_id = ?
    """
    
    params = [item_id]
    
    if start_date:
        query += " AND t.transaction_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND t.transaction_date <= ?"
        params.append(end_date)
    
    query += " ORDER BY t.transaction_date, t.id"
    
    ledger_data = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    # Calculate running balance
    if not ledger_data.empty:
        ledger_data['balance'] = (ledger_data['quantity_in'] - ledger_data['quantity_out']).cumsum()
    
    return ledger_data

def get_dashboard_data():
    """Get data for dashboard widgets and charts"""
    conn = get_connection()
    
    # Total number of parties
    parties_count = pd.read_sql_query("SELECT COUNT(*) as count FROM parties", conn).iloc[0]['count']
    
    # Total number of items
    items_count = pd.read_sql_query("SELECT COUNT(*) as count FROM items", conn).iloc[0]['count']
    
    # Total transactions
    transactions_count = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions", conn).iloc[0]['count']
    
    # Total inventory value
    inventory_value_query = """
    SELECT SUM(inv.quantity * t.rate) as total_value
    FROM inventory inv
    JOIN items i ON inv.item_id = i.id
    LEFT JOIN (
        SELECT item_id, rate, ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY transaction_date DESC) as rn
        FROM transactions
        WHERE transaction_type = 'incoming'
    ) t ON inv.item_id = t.item_id AND t.rn = 1
    """
    inventory_value = pd.read_sql_query(inventory_value_query, conn)
    total_inventory_value = inventory_value.iloc[0]['total_value']
    if pd.isna(total_inventory_value):
        total_inventory_value = 0
    
    # Recent transactions
    recent_transactions = pd.read_sql_query("""
    SELECT t.transaction_date, p.name as party_name, i.name as item_name, 
           t.quantity, t.rate, t.amount, t.transaction_type
    FROM transactions t
    JOIN parties p ON t.party_id = p.id
    JOIN items i ON t.item_id = i.id
    ORDER BY t.id DESC LIMIT 5
    """, conn)
    
    # Transactions by month (for chart)
    monthly_transactions = pd.read_sql_query("""
    SELECT 
        strftime('%Y-%m', transaction_date) as month,
        SUM(CASE WHEN transaction_type = 'incoming' THEN amount ELSE 0 END) as incoming,
        SUM(CASE WHEN transaction_type = 'outgoing' THEN amount ELSE 0 END) as outgoing
    FROM transactions
    WHERE transaction_date >= date('now', '-6 months')
    GROUP BY strftime('%Y-%m', transaction_date)
    ORDER BY month
    """, conn)
    
    # Top 5 items by transaction value
    top_items = pd.read_sql_query("""
    SELECT i.name as item_name, SUM(t.amount) as total_value
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    GROUP BY t.item_id
    ORDER BY total_value DESC
    LIMIT 5
    """, conn)
    
    # Top 5 parties by transaction value
    top_parties = pd.read_sql_query("""
    SELECT p.name as party_name, SUM(t.amount) as total_value
    FROM transactions t
    JOIN parties p ON t.party_id = p.id
    GROUP BY t.party_id
    ORDER BY total_value DESC
    LIMIT 5
    """, conn)
    
    # Transaction types distribution
    transaction_types = pd.read_sql_query("""
    SELECT transaction_type, COUNT(*) as count
    FROM transactions
    GROUP BY transaction_type
    """, conn)
    
    # Inventory status (for items with low stock)
    low_stock_items = pd.read_sql_query("""
    SELECT i.name as item_name, inv.quantity
    FROM inventory inv
    JOIN items i ON inv.item_id = i.id
    WHERE inv.quantity < 10
    ORDER BY inv.quantity
    LIMIT 5
    """, conn)
    
    conn.close()
    
    return {
        "parties_count": parties_count,
        "items_count": items_count,
        "transactions_count": transactions_count,
        "total_inventory_value": total_inventory_value,
        "recent_transactions": recent_transactions,
        "monthly_transactions": monthly_transactions,
        "top_items": top_items,
        "top_parties": top_parties,
        "transaction_types": transaction_types,
        "low_stock_items": low_stock_items
    }

def get_balance_sheet_data(as_of_date=None):
    """Get data for balance sheet"""
    if not as_of_date:
        as_of_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    
    # Assets (Inventory + Receivables)
    inventory_query = """
    SELECT i.name as item_name, inv.quantity, 
           COALESCE((SELECT rate FROM transactions WHERE item_id = i.id AND transaction_type = 'incoming' ORDER BY transaction_date DESC LIMIT 1), 0) as rate,
           inv.quantity * COALESCE((SELECT rate FROM transactions WHERE item_id = i.id AND transaction_type = 'incoming' ORDER BY transaction_date DESC LIMIT 1), 0) as value
    FROM inventory inv
    JOIN items i ON inv.item_id = i.id
    WHERE inv.quantity > 0
    """
    inventory = pd.read_sql_query(inventory_query, conn)
    
    receivables_query = """
    SELECT p.name as party_name, 
           SUM(CASE WHEN t.transaction_type = 'outgoing' THEN t.amount ELSE -t.amount END) as balance
    FROM transactions t
    JOIN parties p ON t.party_id = p.id
    WHERE t.transaction_date <= ?
    GROUP BY t.party_id
    HAVING balance > 0
    """
    receivables = pd.read_sql_query(receivables_query, conn, params=[as_of_date])
    
    # Liabilities (Payables)
    payables_query = """
    SELECT p.name as party_name, 
           SUM(CASE WHEN t.transaction_type = 'incoming' THEN t.amount ELSE -t.amount END) as balance
    FROM transactions t
    JOIN parties p ON t.party_id = p.id
    WHERE t.transaction_date <= ?
    GROUP BY t.party_id
    HAVING balance > 0
    """
    payables = pd.read_sql_query(payables_query, conn, params=[as_of_date])
    
    conn.close()
    
    # Calculate totals
    inventory_total = inventory['value'].sum() if not inventory.empty else 0
    receivables_total = receivables['balance'].sum() if not receivables.empty else 0
    payables_total = payables['balance'].sum() if not payables.empty else 0
    
    # Calculate equity (Assets - Liabilities)
    total_assets = inventory_total + receivables_total
    total_liabilities = payables_total
    equity = total_assets - total_liabilities
    
    return {
        "inventory": inventory,
        "inventory_total": inventory_total,
        "receivables": receivables,
        "receivables_total": receivables_total,
        "payables": payables,
        "payables_total": payables_total,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "equity": equity,
        "as_of_date": as_of_date
    }
