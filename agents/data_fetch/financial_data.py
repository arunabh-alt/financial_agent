import requests
from schemas.company_data import CompanyFinancials
from services.third_party.alpha_vantage import get_stock_data
from validation.cross_verifier import verify_financials

def fetch_company_financials(ticker: str) -> CompanyFinancials:
    # Get data from primary source
    primary_data = get_stock_data(ticker)
    
    # Cross-verify with secondary source
    verified_data = verify_financials(
        primary_data, 
        secondary_source="yahoo_finance"
    )
    
    if verified_data.discrepancy > 0.1:  # Threshold configurable
        raise ValueError(f"Data discrepancy detected for {ticker}")
    
    return CompanyFinancials(
        ticker=ticker,
        current_price=verified_data.price,
        pe_ratio=verified_data.pe_ratio
    )