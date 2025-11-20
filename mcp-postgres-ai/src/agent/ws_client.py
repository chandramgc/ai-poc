"""WebSocket MCP Client for Agent"""
import json
import asyncio
import websockets
from typing import Dict, Any, Optional


class MCPClient:
    def __init__(self, ws_url: str, api_key: str):
        self.ws_url = ws_url
        self.api_key = api_key
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.request_id = 0
    
    async def connect(self):
        """Connect to MCP WebSocket server"""
        headers = {"X-API-Key": self.api_key}
        self.websocket = await websockets.connect(
            self.ws_url,
            extra_headers=headers,
            ping_interval=30,
            ping_timeout=10
        )
        
        # Receive initial tool registry
        registry_msg = await self.websocket.recv()
        registry = json.loads(registry_msg)
        print(f"✓ Connected to MCP server, tools available: {len(registry.get('params', {}).get('tools', []))}")
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool and return result"""
        if not self.websocket:
            raise RuntimeError("Not connected to MCP server")
        
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request
        await self.websocket.send(json.dumps(request))
        
        # Receive response
        response_msg = await self.websocket.recv()
        response = json.loads(response_msg)
        
        if "error" in response:
            raise Exception(f"MCP Error: {response['error']['message']}")
        
        # Extract result from MCP response
        content = response.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        
        return response.get("result", {})
    
    async def run_sql(self, query: str, params: list = None) -> Dict[str, Any]:
        """Execute SQL query via MCP"""
        return await self.call_tool("run_sql", {
            "query": query,
            "params": params or []
        })


async def execute_sql_query(ws_url: str, api_key: str, query: str, params: list = None) -> Dict[str, Any]:
    """
    Convenience function to execute SQL query via MCP.
    Opens connection, executes query, closes connection.
    """
    client = MCPClient(ws_url, api_key)
    try:
        await client.connect()
        result = await client.run_sql(query, params)
        return result
    finally:
        await client.disconnect()
