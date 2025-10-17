"""Python client for the Relationship Finder MCP service."""
import argparse
import asyncio
import json
from typing import Optional
from urllib.parse import urljoin

import httpx
import websockets


async def get_relationship(
    name: str,
    url: str = "http://localhost:8000",
    api_key: str = "dev",
    stream: bool = False
) -> None:
    """Get relationship from the MCP service."""
    if not stream:
        # HTTP request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    urljoin(url, "relationship"),
                    params={"name": name},
                    headers={"X-API-Key": api_key}
                )
                response.raise_for_status()
                print(json.dumps(response.json(), indent=2))
            except httpx.HTTPStatusError as e:
                print(json.dumps(e.response.json(), indent=2))
        return

    # WebSocket streaming
    ws_url = urljoin(url.replace("http", "ws"), "relationship/stream")
    async with websockets.connect(ws_url, extra_headers={"X-API-Key": api_key}) as ws:
        await ws.send(json.dumps({"name": name, "trace": True}))
        try:
            while True:
                msg = await ws.recv()
                print(json.dumps(json.loads(msg), indent=2))
        except websockets.ConnectionClosed:
            pass


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Relationship Finder MCP Client")
    parser.add_argument("--name", required=True, help="Name to look up")
    parser.add_argument("--url", default="http://localhost:8000", help="Service URL")
    parser.add_argument("--api-key", default="dev", help="API key")
    parser.add_argument("--stream", action="store_true", help="Stream results via WebSocket")
    
    args = parser.parse_args()
    asyncio.run(get_relationship(args.name, args.url, args.api_key, args.stream))


if __name__ == "__main__":
    main()