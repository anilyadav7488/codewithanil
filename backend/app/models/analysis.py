import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    input_text = Column(Text, nullable=True) # Only saved if user consented
    text_snippet = Column(String(255), nullable=False)
    analysis_type = Column(String(50), default="text", nullable=False) # 'text' or 'document'
    word_count = Column(Integer, default=0, nullable=False)
    character_count = Column(Integer, default=0, nullable=False)
    prediction = Column(String(50), nullable=False) # 'Human', 'AI-Generated', 'Inconclusive'
    model_score = Column(Float, nullable=False) # AI calibrated score 0.0 - 1.0
    human_score = Column(Float, nullable=False) # Human calibrated score 0.0 - 1.0
    is_inconclusive = Column(Boolean, default=False, nullable=False)
    model_name = Column(String(120), nullable=False)
    model_version = Column(String(50), nullable=False)
    processing_time_ms = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    user = relationship("User", back_populates="analyses")
    document = relationship("Document", back_populates="analysis", uselist=False)
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")
