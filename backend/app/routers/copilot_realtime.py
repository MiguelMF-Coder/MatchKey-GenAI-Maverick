"""
Real-time WebSocket endpoint for HR Copilot interviews.
Provides streaming feedback and progress updates during the interview process.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
import logging

from ..services.hr_copilot.hr_copilot_tool import get_hr_copilot
from ..services.hr_copilot.questions import get_questions_text

router = APIRouter(prefix="/copilot/realtime", tags=["copilot-realtime"])
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time interview sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connection established: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket connection closed: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
    
    async def send_progress(self, session_id: str, step: str, progress: int, message: str):
        """Send progress update to client"""
        await self.send_message(session_id, {
            "type": "progress",
            "step": step,
            "progress": progress,
            "message": message
        })
    
    async def send_question(self, session_id: str, question_num: int, question: str, total: int):
        """Send next question to client"""
        await self.send_message(session_id, {
            "type": "question",
            "question_num": question_num,
            "question": question,
            "total": total
        })
    
    async def send_analysis(self, session_id: str, analysis: dict):
        """Send final analysis to client"""
        await self.send_message(session_id, {
            "type": "analysis",
            "data": analysis
        })
    
    async def send_error(self, session_id: str, error: str):
        """Send error message to client"""
        await self.send_message(session_id, {
            "type": "error",
            "error": error
        })


manager = ConnectionManager()


@router.websocket("/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time interview sessions.
    
    Message Protocol:
    
    Client -> Server:
    {
        "type": "start",
        "candidate_id": 123
    }
    {
        "type": "answer",
        "question_num": 1,
        "answer": "Mi respuesta..."
    }
    {
        "type": "finish"
    }
    
    Server -> Client:
    {
        "type": "progress",
        "step": "initialization",
        "progress": 10,
        "message": "Iniciando entrevista..."
    }
    {
        "type": "question",
        "question_num": 1,
        "question": "¿Qué te motiva?",
        "total": 5
    }
    {
        "type": "analysis",
        "data": { ... }
    }
    {
        "type": "error",
        "error": "Error message"
    }
    """
    await manager.connect(session_id, websocket)
    
    # Session state
    candidate_id = None
    questions = get_questions_text()
    answers = []
    current_question = 0
    
    try:
        await manager.send_progress(session_id, "connected", 0, "Conectado al servidor")
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "start":
                # Start interview session
                candidate_id = data.get("candidate_id")
                
                if not candidate_id:
                    await manager.send_error(session_id, "candidate_id es requerido")
                    continue
                
                await manager.send_progress(
                    session_id, 
                    "initialization", 
                    10, 
                    "Entrevista iniciada"
                )
                
                # Send first question
                current_question = 0
                await manager.send_question(
                    session_id,
                    current_question + 1,
                    questions[current_question],
                    len(questions)
                )
                
                await manager.send_progress(
                    session_id,
                    "ready",
                    15,
                    f"Pregunta {current_question + 1} de {len(questions)}"
                )
            
            elif message_type == "answer":
                # Receive answer from client
                question_num = data.get("question_num", 0)
                answer = data.get("answer", "").strip()
                
                if not answer:
                    await manager.send_error(session_id, "Respuesta vacía")
                    continue
                
                # Store answer
                answers.append(answer)
                
                # Send progress
                progress = 15 + int((len(answers) / len(questions)) * 60)
                await manager.send_progress(
                    session_id,
                    "answering",
                    progress,
                    f"Respuesta {len(answers)} recibida"
                )
                
                # Send next question or finish
                if len(answers) < len(questions):
                    current_question = len(answers)
                    await manager.send_question(
                        session_id,
                        current_question + 1,
                        questions[current_question],
                        len(questions)
                    )
                    
                    await manager.send_progress(
                        session_id,
                        "ready",
                        progress,
                        f"Pregunta {current_question + 1} de {len(questions)}"
                    )
                else:
                    # All questions answered, trigger analysis
                    await manager.send_progress(
                        session_id,
                        "processing",
                        80,
                        "Todas las respuestas recibidas. Analizando..."
                    )
                    
                    # Simulate processing steps for better UX
                    await asyncio.sleep(0.5)
                    await manager.send_progress(
                        session_id,
                        "analyzing",
                        85,
                        "Extrayendo motivaciones..."
                    )
                    
                    await asyncio.sleep(0.3)
                    await manager.send_progress(
                        session_id,
                        "analyzing",
                        90,
                        "Identificando valores..."
                    )
                    
                    await asyncio.sleep(0.3)
                    await manager.send_progress(
                        session_id,
                        "analyzing",
                        95,
                        "Detectando soft skills..."
                    )
                    
                    # Perform actual analysis
                    try:
                        hr = get_hr_copilot()
                        result = hr.run(answers, questions)
                        result["candidate_id"] = candidate_id
                        result["success"] = True
                        
                        await manager.send_progress(
                            session_id,
                            "complete",
                            100,
                            "Análisis completado"
                        )
                        
                        # Send analysis results
                        await manager.send_analysis(session_id, result)
                        
                    except Exception as e:
                        logger.error(f"Error analyzing responses: {e}")
                        await manager.send_error(
                            session_id,
                            f"Error al analizar respuestas: {str(e)}"
                        )
            
            elif message_type == "finish":
                # Client wants to finish session
                await manager.send_progress(
                    session_id,
                    "closing",
                    100,
                    "Sesión finalizada"
                )
                break
            
            else:
                await manager.send_error(
                    session_id,
                    f"Tipo de mensaje desconocido: {message_type}"
                )
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.send_error(session_id, str(e))
        except:
            pass
    finally:
        manager.disconnect(session_id)


@router.get("/health")
def realtime_health():
    """Check real-time endpoint health"""
    return {
        "status": "healthy",
        "active_sessions": len(manager.active_connections),
        "websocket_endpoint": "/copilot/realtime/interview/{session_id}"
    }

