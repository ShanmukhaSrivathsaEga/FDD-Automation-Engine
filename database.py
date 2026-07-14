import pandas as pd
from sqlalchemy import create_engine, inspect
import sqlite3
import os
from datetime import datetime

# ====================================================================
# VAULT A: CLIENT RAW DATA (STRICTLY READ-ONLY FOR ANALYST)
# ====================================================================
DB_NAME_A = "sqlite:///fdd_vault.db"
engine_a = create_engine(DB_NAME_A)

def save_to_vault(table_name, df):
    """Saves a Pandas DataFrame directly to Vault A."""
    try:
        df.to_sql(table_name, con=engine_a, if_exists='replace', index=False)
        return True
    except Exception as e:
        print(f"Vault A Error: {e}")
        return False

def get_from_vault(table_name):
    """Retrieves an SQL table back into a Pandas DataFrame from Vault A."""
    try:
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql(query, con=engine_a)
    except Exception as e:
        print(f"Vault A Retrieval Error: {e}")
        return pd.DataFrame()

def check_vault_contents():
    """Returns a list of all tables currently stored in Vault A."""
    inspector = inspect(engine_a)
    return inspector.get_table_names()

def drop_from_vault(table_name):
    """Safely drops a specific table from Vault A (Data Purge)."""
    conn = sqlite3.connect('fdd_vault.db')
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()


# ====================================================================
# VAULT B: ANALYST WORKPAPERS & EVIDENCE LOGS (THE DUAL-LEDGER)
# ====================================================================
DB_NAME_B = "sqlite:///fdd_workpapers.db"
engine_b = create_engine(DB_NAME_B)

EVIDENCE_DIR = "./evidence_vault"
if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

def save_evidence_file(deal_prefix, uploaded_file):
    """Saves physical evidence securely to the local directory."""
    if uploaded_file is None:
        return None
        
    # Standardize filename to prevent path injection
    safe_name = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._- ")
    file_path = os.path.join(EVIDENCE_DIR, f"{deal_prefix}_{safe_name}")
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return safe_name

def save_analyst_adjustment(deal_prefix, adjustment_dict):
    """Upserts a single analyst adjustment into Vault B."""
    table_name = f"{deal_prefix}_ANALYST_LEDGER"
    
    # Auto-generate immutable timestamp
    adjustment_dict['TIMESTAMP'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load existing ledger to update or append safely
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine_b)
    except Exception:
        df = pd.DataFrame()
        
    new_row = pd.DataFrame([adjustment_dict])
    
    if not df.empty and 'REF_ID' in df.columns:
        # If the analyst is updating an already modified test, drop the old entry first
        df = df[df['REF_ID'] != adjustment_dict['REF_ID']]
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
        
    df.to_sql(table_name, con=engine_b, if_exists='replace', index=False)
    return True

def get_analyst_ledger(deal_prefix):
    """Retrieves the full Analyst Ledger for the active deal."""
    table_name = f"{deal_prefix}_ANALYST_LEDGER"
    try:
        return pd.read_sql(f"SELECT * FROM {table_name}", con=engine_b)
    except Exception:
        return pd.DataFrame()

def remove_analyst_adjustment(deal_prefix, ref_id):
    """Reverts a specific manual adjustment back to the machine baseline."""
    table_name = f"{deal_prefix}_ANALYST_LEDGER"
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine_b)
        df = df[df['REF_ID'] != ref_id]
        df.to_sql(table_name, con=engine_b, if_exists='replace', index=False)
    except Exception:
        pass

def purge_vault_b(deal_prefix):
    """Wipes all analyst adjustments for a specific deal (Nuclear Reset)."""
    conn = sqlite3.connect('fdd_workpapers.db')
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {deal_prefix}_ANALYST_LEDGER")
    conn.commit()
    conn.close()