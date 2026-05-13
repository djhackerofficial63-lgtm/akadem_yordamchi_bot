from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from datetime import datetime

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# ============ MODELS ============

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    first_doc_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.telegram_id}>"

class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    doc_type = Column(String(50))
    template_style = Column(String(50))
    title = Column(String(255))
    content = Column(Text)
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Document {self.id}>"

# ============ DATABASE FUNCTIONS ============

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get database session"""
    return SessionLocal()

def create_user(telegram_id, username=None, first_name=None):
    """Create new user"""
    session = get_session()
    try:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()

def get_user(telegram_id):
    """Get user by telegram_id"""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        return user
    finally:
        session.close()

def save_document(user_id, doc_type, style, title, content, file_path):
    """Save document to database"""
    session = get_session()
    try:
        document = Document(
            user_id=user_id,
            doc_type=doc_type,
            template_style=style,
            title=title,
            content=content,
            file_path=file_path,
            created_at=datetime.utcnow()
        )
        session.add(document)
        session.commit()
        return document
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()
