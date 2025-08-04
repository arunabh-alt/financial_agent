# import json  # Add this import at the top
# import logging
# from agno.agent import Agent
# from app.config import config

# logger = logging.getLogger(__name__)

# class AnalysisAgent:
#     def __init__(self):
#         self.agent = Agent(
#             name="Financial Analysis Agent",
#             role="Analyze company data and identify key investment metrics",
#             model=config.AGENT_CONFIG["analysis_agent"],
#             instructions=[
#                 "Analyze the provided company data",
#                 "Identify key financial metrics: P/E ratio, debt-to-equity, revenue growth, etc.",
#                 "Assess risk factors based on news sentiment and analyst recommendations",
#                 "Generate a summary of financial health and risks",
#                 "Output in concise JSON format"
#             ],
#             show_tool_calls=False
#         )
    
#     def analyze(self, company_data: dict, criteria: dict) -> dict:
#         """Analyze company data against investment criteria"""
#         try:
#             # Create prompt
#             prompt = f"Analyze this company data based on investor criteria:\n\n{json.dumps(company_data)}\n\nCriteria:\n{json.dumps(criteria)}"
            
#             # Get response
#             response = self.agent.run(prompt)
            
#             # Extract content
#             if hasattr(response, 'content'):
#                 return response.content
#             elif hasattr(response, 'data'):
#                 return response.data
#             elif isinstance(response, dict):
#                 return response
#             elif isinstance(response, str):
#                 try:
#                     return json.loads(response)
#                 except:
#                     return {"analysis": response}
            
#             return {"error": f"Unexpected response type: {type(response)}"}
#         except Exception as e:
#             return {"error": str(e)}

import json
import logging
from agno.agent import Agent
from app.config import config

logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self):
        self.agent = Agent(
            name="Financial Analysis Agent",
            role="Analyze company data and identify key investment metrics",
            model=config.AGENT_CONFIG["analysis_agent"],
            instructions=[
                "Analyze the provided company data",
                "Identify key financial metrics: P/E ratio, debt-to-equity, revenue growth, etc.",
                "Assess risk factors based on news sentiment and analyst recommendations",
                "Generate a summary of financial health and risks",
                "Output in concise JSON format",
                "Include 'criteria_violations' array for unmet user criteria"
            ],
            show_tool_calls=False
        )
    
    def analyze(self, company_data: dict, criteria: dict) -> dict:
        """Analyze company data against investment criteria"""
        try:
            # Create enhanced prompt with explicit criteria matching
            prompt = (
                f"Analyze this company data based on investor criteria:\n\n"
                f"{json.dumps(company_data)}\n\n"
                f"Criteria:\n{json.dumps(criteria)}\n\n"
                "Explicitly check these user criteria:\n"
                f"- Max P/E ratio: {criteria.get('max_pe', 'N/A')}\n"
                f"- Min revenue growth: {criteria.get('min_revenue_growth', 'N/A')}\n"
                f"- Max debt-to-equity: {criteria.get('max_debt_equity', 'N/A')}\n"
                "Include 'criteria_violations' array in output for any unmet criteria"
            )
            
            # Get response
            response = self.agent.run(prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'data'):
                return response.data
            elif isinstance(response, dict):
                return response
            elif isinstance(response, str):
                try:
                    return json.loads(response)
                except:
                    return {"analysis": response}
            
            return {"error": f"Unexpected response type: {type(response)}"}
        except Exception as e:
            return {"error": str(e)}
    def close(self):
        """Close any resources used by this agent"""
        if hasattr(self.agent, 'client') and hasattr(self.agent.client, 'close'):
            try:
                self.agent.client.close()
            except Exception as e:
                logger.error(f"Error closing DataAgent client: {str(e)}")