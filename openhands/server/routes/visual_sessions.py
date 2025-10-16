"""
Visual Sessions API for managing visual runtime workers
"""

import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel


class VisualSessionCreate(BaseModel):
    """Request model for creating a visual session"""
    resolution: str = "1600x900"
    timeout_minutes: int = 60
    idle_timeout_minutes: int = 15
    enable_recording: bool = True
    enable_file_transfer: bool = True


class VisualSession(BaseModel):
    """Response model for visual session"""
    session_id: str
    vnc_url: str
    novnc_url: str
    status: str
    created_at: datetime
    expires_at: datetime
    recording_url: Optional[str] = None
    logs_url: Optional[str] = None


class VisualSessionManager:
    """Manages visual runtime sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = 3600  # 1 hour default
        
    def create_session(self, request: VisualSessionCreate) -> VisualSession:
        """Create a new visual session"""
        session_id = str(uuid.uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=request.timeout_minutes)
        
        # Generate URLs
        vnc_url = f"vnc://localhost:5901"
        novnc_url = f"http://localhost:7900/vnc.html?path=vnc.html&resize=scale&autoconnect=true&session={session_id}"
        
        session_data = {
            "session_id": session_id,
            "vnc_url": vnc_url,
            "novnc_url": novnc_url,
            "status": "starting",
            "created_at": created_at,
            "expires_at": expires_at,
            "resolution": request.resolution,
            "recording_enabled": request.enable_recording,
            "file_transfer_enabled": request.enable_file_transfer,
            "last_activity": time.time(),
            "idle_timeout": request.idle_timeout_minutes * 60
        }
        
        self.sessions[session_id] = session_data
        
        return VisualSession(
            session_id=session_id,
            vnc_url=vnc_url,
            novnc_url=novnc_url,
            status="starting",
            created_at=created_at,
            expires_at=expires_at,
            recording_url=f"/api/visual-sessions/{session_id}/recording" if request.enable_recording else None,
            logs_url=f"/api/visual-sessions/{session_id}/logs"
        )
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str):
        """Update session last activity timestamp"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = time.time()
    
    def stop_session(self, session_id: str) -> bool:
        """Stop a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = "stopped"
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            # Check if session has expired
            if datetime.now() > session["expires_at"]:
                expired_sessions.append(session_id)
            # Check if session is idle
            elif current_time - session["last_activity"] > session["idle_timeout"]:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]


# Global session manager
session_manager = VisualSessionManager()


def add_visual_session_endpoints(app: FastAPI):
    """Add visual session endpoints to FastAPI app"""
    
    @app.post("/api/visual-sessions", response_model=VisualSession)
    async def create_visual_session(
        request: VisualSessionCreate,
        background_tasks: BackgroundTasks
    ):
        """Create a new visual runtime session"""
        try:
            session = session_manager.create_session(request)
            
            # In production, this would launch a Docker container
            # For now, we'll simulate the session
            background_tasks.add_task(_start_visual_session, session.session_id)
            
            return session
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    
    @app.get("/api/visual-sessions/{session_id}", response_model=VisualSession)
    async def get_visual_session(session_id: str):
        """Get visual session details"""
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update activity
        session_manager.update_session_activity(session_id)
        
        return VisualSession(**session)
    
    @app.post("/api/visual-sessions/{session_id}/stop")
    async def stop_visual_session(session_id: str):
        """Stop a visual session"""
        if session_manager.stop_session(session_id):
            return {"status": "success", "message": "Session stopped"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    @app.get("/api/visual-sessions/{session_id}/recording")
    async def get_session_recording(session_id: str):
        """Get session recording (placeholder)"""
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "recording_available": session.get("recording_enabled", False),
            "message": "Recording endpoint - would return video file in production"
        }
    
    @app.get("/api/visual-sessions/{session_id}/logs")
    async def get_session_logs(session_id: str):
        """Get session logs (placeholder)"""
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "logs": ["Session started", "Agent connected", "Recording active"],
            "message": "Logs endpoint - would return real logs in production"
        }


async def _start_visual_session(session_id: str):
    """Background task to start visual session (placeholder)"""
    # In production, this would:
    # 1. Launch Docker container with session_id
    # 2. Configure VNC/noVNC
    # 3. Start recording
    # 4. Update session status
    
    import asyncio
    await asyncio.sleep(2)  # Simulate startup time
    
    session = session_manager.get_session(session_id)
    if session:
        session["status"] = "running"