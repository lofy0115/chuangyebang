from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class ComplaintType(Base):
    __tablename__ = "complaint_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("industries.id"), nullable=True)
    keywords = Column(JSON, nullable=True)

    parent = relationship("Industry", remote_side=[id], back_populates="children")
    children = relationship("Industry", back_populates="parent")


class ComplaintRecord(Base):
    __tablename__ = "complaint_records"

    id = Column(Integer, primary_key=True, index=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    complaint_type_id = Column(Integer, ForeignKey("complaint_types.id"), nullable=False)
    content = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    customer_tags = Column(JSON, nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    industry = relationship("Industry", back_populates="complaint_records")
    complaint_type = relationship("ComplaintType", back_populates="complaint_records")


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tags = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    complaint_type_id = Column(Integer, ForeignKey("complaint_types.id"), nullable=True)
    count = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    customer_segment = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    industry = relationship("Industry", back_populates="analysis_results")
    complaint_type = relationship("ComplaintType", back_populates="analysis_results")


Industry.complaint_records = relationship("ComplaintRecord", back_populates="industry")
Industry.analysis_results = relationship("AnalysisResult", back_populates="industry")
ComplaintType.complaint_records = relationship("ComplaintRecord", back_populates="complaint_type")
ComplaintType.analysis_results = relationship("AnalysisResult", back_populates="complaint_type")