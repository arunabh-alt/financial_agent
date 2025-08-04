# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import time
from contextlib import asynccontextmanager

from app.orchestrator import Orchestrator
from app.schemas import InvestmentRecommendation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Investment Recommendation API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    tickers: list[str]
    criteria: dict

class RecommendationResponse(BaseModel):
    recommendations: list[InvestmentRecommendation]
    processing_time: float

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    try:
        logger.info(f"Processing request for {request.tickers}")
        start_time = time.time()
        
        async with Orchestrator() as orchestrator:
            results = await orchestrator.process_tickers(request.tickers, request.criteria)
            
        return RecommendationResponse(
            recommendations=results,
            processing_time=round(time.time() - start_time, 2)
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)