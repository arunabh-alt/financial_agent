# import json
# import logging
# import re
# from agno.agent import Agent
# from app.config import config

# logger = logging.getLogger(__name__)

# class RecommendationAgent:
#     def __init__(self):
#         self.agent = Agent(
#             name="Investment Recommendation Agent",
#             role="Generate structured investment recommendations for software companies",
#             model=config.AGENT_CONFIG["recommendation_agent"],
#             instructions=[
#                 "Generate investment recommendations based on financial analysis of SOFTWARE COMPANIES",
#                 "Output MUST be in valid JSON format with these REQUIRED keys:",
#                 "confidence_score (0-1), investment_thesis (string), risk_assessment (string), key_metrics (object), warnings (array)",
#                 "risk_assessment must be one of: 'low', 'medium', or 'high' (lowercase string only)",
#                 "warnings must be an array of strings, even if empty",
#                 "Example format:",
#                 '''{
#                     "confidence_score": 0.85,
#                     "investment_thesis": "Strong growth potential...",
#                     "risk_assessment": "medium",
#                     "key_metrics": {
#                         "pe_ratio": 25.3,
#                         "debt_to_equity": 0.45,
#                         "revenue_growth": 0.12
#                     },
#                     "warnings": ["High P/E ratio", "Competitive market"]
#                 }'''
#             ],
#             show_tool_calls=False
#         )
    
#     def close(self):
#         """Clean up resources"""
#         if hasattr(self.agent, 'client'):
#             try:
#                 self.agent.client.close()
#             except Exception as e:
#                 logger.error(f"Error closing RecommendationAgent client: {str(e)}")

#     def generate(self, analysis: str) -> dict:
#         """Generate investment recommendation from analysis"""
#         try:
#             response = self.agent.run(
#                 f"Convert this financial analysis into a structured investment recommendation:\n{analysis}",
#                 max_tokens=500
#             )
            
#             # Extract content
#             content = response
#             if hasattr(response, 'content'):
#                 content = response.content
#             elif hasattr(response, 'data'):
#                 content = response.data
            
#             # 1. First try to parse as JSON
#             if isinstance(content, str):
#                 try:
#                     parsed = json.loads(content)
#                     return self._normalize_recommendation(parsed)
#                 except json.JSONDecodeError:
#                     pass
            
#             # 2. Try to extract JSON block
#             if isinstance(content, str):
#                 try:
#                     json_str = re.search(r'\{.*\}', content, re.DOTALL)
#                     if json_str:
#                         parsed = json.loads(json_str.group())
#                         return self._normalize_recommendation(parsed)
#                 except Exception:
#                     pass
            
#             # 3. Fallback: Safe extraction
#             return self._create_fallback_recommendation(content)
                
#         except Exception as e:
#             logger.error(f"Recommendation generation failed: {str(e)}")
#             return {
#                 "error": str(e),
#                 "confidence_score": 0.0,
#                 "investment_thesis": f"Generation error: {str(e)}",
#                 "risk_assessment": "high",
#                 "key_metrics": {},
#                 "warnings": ["Processing failure"]
#             }
    
#     def _normalize_recommendation(self, rec: dict) -> dict:
#         """Ensure recommendation has correct structure and types"""
#         # Ensure risk_assessment is a string
#         if isinstance(rec.get("risk_assessment"), dict):
#             rec["risk_assessment"] = rec["risk_assessment"].get("overall", "medium")
#         elif not isinstance(rec.get("risk_assessment"), str):
#             rec["risk_assessment"] = "medium"
        
#         # Force lowercase for risk assessment
#         if "risk_assessment" in rec:
#             rec["risk_assessment"] = rec["risk_assessment"].lower()
#             if rec["risk_assessment"] not in ["low", "medium", "high"]:
#                 rec["risk_assessment"] = "medium"
        
#         # Ensure warnings is a list
#         if "warnings" not in rec:
#             rec["warnings"] = []
#         elif not isinstance(rec["warnings"], list):
#             if isinstance(rec["warnings"], str):
#                 rec["warnings"] = [rec["warnings"]]
#             else:
#                 rec["warnings"] = []
        
#         # Ensure confidence score is valid
#         if "confidence_score" not in rec:
#             rec["confidence_score"] = 0.7
#         else:
#             try:
#                 rec["confidence_score"] = float(rec["confidence_score"])
#                 rec["confidence_score"] = max(0.0, min(1.0, rec["confidence_score"]))
#             except (ValueError, TypeError):
#                 rec["confidence_score"] = 0.7
        
#         return rec
    
#     def _create_fallback_recommendation(self, content) -> dict:
#         """Create a safe recommendation when parsing fails"""
#         return {
#             "confidence_score": 0.7,
#             "investment_thesis": str(content)[:500] if content else "No content generated",
#             "risk_assessment": "medium",
#             "key_metrics": {},
#             "warnings": ["Response formatting issue"]
#         }

import json
import logging
from agno.agent import Agent
from app.config import config

logger = logging.getLogger(__name__)

class RecommendationAgent:
    def __init__(self):
        self.agent = Agent(
            name="Investment Recommendation Agent",
            role="Generate structured investment recommendations",
            model=config.AGENT_CONFIG["recommendation_agent"],
            instructions=[
                "You MUST output valid JSON with these EXACT fields:",
                "- confidence_score: number between 0-1",
                "- investment_thesis: string",
                "- risk_assessment: string (only 'low', 'medium', or 'high')",
                "- key_metrics: object",
                "- warnings: array of strings",
                "Example:",
                '''{
                    "confidence_score": 0.8,
                    "investment_thesis": "The company shows strong growth...",
                    "risk_assessment": "medium",
                    "key_metrics": {"pe_ratio": 25},
                    "warnings": []
                }'''
            ],
            show_tool_calls=False
        )

    def generate(self, analysis: str) -> dict:
        try:
            response = self.agent.run(analysis)
            content = self._extract_content(response)
            recommendation = self._parse_content(content)
            return self._validate_recommendation(recommendation)
        except Exception as e:
            logger.error(f"Recommendation error: {str(e)}")
            return self._create_error_response(str(e))

    def _extract_content(self, response):
        if hasattr(response, 'content'):
            return response.content
        elif hasattr(response, 'data'):
            return response.data
        return response

    def _parse_content(self, content):
        if isinstance(content, dict):
            return content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}

    def _validate_recommendation(self, rec):
        # Ensure all required fields exist
        rec.setdefault("confidence_score", 0.7)
        rec.setdefault("investment_thesis", "Analysis complete")
        rec.setdefault("key_metrics", {})
        rec.setdefault("warnings", [])
        
        # Force risk_assessment to be a valid string
        risk = rec.get("risk_assessment", "medium")
        if isinstance(risk, dict):
            risk = risk.get("overall", "medium")
        rec["risk_assessment"] = str(risk).lower()
        if rec["risk_assessment"] not in ["low", "medium", "high"]:
            rec["risk_assessment"] = "medium"
            
        return rec

    def _create_error_response(self, error):
        return {
            "confidence_score": 0.0,
            "investment_thesis": f"Error: {error}",
            "risk_assessment": "high",
            "key_metrics": {},
            "warnings": ["Processing error"]
        }

    def close(self):
        if hasattr(self, 'agent') and hasattr(self.agent, 'client'):
            try:
                self.agent.client.close()
            except Exception as e:
                logger.error(f"Error closing client: {str(e)}")