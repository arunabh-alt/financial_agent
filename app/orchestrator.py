# from app.agents.data_agent import DataAgent
# from app.agents.analysis_agent import AnalysisAgent
# from app.agents.recommendation_agent import RecommendationAgent
# from app.schemas import InvestmentRecommendation
# import asyncio
# import time
# import logging
# from app.config import config

# logger = logging.getLogger(__name__)

# class Orchestrator:
#     def __init__(self):
#         self.data_agent = DataAgent()
#         self.analysis_agent = AnalysisAgent()
#         self.recommendation_agent = RecommendationAgent()
    
#     async def process_ticker(self, ticker: str, criteria: dict) -> InvestmentRecommendation:
#         logger.info(f"Processing {ticker} with criteria: {criteria}")
#         attempts = 0
#         while attempts < config.MAX_RETRIES:
#             try:
#                 # Step 1: Collect data
#                 company_data = self.data_agent.collect_data(ticker)
#                 if not company_data or "error" in company_data:
#                     # Special handling for Google
#                     if ticker == "GOOGL":
#                         logger.info("Trying alternative approaches for Google")
#                         # Try with GOOG
#                         company_data = self.data_agent.collect_data("GOOG")
#                         if not company_data or "error" in company_data:
#                             # Try with full name
#                             company_data = self.data_agent.collect_data("Alphabet")
#                     if not company_data or "error" in company_data:
#                         raise ValueError(f"Invalid data for {ticker}")
                
#                 # Step 2: Analyze data
#                 analysis = self.analysis_agent.analyze(company_data, criteria)
#                 if not analysis or "error" in analysis:
#                     raise ValueError(f"Invalid analysis from AnalysisAgent: {analysis}")
                
#                 # Step 3: Generate recommendation
#                 recommendation = self.recommendation_agent.generate(analysis)
                
#                 # Handle recommendation errors
#                 if "error" in recommendation:
#                     logger.error(f"RecommendationAgent error for {ticker}: {recommendation['error']}")
                    
#                 # Validate structure
#                 required_keys = ["confidence_score", "investment_thesis", "risk_assessment"]
#                 missing_keys = [key for key in required_keys if key not in recommendation]
#                 if missing_keys:
#                     logger.warning(f"Recommendation missing keys for {ticker}: {missing_keys}")
#                     recommendation = {
#                         "confidence_score": 0.0,
#                         "investment_thesis": f"Partial recommendation - missing {missing_keys}",
#                         "risk_assessment": "high",
#                         "key_metrics": recommendation.get("key_metrics", {}),
#                         "warnings": ["Incomplete recommendation"] + (recommendation.get("warnings", []) if isinstance(recommendation.get("warnings"), list) else [])
#                     }
                
#                 # Ensure warnings is a list
#                 if "warnings" in recommendation and not isinstance(recommendation["warnings"], list):
#                     recommendation["warnings"] = [str(recommendation["warnings"])]
                
#                 return InvestmentRecommendation(
#                     ticker=ticker,
#                     confidence_score=recommendation.get("confidence_score", 0.0),
#                     investment_thesis=recommendation.get("investment_thesis", "Analysis complete"),
#                     risk_assessment=recommendation.get("risk_assessment", "medium"),
#                     key_metrics=recommendation.get("key_metrics", {}),
#                     warnings=recommendation.get("warnings", [])
#                 )
                
#             except Exception as e:
#                 if "rate_limit" in str(e).lower():
#                     attempts += 1
#                     delay = config.RETRY_DELAY * (2 ** attempts)
#                     logger.warning(f"Rate limit hit for {ticker}. Retry {attempts}/{config.MAX_RETRIES} in {delay}s")
#                     time.sleep(delay)
#                 else:
#                     logger.error(f"Error processing {ticker}: {str(e)}")
#                     return InvestmentRecommendation(
#                         ticker=ticker,
#                         confidence_score=0.0,
#                         investment_thesis=f"Error: {str(e)}",
#                         risk_assessment="high",
#                         key_metrics={},
#                         warnings=["Processing error"]
#                     )
        
#         return InvestmentRecommendation(
#             ticker=ticker,
#             confidence_score=0.0,
#             investment_thesis="Failed after rate limit retries",
#             risk_assessment="high",
#             key_metrics={},
#             warnings=["Rate limit exceeded"]
#         )
    
#     async def process_tickers(self, tickers: list, criteria: dict) -> list:
#         """Process multiple tickers concurrently"""
#         tasks = [self.process_ticker(ticker, criteria) for ticker in tickers]
#         return await asyncio.gather(*tasks)

import asyncio
import time
import logging
import json
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from app.config import config
from app.agents.data_agent import DataAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.schemas import InvestmentRecommendation

logger = logging.getLogger(__name__)

class VerificationAgent:
    """Verifies recommendations against source data"""
    def verify(self, recommendation: Dict[str, Any], source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates recommendation metrics against source data"""
        warnings = recommendation.get('warnings', [])
        sources = recommendation.get('sources', [])
        
        # Metric verification
        metric_discrepancies = []
        for metric, rec_value in recommendation.get('key_metrics', {}).items():
            src_value = None
            for data_section in ['fundamentals', 'analyst_recommendations', 'key_metrics']:
                if data_section in source_data and metric in source_data[data_section]:
                    src_value = source_data[data_section][metric]
                    break
            
            if src_value and rec_value:
                try:
                    # Normalize values
                    rec_num = float(str(rec_value).replace('%', ''))
                    src_num = float(str(src_value).replace('%', ''))
                    
                    # Check for significant discrepancies (>5%)
                    if abs(rec_num - src_num) > 0.05 * src_num:
                        metric_discrepancies.append(metric)
                        sources.append(f"Discrepancy in {metric}: {rec_num} vs {src_num}")
                except ValueError:
                    if str(rec_value).lower() != str(src_value).lower():
                        metric_discrepancies.append(metric)
        
        if metric_discrepancies:
            warnings.append(f"Metric discrepancies: {', '.join(metric_discrepancies)}")
        
        # Confidence check
        if recommendation.get('confidence_score', 0) < config.MIN_CONFIDENCE:
            warnings.append(f"Low confidence ({recommendation['confidence_score']})")
        
        return {
            **recommendation,
            "warnings": warnings,
            "sources": sources
        }

class Orchestrator:
    def __init__(self):
        """Initialize with proper client tracking"""
        self._clients = []
        self.data_agent = self._init_agent(DataAgent)
        self.analysis_agent = self._init_agent(AnalysisAgent)
        self.recommendation_agent = self._init_agent(RecommendationAgent)
        self.verification_agent = VerificationAgent()
        self.cache = {}

    def _init_agent(self, agent_class):
        """Initialize agent and track its client"""
        agent = agent_class()
        if hasattr(agent, 'agent') and hasattr(agent.agent, 'client'):
            self._clients.append(agent.agent.client)
        return agent

    async def cleanup(self):
        """Explicitly clean up all resources"""
        for client in self._clients:
            try:
                if hasattr(client, 'close'):
                    client.close()
            except Exception as e:
                logger.error(f"Error closing client: {str(e)}")
        self._clients.clear()
        self.cache.clear()

    async def process_ticker(self, ticker: str, criteria: Dict[str, Any]) -> InvestmentRecommendation:
        """Process a single ticker with proper error handling"""
        logger.info(f"Processing {ticker} with criteria: {criteria}")
        
        # Create cache key
        cache_key = f"{ticker}-{json.dumps(criteria, sort_keys=True)}"
        if cache_key in self.cache:
            logger.info(f"Using cached result for {ticker}")
            return self.cache[cache_key]
        
        attempts = 0
        while attempts < config.MAX_RETRIES:
            try:
                # Step 1: Collect data
                company_data = self.data_agent.collect_data(ticker)
                if not company_data or "error" in company_data:
                    if ticker == "GOOGL":
                        company_data = self.data_agent.collect_data("GOOG") or \
                                      self.data_agent.collect_data("Alphabet")
                    if not company_data or "error" in company_data:
                        raise ValueError(f"Data collection failed for {ticker}")
                
                # Step 2: Analyze data
                analysis = self.analysis_agent.analyze(company_data, criteria)
                if not analysis or "error" in analysis:
                    raise ValueError(f"Analysis failed: {analysis.get('error', 'Unknown error')}")
                
                # Step 3: Generate recommendation
                recommendation = self.recommendation_agent.generate(analysis)
                if "error" in recommendation:
                    raise ValueError(f"Recommendation failed: {recommendation['error']}")
                
                # Step 4: Verify recommendation
                verified_rec = self.verification_agent.verify(recommendation, company_data)
                
                # Normalize risk assessment
                risk_assessment = verified_rec.get('risk_assessment', 'medium')
                if isinstance(risk_assessment, dict):
                    risk_assessment = risk_assessment.get('overall', 'medium')
                verified_rec['risk_assessment'] = str(risk_assessment).lower()
                if verified_rec['risk_assessment'] not in ['low', 'medium', 'high']:
                    verified_rec['risk_assessment'] = 'medium'
                
                # Add sources to thesis
                if verified_rec.get('sources'):
                    sources_str = "\nSources: " + "; ".join(verified_rec['sources'])[:250]
                    verified_rec['investment_thesis'] += sources_str
                
                # Create final result
                result = InvestmentRecommendation(
                    ticker=ticker,
                    confidence_score=verified_rec.get('confidence_score', 0.0),
                    investment_thesis=verified_rec.get('investment_thesis', 'Analysis complete'),
                    risk_assessment=verified_rec['risk_assessment'],
                    key_metrics=verified_rec.get('key_metrics', {}),
                    warnings=verified_rec.get('warnings', []),
                    sources=verified_rec.get('sources', [])
                )
                
                # Cache result
                self.cache[cache_key] = result
                return result
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    attempts += 1
                    delay = config.RETRY_DELAY * (2 ** attempts)
                    logger.warning(f"Rate limit hit. Retry {attempts}/{config.MAX_RETRIES} in {delay}s")
                    time.sleep(delay)
                else:
                    logger.error(f"Error processing {ticker}: {str(e)}")
                    return InvestmentRecommendation(
                        ticker=ticker,
                        confidence_score=0.0,
                        investment_thesis=f"Error: {str(e)}",
                        risk_assessment="high",
                        key_metrics={},
                        warnings=["Processing error"],
                        sources=[]
                    )
        
        return InvestmentRecommendation(
            ticker=ticker,
            confidence_score=0.0,
            investment_thesis="Rate limit exceeded",
            risk_assessment="high",
            key_metrics={},
            warnings=["Max retries reached"],
            sources=[]
        )

    async def process_tickers(self, tickers: List[str], criteria: Dict[str, Any]) -> List[InvestmentRecommendation]:
        """Process multiple tickers concurrently with cleanup"""
        try:
            tasks = [self.process_ticker(ticker, criteria) for ticker in tickers]
            return await asyncio.gather(*tasks)
        finally:
            await self.cleanup()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()