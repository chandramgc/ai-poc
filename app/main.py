"""Main FastAPI application module."""
import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, status, WebSocketDisconnect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.schemas import ErrorResponse, RelationshipResponse, WSRequest
from app.service import RelationshipService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Initialize service on startup
    app.state.service = RelationshipService()
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="Relationship Finder MCP",
    description="Find relationships using FastAPI and LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)


def verify_api_key(request: Request, settings: Settings = Depends(get_settings)) -> None:
    """Verify the API key from headers."""
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/healthz",
    tags=["health"],
    summary="Get service health status",
    response_model=dict
)
async def health_check():
    """Get service health status."""
    return app.state.service.get_health()


@app.get(
    "/relationship",
    tags=["relationship"],
    summary="Get relationship by name",
    response_model=RelationshipResponse,
    dependencies=[Depends(verify_api_key)],
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_relationship(name: str, request: Request):
    """Get relationship for a person by name."""
    result = await app.state.service.get_relationship(name)
    
    if result["confidence"] == "Low":
        trace_id = str(uuid.uuid4())
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"No confident match found for name: {name}",
                    "traceId": trace_id
                }
            }
        )
    
    return result


@app.post(
    "/reload",
    tags=["admin"],
    summary="Reload data from Excel file",
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def reload_data():
    """Reload data from Excel file."""
    app.state.service.reload_data()


@app.websocket("/relationship/stream")
async def relationship_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming relationship lookup steps."""
    await websocket.accept()

    try:
        # Verify API key
        api_key = websocket.headers.get("X-API-Key")
        if not api_key or api_key != get_settings().API_KEY:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Handle multiple requests in a loop
        while True:
            try:
                # Get request data
                data = await websocket.receive_json()
                
                try:
                    request = WSRequest(**data)
                except Exception as validation_error:
                    await websocket.send_json({
                        "event": "error",
                        "error": {
                            "code": "INVALID_REQUEST",
                            "message": f"Invalid request format: {str(validation_error)}",
                            "traceId": str(uuid.uuid4())
                        }
                    })
                    continue  # Continue to next request instead of closing

                # Stream results
                async for event in app.state.service.get_relationship_stream(request.name):
                    await websocket.send_json(event)

            except Exception as e:
                # Check if it's a connection close
                if isinstance(e, WebSocketDisconnect):
                    break  # Exit the loop on connection close
                
                await websocket.send_json({
                    "event": "error",
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": str(e),
                        "traceId": str(uuid.uuid4())
                    }
                })
                break  # Exit on other errors

    finally:
        await websocket.close()