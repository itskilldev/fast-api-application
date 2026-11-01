from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import ai as ai_service
from ..database import get_db
from ..models import Note, User
from ..schemas import NoteOut, SummarizeRequest, SummarizeResponse
from ..security import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_text(payload: SummarizeRequest, _: User = Depends(get_current_user)):
    summary, provider = ai_service.summarize(payload.text)
    return SummarizeResponse(summary=summary, provider=provider)


@router.post("/notes/{note_id}/summarize", response_model=NoteOut)
def summarize_note(note_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    note.summary, _ = ai_service.summarize(note.content)
    db.commit()
    db.refresh(note)
    return note
