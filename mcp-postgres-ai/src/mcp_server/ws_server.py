"""WebSocket MCP Server Implementation"""
import json
import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Dict, Any
from .config import settings
from .tools import run_sql, MCP_TOOLS


async def handle_mcp_request(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol messages"""
    
    # List tools request
    if message.get("method") == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": MCP_TOOLS
        }
    
    # Call tool request
    if message.get("method") == "tools/call":
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "run_sql":
            try:
                result = await run_sql(
                    query=arguments.get("query"),
                    params=arguments.get("params", [])
                )
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32601,
                "message": f"Tool not found: {tool_name}"
            }
        }
    
    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": message.get("id"),
        "error": {
            "code": -32601,
            "message": f"Method not found: {message.get('method')}"
        }
    }


async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
    """Handle WebSocket connections"""
    
    # Validate path
    if path != "/mcp":
        await websocket.close(code=1008, reason="Invalid path")
        return
    
    # Validate API key
    api_key = websocket.request_headers.get("X-API-Key")
    if api_key != settings.ws_api_key:
        await websocket.close(code=1008, reason="Invalid API key")
        return
    
    print(f"✓ Client connected: {websocket.remote_address}")
    
    try:
        # Send initial tool registry
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/registry",
            "params": MCP_TOOLS
        }))
        
        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                response = await handle_mcp_request(data)
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }))
            except Exception as e:
                print(f"✗ Error handling message: {e}")
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }))
    
    except websockets.exceptions.ConnectionClosed:
        print(f"✓ Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"✗ WebSocket error: {e}")


async def start_websocket_server():
    """Start WebSocket MCP server"""
    server = await websockets.serve(
        websocket_handler,
        settings.ws_host,
        settings.ws_port,
        ping_interval=30,
        ping_timeout=10
    )
    
    print(f"✓ MCP WebSocket server started: ws://{settings.ws_host}:{settings.ws_port}/mcp")
    print(f"  API Key required: X-API-Key header")
    
    await asyncio.Future()  # Run forever
