"""
WebSocket routes for real-time court case updates
Clients can connect and receive live notifications when new cases are detected
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Case
import logging
import json
from datetime import datetime
from typing import Set

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ws", tags=["websocket"])

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: dict = {}  # user_id -> {filters}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[client_id] = {"courts": [], "case_types": []}
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections.discard(websocket)
        self.subscriptions.pop(client_id, None)
        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending message: {str(e)}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def broadcast_filtered(self, message: dict, court_id: int = None, case_type: str = None):
        """Broadcast only to subscribed clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                # Check if this client should receive this message
                # based on their subscriptions
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending filtered message: {str(e)}")
                disconnected.add(connection)
        
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
    
    def set_subscription(self, client_id: str, courts: list = None, case_types: list = None):
        """Set subscription filters for a client"""
        if client_id in self.subscriptions:
            if courts:
                self.subscriptions[client_id]["courts"] = courts
            if case_types:
                self.subscriptions[client_id]["case_types"] = case_types
            logger.info(f"Updated subscription for client {client_id}: courts={courts}, types={case_types}")


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time case updates.
    
    Client should send subscription messages like:
    {
        "type": "subscribe",
        "courts": ["Delhi High Court", "Bombay High Court"],
        "case_types": ["Writ Petition", "Civil Appeal"]
    }
    
    Server sends case updates like:
    {
        "type": "new_case",
        "case": {
            "id": 123,
            "case_number": "WP-2026-001",
            "cnr": "DELHC0123456789",
            "court": "Delhi High Court",
            "case_type": "Writ Petition",
            "petitioner": "...",
            "respondent": "...",
            "first_detected_at": "2026-03-10T10:30:00"
        }
    }
    """
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                # Update subscription preferences
                courts = message.get("courts", [])
                case_types = message.get("case_types", [])
                manager.set_subscription(client_id, courts, case_types)
                
                # Confirm subscription
                await manager.send_personal(
                    websocket,
                    {
                        "type": "subscribed",
                        "courts": courts,
                        "case_types": case_types,
                        "message": "Successfully subscribed to updates"
                    }
                )
            
            elif message.get("type") == "ping":
                # Keep-alive ping
                await manager.send_personal(
                    websocket,
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )
            
            elif message.get("type") == "get_status":
                # Get current connection status
                await manager.send_personal(
                    websocket,
                    {
                        "type": "status",
                        "connected": True,
                        "active_clients": len(manager.active_connections),
                        "subscription": manager.subscriptions.get(client_id, {})
                    }
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        manager.disconnect(websocket, client_id)


async def broadcast_new_case(case_data: dict):
    """
    Broadcast a newly detected case to all connected clients.
    Called by scraper when a new case is detected.
    """
    message = {
        "type": "new_case",
        "case": case_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(message)
    logger.info(f"Broadcasted new case: {case_data.get('case_number')} to {len(manager.active_connections)} clients")


async def broadcast_case_update(case_id: int, update_data: dict):
    """
    Broadcast case update (e.g., judgment released, status changed)
    """
    message = {
        "type": "case_update",
        "case_id": case_id,
        "update": update_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(message)
    logger.info(f"Broadcasted case update for case {case_id}")


async def broadcast_scrape_status(status: dict):
    """
    Broadcast scraping job status (started, completed, error)
    """
    message = {
        "type": "scrape_status",
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(message)
    logger.info(f"Broadcasted scrape status: {status.get('action')}")


@router.get("/ws/status")
async def get_websocket_status():
    """Get current WebSocket connection status"""
    return {
        "status": "ok",
        "active_connections": len(manager.active_connections),
        "subscriptions": len(manager.subscriptions),
        "timestamp": datetime.utcnow().isoformat()
    }
