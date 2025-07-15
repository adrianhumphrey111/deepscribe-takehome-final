from typing import List, Optional
from pydantic import BaseModel

class QARequest(BaseModel):
    trial_id: str
    question: str
    patient_context: Optional[dict] = None

class QAResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str]
    response_time_ms: int
    success: bool = True
    error_message: Optional[str] = None

class QASession(BaseModel):
    session_id: str
    trial_id: str
    conversation_history: List[dict]
    created_at: str