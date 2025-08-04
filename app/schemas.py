from pydantic import BaseModel, validator, Field
from typing import Dict, List, Optional, Union, Any

class CompanyData(BaseModel):
    ticker: str
    fundamentals: Dict
    news: List[Dict]
    analyst_recommendations: Dict
    price_history: Dict

class InvestmentRecommendation(BaseModel):
    ticker: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    investment_thesis: str
    risk_assessment: Dict[str, str] = Field(default_factory=dict)  # Changed to dict
    key_metrics: Dict[str, Optional[Union[float, int]]]
    warnings: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)  # Added for citations
    
   
    
    @validator('risk_assessment', pre=True)
    def normalize_risk_assessment(cls, value):
        """Ensure risk_assessment is always a dict"""
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return {"overall": value}
        return {"overall": "medium"}

    @validator('warnings', pre=True)
    def normalize_warnings(cls, value):
        """Ensure warnings is always a list of strings"""
        if value is None:
            return []
        if isinstance(value, str):
            if ',' in value:
                return [w.strip() for w in value.split(',')]
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

    @validator('key_metrics', pre=True)
    def convert_metrics(cls, value):
        """Convert string metrics to numbers where possible"""
        if not isinstance(value, dict):
            return {}
            
        converted = {}
        for k, v in value.items():
            if isinstance(v, (float, int)):
                converted[k] = v
            elif isinstance(v, str):
                if v.replace('.', '', 1).isdigit():
                    converted[k] = float(v)
                elif v.lower() in ['n/a', 'na', 'null']:
                    converted[k] = None
                else:
                    try:
                        if '%' in v:
                            converted[k] = float(v.strip('%')) / 100
                        elif '-' in v:
                            parts = v.split('-')
                            converted[k] = (float(parts[0]) + float(parts[1])) / 2
                        elif any(word in v.lower() for word in ['above', 'below', 'over', 'under']):
                            for part in v.split():
                                if part.replace('.', '', 1).isdigit():
                                    converted[k] = float(part)
                                    break
                            else:
                                converted[k] = None
                        else:
                            converted[k] = None
                    except:
                        converted[k] = None
            else:
                converted[k] = None
        return converted