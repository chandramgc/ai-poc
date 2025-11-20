"""MCP Tool: run_sql"""
import time
import re
from typing import Dict, Any, List
from .db import db_pool


def is_select_only(query: str) -> bool:
    """Validate that query is SELECT only"""
    # Remove comments and normalize whitespace
    query_clean = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
    query_clean = query_clean.strip().upper()
    
    # Check for dangerous keywords
    dangerous_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE',
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE', 'CALL'
    ]
    
    for keyword in dangerous_keywords:
        if re.search(rf'\b{keyword}\b', query_clean):
            return False
    
    # Must start with SELECT (or WITH for CTEs)
    if not (query_clean.startswith('SELECT') or query_clean.startswith('WITH')):
        return False
    
    return True


async def run_sql(query: str, params: List[Any] = None) -> Dict[str, Any]:
    """
    Execute SQL query on PostgreSQL database.
    
    Args:
        query: SQL query string (SELECT only)
        params: Optional list of query parameters
    
    Returns:
        {
            "rows": [...],
            "rowCount": int,
            "executionTimeMs": float
        }
    
    Raises:
        ValueError: If query is not SELECT only
        Exception: Database execution errors
    """
    if not is_select_only(query):
        raise ValueError("Only SELECT queries are allowed")
    
    start_time = time.time()
    
    try:
        rows = await db_pool.execute_query(query, params or [])
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "rows": rows,
            "rowCount": len(rows),
            "executionTimeMs": round(execution_time, 2)
        }
    
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        raise Exception(f"Query execution failed: {str(e)}")


# MCP Tool Registry
MCP_TOOLS = {
    "tools": [
        {
            "name": "run_sql",
            "description": "Execute a SELECT query on PostgreSQL database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional query parameters for parameterized queries",
                        "items": {},
                        "default": []
                    }
                },
                "required": ["query"]
            }
        }
    ]
}
