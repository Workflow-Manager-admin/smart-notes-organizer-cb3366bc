from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api import models, auth
from src.api.database import get_db, Note as DBNote, Tag as DBTag, User as DBUser

router = APIRouter(prefix="/notes", tags=["Notes"])

# PUBLIC_INTERFACE
@router.post("/", response_model=models.Note, summary="Create a note")
def create_note(note: models.NoteCreate, db: Session = Depends(get_db), current_user: DBUser = Depends(auth.get_current_user)):
    """
    Create a new note for the authenticated user. Tags provided will be created if new.
    """
    db_note = DBNote(title=note.title, content=note.content, owner_id=current_user.id)
    # Attach tags
    note_tags = []
    for tag_name in note.tags:
        db_tag = db.query(DBTag).filter_by(name=tag_name).first()
        if not db_tag:
            db_tag = DBTag(name=tag_name)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        note_tags.append(db_tag)
    db_note.tags = note_tags
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# PUBLIC_INTERFACE
@router.get("/", response_model=List[models.Note], summary="List all notes", response_description="List of all notes for the user.")
def list_notes(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(auth.get_current_user),
    search: Optional[str] = Query(None, description="Filter by search term in title or content"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
):
    """
    List all notes for the current user, optionally filtering by search keyword or tag.
    """
    query = db.query(DBNote).filter(DBNote.owner_id == current_user.id)
    if search:
        query = query.filter(
            (DBNote.title.ilike(f'%{search}%')) | (DBNote.content.ilike(f'%{search}%'))
        )
    if tag:
        query = query.join(DBNote.tags).filter(DBTag.name == tag)
    return query.order_by(DBNote.updated_at.desc()).all()

# PUBLIC_INTERFACE
@router.get("/{note_id}", response_model=models.Note, summary="Get note by ID")
def get_note(note_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(auth.get_current_user)):
    """
    Retrieve a note by its ID if the user owns it.
    """
    note = db.query(DBNote).filter(DBNote.id == note_id, DBNote.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# PUBLIC_INTERFACE
@router.put("/{note_id}", response_model=models.Note, summary="Update a note")
def update_note(note_id: int, note: models.NoteUpdate, db: Session = Depends(get_db), current_user: DBUser = Depends(auth.get_current_user)):
    """
    Update title/content/tags of a note (patch semantics). Only owner can update.
    """
    db_note = db.query(DBNote).filter(DBNote.id == note_id, DBNote.owner_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.title is not None:
        db_note.title = note.title
    if note.content is not None:
        db_note.content = note.content
    if note.tags is not None:
        note_tags = []
        for tag_name in note.tags:
            db_tag = db.query(DBTag).filter_by(name=tag_name).first()
            if not db_tag:
                db_tag = DBTag(name=tag_name)
                db.add(db_tag)
                db.commit()
                db.refresh(db_tag)
            note_tags.append(db_tag)
        db_note.tags = note_tags
    db.commit()
    db.refresh(db_note)
    return db_note

# PUBLIC_INTERFACE
@router.delete("/{note_id}", summary="Delete a note", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(auth.get_current_user)):
    """
    Delete a note. Only user who owns the note can delete.
    """
    db_note = db.query(DBNote).filter(DBNote.id == note_id, DBNote.owner_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return
