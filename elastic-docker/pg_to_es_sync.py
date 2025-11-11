#!/usr/bin/env python3
"""
PostgreSQL to Elasticsearch Sync Script

This script loads data from PostgreSQL tables and indexes them into Elasticsearch.
It supports bulk indexing, custom mappings, and incremental updates.
"""

import sys
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from elasticsearch import Elasticsearch, helpers


# =====================================================
# CONFIGURATION
# =====================================================

# PostgreSQL Configuration
PG_CONFIG = {
    'host': 'localhost',
    'port': 6003,
    'database': 'postgres',  # Change to 'langfuse' if needed
    'user': 'postgres',
    'password': 'postgres'  # Update with your actual password
}

# Elasticsearch Configuration
ES_CONFIG = {
    'hosts': ['http://localhost:6015'],
    'request_timeout': 30
}

# Tables to sync (table_name -> index_name mapping)
TABLES_TO_SYNC = {
    # Example: 'users': 'users_index',
    # Example: 'orders': 'orders_index',
    # Add your tables here
}

# Bulk indexing batch size
BATCH_SIZE = 1000

# Primary key field name (used as document ID)
PRIMARY_KEY_FIELD = 'id'


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def serialize_value(value: Any) -> Any:
    """Convert PostgreSQL values to JSON-serializable format."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    elif value is None:
        return None
    return value


def get_pg_connection():
    """Create and return PostgreSQL connection."""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        print(f"✓ Connected to PostgreSQL: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)


def get_es_client():
    """Create and return Elasticsearch client."""
    try:
        es = Elasticsearch(**ES_CONFIG)
        # Test connection by getting cluster info
        info = es.info()
        print(f"✓ Connected to Elasticsearch: {info['version']['number']}")
        return es
    except Exception as e:
        print(f"✗ Failed to connect to Elasticsearch: {e}")
        sys.exit(1)


def list_pg_tables(conn) -> List[str]:
    """List all tables in the PostgreSQL database."""
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        tables = [row[0] for row in cur.fetchall()]
    return tables


def get_table_count(conn, table_name: str) -> int:
    """Get row count for a table."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cur.fetchone()[0]


def get_table_schema(conn, table_name: str) -> List[Dict]:
    """Get column information for a table."""
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (table_name,))
        return cur.fetchall()


def create_es_index(es: Elasticsearch, index_name: str, schema: List[Dict]) -> bool:
    """Create Elasticsearch index with dynamic mapping."""
    if es.indices.exists(index=index_name):
        print(f"  Index '{index_name}' already exists")
        return True
    
    # Basic index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "refresh_interval": "30s"
        },
        "mappings": {
            "properties": {}
        }
    }
    
    # Map PostgreSQL types to Elasticsearch types
    type_mapping = {
        'integer': 'integer',
        'bigint': 'long',
        'smallint': 'short',
        'numeric': 'double',
        'real': 'float',
        'double precision': 'double',
        'boolean': 'boolean',
        'timestamp without time zone': 'date',
        'timestamp with time zone': 'date',
        'date': 'date',
        'text': 'text',
        'character varying': 'text',
        'json': 'object',
        'jsonb': 'object',
        'uuid': 'keyword'
    }
    
    # Generate field mappings
    for col in schema:
        col_name = col['column_name']
        data_type = col['data_type']
        es_type = type_mapping.get(data_type, 'text')
        settings['mappings']['properties'][col_name] = {'type': es_type}
    
    try:
        es.indices.create(index=index_name, body=settings)
        print(f"  ✓ Created index '{index_name}'")
        return True
    except Exception as e:
        print(f"  ✗ Failed to create index '{index_name}': {e}")
        return False


def sync_table_to_es(conn, es: Elasticsearch, table_name: str, index_name: str):
    """Sync all data from a PostgreSQL table to Elasticsearch."""
    print(f"\n📊 Syncing table '{table_name}' -> index '{index_name}'")
    
    # Get table info
    row_count = get_table_count(conn, table_name)
    schema = get_table_schema(conn, table_name)
    
    print(f"  Rows: {row_count:,}")
    print(f"  Columns: {len(schema)}")
    
    if row_count == 0:
        print("  ⚠ Table is empty, skipping")
        return
    
    # Create index if it doesn't exist
    create_es_index(es, index_name, schema)
    
    # Fetch and index data in batches
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {table_name}")
        
        batch = []
        indexed_count = 0
        
        while True:
            rows = cur.fetchmany(BATCH_SIZE)
            if not rows:
                break
            
            # Prepare bulk actions
            for row in rows:
                # Serialize values
                doc = {k: serialize_value(v) for k, v in row.items()}
                
                # Use primary key as document ID if available
                doc_id = doc.get(PRIMARY_KEY_FIELD)
                
                action = {
                    '_index': index_name,
                    '_source': doc
                }
                
                if doc_id:
                    action['_id'] = str(doc_id)
                
                batch.append(action)
            
            # Bulk index
            try:
                success, failed = helpers.bulk(es, batch, raise_on_error=False)
                indexed_count += success
                
                if failed:
                    print(f"  ⚠ Failed to index {len(failed)} documents")
                
                batch = []
                print(f"  Progress: {indexed_count:,}/{row_count:,} ({indexed_count/row_count*100:.1f}%)", end='\r')
                
            except Exception as e:
                print(f"\n  ✗ Bulk indexing error: {e}")
                batch = []
        
        print(f"\n  ✓ Indexed {indexed_count:,} documents")
        
        # Refresh index
        es.indices.refresh(index=index_name)


def list_es_indices(es: Elasticsearch):
    """List all indices in Elasticsearch."""
    indices = es.cat.indices(format='json')
    return sorted([idx['index'] for idx in indices if not idx['index'].startswith('.')])


# =====================================================
# MAIN FUNCTIONS
# =====================================================

def interactive_mode():
    """Interactive mode to select tables and sync."""
    print("\n" + "="*60)
    print("  PostgreSQL to Elasticsearch Sync Tool")
    print("="*60)
    
    # Connect to databases
    pg_conn = get_pg_connection()
    es = get_es_client()
    
    print("\n📋 Available PostgreSQL tables:")
    tables = list_pg_tables(pg_conn)
    
    if not tables:
        print("  No tables found in database")
        return
    
    for idx, table in enumerate(tables, 1):
        count = get_table_count(pg_conn, table)
        print(f"  {idx:2d}. {table:30s} ({count:,} rows)")
    
    print("\n📂 Existing Elasticsearch indices:")
    indices = list_es_indices(es)
    if indices:
        for idx in indices:
            doc_count = es.count(index=idx)['count']
            print(f"  - {idx:30s} ({doc_count:,} docs)")
    else:
        print("  (none)")
    
    print("\n" + "-"*60)
    print("Options:")
    print("  1. Sync specific table")
    print("  2. Sync all tables")
    print("  3. Exit")
    print("-"*60)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        table_num = input(f"Enter table number (1-{len(tables)}): ").strip()
        try:
            table_idx = int(table_num) - 1
            if 0 <= table_idx < len(tables):
                table_name = tables[table_idx]
                index_name = input(f"Enter Elasticsearch index name (default: {table_name}_index): ").strip()
                if not index_name:
                    index_name = f"{table_name}_index"
                
                sync_table_to_es(pg_conn, es, table_name, index_name)
            else:
                print("Invalid table number")
        except ValueError:
            print("Invalid input")
    
    elif choice == '2':
        confirm = input(f"Sync all {len(tables)} tables? (yes/no): ").strip().lower()
        if confirm == 'yes':
            for table_name in tables:
                index_name = f"{table_name}_index"
                try:
                    sync_table_to_es(pg_conn, es, table_name, index_name)
                except Exception as e:
                    print(f"  ✗ Error syncing {table_name}: {e}")
        else:
            print("Cancelled")
    
    elif choice == '3':
        print("Exiting...")
    
    else:
        print("Invalid choice")
    
    pg_conn.close()
    print("\n✓ Done!")


def batch_mode():
    """Batch mode using TABLES_TO_SYNC configuration."""
    if not TABLES_TO_SYNC:
        print("Error: TABLES_TO_SYNC is empty. Configure tables to sync in the script.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("  PostgreSQL to Elasticsearch Sync (Batch Mode)")
    print("="*60)
    
    pg_conn = get_pg_connection()
    es = get_es_client()
    
    for table_name, index_name in TABLES_TO_SYNC.items():
        try:
            sync_table_to_es(pg_conn, es, table_name, index_name)
        except Exception as e:
            print(f"✗ Error syncing {table_name}: {e}")
    
    pg_conn.close()
    print("\n✓ All tables synced!")


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        batch_mode()
    else:
        interactive_mode()
