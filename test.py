import requests
import json
import time

def test_recommendations(ticker, custom_criteria=None):
    url = "http://localhost:8000/recommendations"
    
    # Default criteria for software companies
    criteria = {
        "min_price": 100,
        "sectors": ["Technology", "Software"],
        "max_pe_ratio": 30,
        "max_debt_ratio": 0.5,
        "min_revenue_growth": 0.1
    }
    
    # Merge with custom criteria if provided
    if custom_criteria:
        criteria.update(custom_criteria)
    
    payload = {
        "tickers": [ticker],
        "criteria": criteria
    }
    
    print(f"Testing {ticker} with criteria: {json.dumps(criteria, indent=2)}")
    
    start_time = time.time()
    response = requests.post(url, json=payload)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {data['processing_time']:.2f}s (client measured: {elapsed:.2f}s)")
        print("Recommendation:")
        print(json.dumps(data['recommendations'][0], indent=2))
    else:
        print(f"Status Code: {response.status_code}")
        print(f"Error: {response.text}")
    
    print("=" * 50)

if __name__ == "__main__":
    # Test with different companies
    test_recommendations("AAPL")
    test_recommendations("GOOGL")
    
    # Test with custom criteria
    custom_criteria = {
        "min_price": 50,
        "max_pe_ratio": 25,
        "min_revenue_growth": 0.15
    }
    test_recommendations("AMZN", custom_criteria)