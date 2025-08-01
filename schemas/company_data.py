from pydantic import BaseModel, Field
from typing import List, Optional

class CompanyFinancials(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    current_price: float
    pe_ratio: Optional[float]
    revenue_growth: float

class CompanySentiment(BaseModel):
    positive_score: float = Field(..., ge=0, le=1)
    risk_factors: List[str]

class InvestmentRecommendation(BaseModel):
    company_id: str
    match_score: float
    sources: List[str]  # For hallucination tracking