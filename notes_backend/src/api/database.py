import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

DATABASE_URL = os.environ.get("NOTES_DB_URL", "sqlite:///./notes.db")

Base = declarative_base()

# Association table for notes <-> tags (many-to-many)
note_tag_table = Table(
    "note_tag_association", Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class User(Base):
    """SQLAlchemy User model."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship('Note', back_populates='owner')

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class Note(Base):
    """SQLAlchemy Note model."""
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tags = relationship("Tag", secondary=note_tag_table, backref="notes")
    owner = relationship("User", back_populates="notes")

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the database, creating tables if needed."""
    Base.metadata.create_all(bind=engine)
