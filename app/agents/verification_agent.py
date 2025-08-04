import logging
from app.schemas import InvestmentRecommendation

logger = logging.getLogger(__name__)

class VerificationAgent:
    def __init__(self):
        pass
    
    def verify(self, recommendation: dict, source_data: dict) -> dict:
        """Verify recommendation against source data"""
        warnings = recommendation.get('warnings', [])
        sources = recommendation.get('sources', [])
        
        # Metric verification
        metric_discrepancies = []
        for metric, rec_value in recommendation.get('key_metrics', {}).items():
            src_value = source_data.get('fundamentals', {}).get(metric)
            if src_value and rec_value and abs(rec_value - src_value) > 0.05 * src_value:
                metric_discrepancies.append(metric)
                sources.append(f"Source discrepancy in {metric}: Rec {rec_value} vs Source {src_value}")
        
        if metric_discrepancies:
            warnings.append(f"Metric discrepancies: {', '.join(metric_discrepancies)}")
        
        # Confidence check
        if recommendation.get('confidence_score', 0) < 0.7:
            warnings.append("Low confidence - human review recommended")
        
        return {
            **recommendation,
            "warnings": warnings,
            "sources": sources
        }