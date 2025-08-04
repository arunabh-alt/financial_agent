import os
from dotenv import load_dotenv
from agno.models.groq import Groq

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    AGENT_CONFIG = {
        "data_agent": Groq(id="llama-3.1-8b-instant"),
        "analysis_agent": Groq(id="llama-3.1-8b-instant"),
        "recommendation_agent": Groq(id="deepseek-r1-distill-llama-70b")
    }

    TOKEN_LIMITS = {
        "data_agent": 800,
        "analysis_agent": 1000,
        "recommendation_agent": 1500
    }

    MAX_RETRIES = 2
    RETRY_DELAY = 3
    MIN_CONFIDENCE = 0.7  

    CACHE_SETTINGS = {
        'enabled': True,
        'ttl': 3600,  
    }
    
    MONITORING = {
        'prometheus': True,
        'hallucination_metrics': ['confidence_score', 'metric_discrepancies']
    }

config = Config()