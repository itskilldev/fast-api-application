from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Note, User
from ..schemas import NoteCreate, NoteOut, NoteUpdate
from ..security import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes (CRUD)"])


def _get_owned_note(note_id: int, user: User, db: Session) -> Note:
    note = db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = Note(**payload.model_dump(), owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[NoteOut])
def list_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Note).where(Note.owner_id == user.id).order_by(Note.id.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_owned_note(note_id, user, db)


@router.put("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int, payload: NoteUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    note = _get_owned_note(note_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = _get_owned_note(note_id, user, db)
    db.delete(note)
    db.commit()
