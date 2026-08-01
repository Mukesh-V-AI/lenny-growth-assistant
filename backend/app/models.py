import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    llm_engine = Column(String, default="ollama")
    
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(String)
    has_artifact = Column(Boolean, default=False)
    artifact_type = Column(String, nullable=True)
    artifact_content = Column(String, nullable=True)
    sources_json = Column(String, nullable=True)
    latency_ms = Column(String, nullable=True)
    llm_engine = Column(String, nullable=True)
    token_count = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="messages")
