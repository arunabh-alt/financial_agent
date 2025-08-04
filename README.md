# Investment Recommendation Assistant

This project is an AI-powered API and web application that provides investment recommendations for software and technology companies based on financial metrics and market analysis. It leverages multiple agents for data collection, analysis, recommendation generation, and verification.

## Features

- **FastAPI backend** for serving recommendations via REST API.
- **Multi-agent architecture**: DataAgent, AnalysisAgent, RecommendationAgent, VerificationAgent.
- **Financial data collection** using [YFinanceTools](https://github.com/phidata/agno) and sentiment analysis.
- **Structured investment recommendations** with confidence scores, risk assessment, key metrics, and warnings.
- **Caching and retry logic** for robust API responses.
- **Web frontend** ([static/web_index.html](static/web_index.html)) for interactive user experience.
- **Test script** ([test.py](test.py)) for API validation.

## Directory Structure

```
Financial_Agent/
│
├── main.py                # FastAPI entrypoint
├── requirements.txt       # Python dependencies
├── .env                   # API keys and secrets
├── test.py                # API test script
├── README.md              # Project documentation
│
├── app/
│   ├── config.py          # Configuration and agent settings
│   ├── orchestrator.py    # Orchestrates agent workflow
│   ├── schemas.py         # Pydantic models for API and agents
│   ├── agents/
│   │   ├── data_agent.py          # Collects financial/company data
│   │   ├── analysis_agent.py      # Analyzes company data
│   │   ├── recommendation_agent.py# Generates investment recommendations
│   │   ├── verification_agent.py  # Verifies recommendations
│   │   └── __init__.py
│   └── __init__.py
│
├── static/
│   └── web_index.html     # Web UI for recommendations
└── .gitignore
```

## Setup

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd Financial_Agent
```

### 2. Install dependencies

Create a virtual environment and install required packages:

```sh
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API keys

Edit `.env` and provide your API keys for Agno, Groq, and OpenAI:

```
AGNO_API_KEY = <your-agno-key>
GROQ_API_KEY = <your-groq-key>
OPENAI_API_KEY = <your-openai-key>
```

### 4. Run the API server

```sh
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

### 5. Access the Web UI

Open [static/web_index.html](static/web_index.html) in your browser.  
**Note:** The web UI expects the API to be running locally at `/recommendations`.

## Usage

### API Endpoint

**POST** `/recommendations`

**Request Body:**
```json
{
  "tickers": ["AAPL", "MSFT"],
  "criteria": {
    "min_price": 100,
    "max_pe_ratio": 30,
    "max_debt_ratio": 0.5,
    "sectors": ["Technology", "Software"]
  }
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "ticker": "AAPL",
      "confidence_score": 0.85,
      "investment_thesis": "...",
      "risk_assessment": "medium",
      "key_metrics": { "pe_ratio": 28.5, "debt_to_equity": 0.45 },
      "warnings": [],
      "sources": []
    }
  ],
  "processing_time": 2.34
}
```

### Testing

Run the included test script to validate the API:

```sh
python test.py
```

## Agents Overview

- **DataAgent** ([app/agents/data_agent.py](app/agents/data_agent.py)): Collects financial data using YFinanceTools and sentiment analysis.
- **AnalysisAgent** ([app/agents/analysis_agent.py](app/agents/analysis_agent.py)): Analyzes company data against investor criteria.
- **RecommendationAgent** ([app/agents/recommendation_agent.py](app/agents/recommendation_agent.py)): Generates structured investment recommendations.
- **VerificationAgent** ([app/agents/verification_agent.py](app/agents/verification_agent.py)): Verifies recommendations against source data.

## Configuration

All agent models, token limits, and retry settings are managed in [app/config.py](app/config.py).

## Extending

- Add new agents in `app/agents/`.
- Update schemas in [app/schemas.py](app/schemas.py) for new fields.
- Customize frontend in [static/web_index.html](static/web_index.html).

## License

This project is for educational and informational purposes only.  
**Not financial advice.**

---

**Contact:**  
For questions or contributions, open an issue or