"""MCP Server Entry Point"""
import asyncio
import signal
from .db import db_pool
from .ws_server import start_websocket_server


async def shutdown(signal_type):
    """Graceful shutdown handler"""
    print(f"\n✓ Received {signal_type}, shutting down...")
    await db_pool.close()


async def main():
    """Main entry point"""
    print("=" * 60)
    print("  MCP PostgreSQL Server (WebSocket)")
    print("=" * 60)
    
    # Connect to database
    await db_pool.connect()
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s))
        )
    
    # Start WebSocket server
    try:
        await start_websocket_server()
    except KeyboardInterrupt:
        await shutdown("SIGINT")


if __name__ == "__main__":
    asyncio.run(main())
