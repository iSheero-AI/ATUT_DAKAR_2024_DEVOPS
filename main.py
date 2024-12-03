from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from prompts import prompt
from helpers import retriever
from helpers import generator
import os, json
from dotenv import load_dotenv

load_dotenv()
retriever_instance = retriever.Retriever()
generator_instance = generator.Generator()
chain = generator_instance.create_chain()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("DBMessage", back_populates="conversation")

class DBMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")

Base.metadata.create_all(bind=engine)

class MessageBase(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class Message(MessageBase):
    id: Optional[int] = None
    conversation_id: Optional[int] = None

    class Config:
        orm_mode = True

class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[Message]

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    message: Message

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper Functions
def get_conversation_messages(db: Session, conversation_id: int) -> List[dict]:
    messages = db.query(DBMessage).filter(
        DBMessage.conversation_id == conversation_id
    ).order_by(DBMessage.timestamp).all()
    return [{"role": msg.role, "content": msg.content} for msg in messages]

# Routes
@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    db_conversation = Conversation(title=conversation.title)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@app.get("/api/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: Session = Depends(get_db)
):
    # print(json.dumps(TOOLS))
    return db.query(Conversation).all()

@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted"}


@app.post("/api/chat", response_model=Message)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        # Create new conversation if none specified
        if not request.conversation_id:
            conversation = Conversation(title=request.message[:30] + "...")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
        else:
            conversation_id = request.conversation_id
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

        user_message = DBMessage(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()

        messages = get_conversation_messages(db, conversation_id)
        documents = retriever_instance.get_relevants_documents(request.message, 5)
        question, answer = generator_instance.generate(chain, request.message, documents)
        print(answer)

        assistant_message = DBMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            timestamp=datetime.utcnow()
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return assistant_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
