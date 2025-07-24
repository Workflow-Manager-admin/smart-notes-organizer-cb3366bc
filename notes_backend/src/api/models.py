from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT access and refresh tokens for authentication responses."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token")

# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """Token payload structure, contains username."""
    username: Optional[str] = Field(None, description="Email of the user")

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """Base user info structure used for input/return."""
    email: EmailStr = Field(..., description="User email address")

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    """User registration payload."""
    password: str = Field(..., min_length=6, description="Password for new user")

# PUBLIC_INTERFACE
class UserLogin(UserBase):
    """User login payload."""
    password: str = Field(..., min_length=6, description="Password for login")

# PUBLIC_INTERFACE
class User(UserBase):
    """User model for responses."""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class Tag(BaseModel):
    """Note tag model."""
    id: int
    name: str
    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class TagCreate(BaseModel):
    """Tag creation model."""
    name: str

# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Shared properties for notes."""
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")
    tags: Optional[List[str]] = Field(default=[], description="List of tags as strings")

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Payload for creating a note."""
    pass

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Payload for updating a note."""
    title: Optional[str] = Field(None, description="Title of the note")
    content: Optional[str] = Field(None, description="Content of the note")
    tags: Optional[List[str]] = Field(default=None, description="List of tag names (strings)")

# PUBLIC_INTERFACE
class Note(NoteBase):
    """Note model for returning a note object."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []
    class Config:
        orm_mode = True
