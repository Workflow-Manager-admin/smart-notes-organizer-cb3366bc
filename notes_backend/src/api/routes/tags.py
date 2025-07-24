from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api import models, auth
from src.api.database import get_db, Tag as DBTag, DBUser

router = APIRouter(prefix="/tags", tags=["Tags"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[models.Tag], summary="List all tags for current user")
def list_tags(db: Session = Depends(get_db), current_user: DBUser = Depends(auth.get_current_user)):
    """
    List all tags associated with the authenticated user's notes.
    """
    tags = db.query(DBTag).join(DBTag.notes).filter(DBTag.notes.any(owner_id=current_user.id)).distinct().all()
    return tags

# PUBLIC_INTERFACE
@router.post("/", response_model=models.Tag, summary="Create tag")
def create_tag(tag: models.TagCreate, db: Session = Depends(get_db), current_user: DBUser = Depends(auth.get_current_user)):
    """
    Create a new tag for organizing notes.
    Tags are global, but multiple users can share them. Returns the tag object.
    """
    db_tag = db.query(DBTag).filter_by(name=tag.name).first()
    if db_tag:
        return db_tag
    db_tag = DBTag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag
