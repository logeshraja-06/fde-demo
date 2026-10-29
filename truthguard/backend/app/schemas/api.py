from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.verification import FinalTruthGuardReport


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000, description="User question to verify against documents")
    user_id: Optional[str] = "default_user"
    permissions: List[str] = Field(default_factory=lambda: ["read_all"])
    version_filter: Optional[str] = None
    document_ids: Optional[List[str]] = None


class QuestionResponse(FinalTruthGuardReport):
    pass
