"""FastAPI HTTP Agent - Natural Language to SQL"""
import os
import re
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI
from langfuse import Langfuse
from .ws_client import execute_sql_query


# Configuration
WS_URL = f"ws://{os.getenv('MCP_HOST', 'localhost')}:{os.getenv('WS_PORT', '9001')}/mcp"
WS_API_KEY = os.getenv("WS_API_KEY", "change-me")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Langfuse configuration
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:6005")

# Initialize clients
use_langfuse = bool(LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)

if use_langfuse:
    # Use Langfuse-wrapped OpenAI client for automatic tracking
    openai_client = LangfuseAsyncOpenAI(
        api_key=LLM_API_KEY,
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )
    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )
    print(f"✓ Langfuse observability enabled: {LANGFUSE_HOST}")
else:
    # Standard OpenAI client without tracking
    openai_client = AsyncOpenAI(api_key=LLM_API_KEY)
    langfuse = None
    print("⚠ Langfuse not configured - LLM calls won't be tracked")

# FastAPI app
app = FastAPI(
    title="MCP PostgreSQL AI Agent",
    description="Natural language query interface to PostgreSQL via MCP",
    version="0.1.0"
)


class QueryRequest(BaseModel):
    question: str
    schema_context: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    question: str
    sql_query: str
    result: Dict[str, Any]
    trace_url: Optional[str] = None


def validate_sql(sql: str) -> bool:
    """Ensure SQL is SELECT only"""
    sql_clean = sql.strip().upper()
    dangerous = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
    for keyword in dangerous:
        if re.search(rf'\b{keyword}\b', sql_clean):
            return False
    return sql_clean.startswith('SELECT') or sql_clean.startswith('WITH')


async def nl_to_sql(
    question: str, 
    schema_context: str = "",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_id: Optional[str] = None
) -> str:
    """Convert natural language to SQL using LLM with Langfuse tracking"""
    
    system_prompt = f"""You are a PostgreSQL expert. Convert natural language questions to SQL queries.

Rules:
- Generate ONLY SELECT queries
- Use proper PostgreSQL syntax
- Return ONLY the SQL query, no explanation
- Do not use markdown code blocks
- Limit results to 100 rows by default unless specified

{schema_context}
"""
    
    user_prompt = f"Convert this to SQL: {question}"
    
    try:
        # If using Langfuse, add metadata
        kwargs = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "max_tokens": 500
        }
        
        # Add Langfuse metadata if enabled
        if use_langfuse and trace_id:
            kwargs["trace_id"] = trace_id
            if user_id:
                kwargs["user_id"] = user_id
            if session_id:
                kwargs["session_id"] = session_id
            kwargs["name"] = "nl_to_sql"
            kwargs["metadata"] = {
                "question": question,
                "has_schema_context": bool(schema_context)
            }
        
        response = await openai_client.chat.completions.create(**kwargs)
        
        sql = response.choices[0].message.content.strip()
        
        # Clean up SQL (remove markdown if present)
        sql = re.sub(r'^```sql\s*\n?', '', sql)
        sql = re.sub(r'\n?```$', '', sql)
        sql = sql.strip()
        
        return sql
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "MCP PostgreSQL AI Agent",
        "endpoints": {
            "query": "POST /query",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Natural language query endpoint with Langfuse observability.
    
    Example:
        POST /query
        {
            "question": "show me last 5 users",
            "schema_context": "Table: users (id, name, email, created_at)",
            "user_id": "user-123",
            "session_id": "session-456"
        }
    """
    trace_url = None
    trace = None
    
    try:
        # Create Langfuse trace if enabled
        if use_langfuse and langfuse:
            trace = langfuse.trace(
                name="nl_to_sql_query",
                user_id=request.user_id,
                session_id=request.session_id,
                metadata={
                    "question": request.question,
                    "has_schema_context": bool(request.schema_context)
                },
                tags=["mcp-agent", "postgresql"]
            )
            trace_url = trace.get_trace_url()
        
        # Step 1: Convert NL to SQL using LLM
        if trace:
            span = trace.span(
                name="nl_to_sql_conversion",
                input={"question": request.question, "schema_context": request.schema_context}
            )
        
        sql_query = await nl_to_sql(
            request.question, 
            request.schema_context,
            user_id=request.user_id,
            session_id=request.session_id,
            trace_id=trace.id if trace else None
        )
        
        if trace:
            span.end(output={"sql_query": sql_query})
        
        # Step 2: Validate SQL
        if not validate_sql(sql_query):
            if trace:
                trace.update(
                    level="ERROR",
                    status_message="Generated SQL is not a SELECT query"
                )
            raise HTTPException(
                status_code=400,
                detail="Generated SQL is not a SELECT query"
            )
        
        # Step 3: Execute via MCP WebSocket
        if trace:
            span = trace.span(
                name="mcp_sql_execution",
                input={"sql_query": sql_query}
            )
        
        result = await execute_sql_query(WS_URL, WS_API_KEY, sql_query)
        
        if trace:
            span.end(output={
                "row_count": result.get("rowCount"),
                "execution_time_ms": result.get("executionTimeMs")
            })
        
        # Step 4: Update trace with success
        if trace:
            trace.update(
                output={
                    "sql_query": sql_query,
                    "row_count": result.get("rowCount"),
                    "execution_time_ms": result.get("executionTimeMs")
                },
                level="DEFAULT",
                status_message="Success"
            )
        
        # Step 5: Return response
        return QueryResponse(
            question=request.question,
            sql_query=sql_query,
            result=result,
            trace_url=trace_url
        )
    
    except HTTPException:
        if trace:
            trace.update(level="ERROR", status_message="HTTP error")
        raise
    except Exception as e:
        if trace:
            trace.update(
                level="ERROR",
                status_message=str(e)
            )
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Flush Langfuse data on shutdown"""
    if use_langfuse and langfuse:
        langfuse.flush()
        print("✓ Langfuse data flushed")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("HTTP_PORT", "9002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
