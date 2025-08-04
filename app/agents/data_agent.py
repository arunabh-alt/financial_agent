# from agno.agent import Agent
# from agno.tools.yfinance import YFinanceTools
# from app.config import config
# import json
# import time
# import logging
# from textblob import TextBlob 

# logger = logging.getLogger(__name__)

# class DataAgent:
#     def __init__(self):
#         self.agent = Agent(
#             name="Financial Data Agent",
#             role="Collect comprehensive financial data for SOFTWARE COMPANIES",
#             model=config.AGENT_CONFIG["data_agent"],
#             tools=[
#                 YFinanceTools(
#                     stock_price=True,
#                     analyst_recommendations=True,
#                     stock_fundamentals=True,
#                     company_news=True
#                 )
#             ],
#             instructions=[
#                 "Collect ONLY essential financial data for the given SOFTWARE COMPANY ticker",
#                 "Include ONLY: current price, P/E ratio, EPS, debt-to-equity, revenue growth, sentiment score",
#                 "For Google (GOOGL), use GOOG if data unavailable",
#                 "For each data point, if not available, return null",
#                 "Limit news to 3 most recent headlines (no full articles)",
#                 "Return data in compact JSON format",
#                 "Do NOT include historical price data",
#                 f"Keep response under {config.TOKEN_LIMITS['data_agent']} tokens",
#                 "Special cases:",
#                 "  - GOOGL: Use GOOG as fallback",
#                 "  - MSFT: Use Microsoft full name if needed"
#             ],
#             show_tool_calls=True
#         )
    
#     def collect_data(self, ticker: str) -> dict:
#         """Collect financial data for a single company"""
#         try:
#             # Special handling for Google
#             if ticker == "GOOGL":
#                 logger.info("Collecting Google data")
#                 # First try with GOOG
#                 response = self.agent.run(f"Collect financial data for GOOG")
#                 if not response or (isinstance(response, dict) and "error" in response):
#                     # Then try with full name
#                     response = self.agent.run(f"Get Alphabet Inc. (GOOGL) financial data")
#             else:
#                 response = self.agent.run(f"Collect financial data for {ticker}")
            
#             # Extract content
#             if hasattr(response, 'content'):
#                 content = response.content
#             elif hasattr(response, 'data'):
#                 content = response.data
#             else:
#                 content = response
            
#             # Parse JSON if string
#             if isinstance(content, str):
#                 try:
#                     return json.loads(content)
#                 except:
#                     return {"raw_response": content}
            
#             # Return directly if dict
#             if isinstance(content, dict):
#                 return content
            
#             return {"error": f"Unexpected response type: {type(content)}", "response": str(content)}
#         except Exception as e:
#             return {"error": str(e)}

from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from app.config import config
import json
import logging
from textblob import TextBlob  

logger = logging.getLogger(__name__)

class DataAgent:
    def __init__(self):
        self.agent = Agent(
            name="Financial Data Agent",
            role="Collect comprehensive financial data for SOFTWARE COMPANIES",
            model=config.AGENT_CONFIG["data_agent"],
            tools=[
                YFinanceTools(
                    stock_price=True,
                    analyst_recommendations=True,
                    stock_fundamentals=True,
                    company_news=True
                )
            ],
            instructions=[
                "Collect ONLY essential financial data for the given SOFTWARE COMPANY ticker",
                "Include ONLY: current price, P/E ratio, EPS, debt-to-equity, revenue growth, sentiment score",
                "For Google (GOOGL), use GOOG if data unavailable",
                "For each data point, if not available, return null",
                "Limit news to 3 most recent headlines (no full articles)",
                "Return data in compact JSON format",
                "Do NOT include historical price data",
                f"Keep response under {config.TOKEN_LIMITS['data_agent']} tokens",
                "Special cases:",
                "  - GOOGL: Use GOOG as fallback",
                "  - MSFT: Use Microsoft full name if needed"
            ],
            show_tool_calls=True
        )
    
    def collect_data(self, ticker: str) -> dict:
        """Collect financial data for a single company"""
        try:
            # Special handling for Google
            if ticker == "GOOGL":
                logger.info("Collecting Google data")
                # First try with GOOG
                response = self.agent.run(f"Collect financial data for GOOG")
                if not response or (isinstance(response, dict) and "error" in response):
                    # Then try with full name
                    response = self.agent.run(f"Get Alphabet Inc. (GOOGL) financial data")
            else:
                response = self.agent.run(f"Collect financial data for {ticker}")
            
            # Extract content
            if hasattr(response, 'content'):
                content = response.content
            elif hasattr(response, 'data'):
                content = response.data
            else:
                content = response
            
            # Parse JSON if string
            if isinstance(content, str):
                try:
                    parsed_content = json.loads(content)
                except:
                    parsed_content = {"raw_response": content}
            elif isinstance(content, dict):
                parsed_content = content
            else:
                parsed_content = {"error": f"Unexpected response type: {type(content)}", "response": str(content)}
            
            # Add sentiment analysis to news
            if 'news' in parsed_content and isinstance(parsed_content['news'], list):
                for news_item in parsed_content['news']:
                    if 'title' in news_item:
                        text = news_item['title']
                        if 'summary' in news_item and news_item['summary']:
                            text += " " + news_item['summary']
                        
                        # Perform sentiment analysis
                        analysis = TextBlob(text)
                        news_item['sentiment'] = {
                            'polarity': analysis.sentiment.polarity,
                            'subjectivity': analysis.sentiment.subjectivity
                        }
            
            return parsed_content
        except Exception as e:
            return {"error": str(e)}
    def close(self):
        """Close any resources used by this agent"""
        if hasattr(self.agent, 'client') and hasattr(self.agent.client, 'close'):
            try:
                self.agent.client.close()
            except Exception as e:
                logger.error(f"Error closing DataAgent client: {str(e)}")