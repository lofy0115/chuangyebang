from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ComplaintTypeSchema(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    keywords: Optional[list[str]] = None

    class Config:
        from_attributes = True


class IndustrySchema(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    keywords: Optional[list[str]] = None

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    keyword: str


class ComplaintDistributionItem(BaseModel):
    type: str
    count: int
    percentage: float


class TopValueNeed(BaseModel):
    need: str
    priority: int


class CustomerSegmentNeed(BaseModel):
    segment: str
    needs: list[str]


class AnalyzeResponse(BaseModel):
    industry: str
    complaint_distribution: list[ComplaintDistributionItem]
    top_value_needs: list[TopValueNeed]
    customer_segments: list[CustomerSegmentNeed]
    total_records: int


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.now)