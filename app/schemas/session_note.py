# app/schemas/session_note.py

from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class NoteType(str, Enum):
    RAW = "RAW"
    # PostgreSQL'deki note_type enum'unda ne varsa:
    # CLEANED = "CLEANED"
    # SUMMARY = "SUMMARY"
    # ACTION_ITEMS = "ACTION_ITEMS"
    # vs.


class SessionNoteBase(BaseModel):
    session_id: int
    author_id: int | None = None  # create'de boş gelirse current_user'dan set edebiliriz
    type: NoteType | None = None  # None => DB default RAW
    content: str
    is_private: bool | None = None  # None => DB default true


class SessionNoteCreate(SessionNoteBase):
    # Şimdilik ekstra bir field yok
    pass


class SessionNoteUpdate(BaseModel):
    session_id: int | None = None
    author_id: int | None = None
    type: NoteType | None = None
    content: str | None = None
    is_private: bool | None = None


class SessionNoteOut(SessionNoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v1 ise:
        # orm_mode = True
