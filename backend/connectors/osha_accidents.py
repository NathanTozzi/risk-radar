import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .base import BaseAdapter, NormalizedEvent

class MockOshaAccidentAdapter(BaseAdapter):
    """Mock OSHA Accident/Investigation adapter with realistic incident data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.mock_data = [
            {
                "company_name": "ABC Construction LLC",
                "incident_date": datetime.now() - timedelta(days=8),
                "narrative": "Employee fell from scaffolding during commercial construction work. Safety harness was not properly secured.",
                "fatality": False,
                "catastrophe": False,
                "keywords": ["fall", "scaffolding", "safety harness"]
            },
            {
                "company_name": "Danger Zone Demolition",
                "incident_date": datetime.now() - timedelta(days=22),
                "narrative": "Worker struck by heavy machinery during building demolition. Multiple safety protocols were not followed.",
                "fatality": True,
                "catastrophe": False,
                "keywords": ["struck by", "heavy machinery", "demolition", "fatality"]
            },
            {
                "company_name": "QuickBuild Contractors",
                "incident_date": datetime.now() - timedelta(days=67),
                "narrative": "Crane collapse during high-rise construction resulted in multiple injuries. Equipment maintenance records under investigation.",
                "fatality": False,
                "catastrophe": True,
                "keywords": ["crane collapse", "multiple injuries", "equipment maintenance"]
            }
        ]
    
    async def pull(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        companies: Optional[List[str]] = None,
        projects: Optional[List[str]] = None
    ) -> List[NormalizedEvent]:
        events = []
        
        for record in self.mock_data:
            if since and record["incident_date"] < since:
                continue
            if until and record["incident_date"] > until:
                continue
            if companies and not any(company.lower() in record["company_name"].lower() for company in companies):
                continue
            
            severity_score = self._calculate_severity_score(record)
            
            event = NormalizedEvent(
                source="osha_accidents",
                event_type="accident",
                company_name=self.normalize_company_name(record["company_name"]),
                occurred_on=record["incident_date"],
                severity_score=severity_score,
                data={
                    "narrative": record["narrative"],
                    "fatality": record["fatality"],
                    "catastrophe": record["catastrophe"],
                    "keywords": record["keywords"],
                    "raw_company_name": record["company_name"]
                },
                link=f"https://osha.gov/accidents/{record['company_name'].replace(' ', '_')}"
            )
            events.append(event)
        
        return events
    
    def _calculate_severity_score(self, record: Dict[str, Any]) -> float:
        base_score = 30.0
        
        if record["fatality"]:
            base_score = 95.0
        elif record["catastrophe"]:
            base_score = 80.0
        
        # Add points for high-risk keywords
        risk_keywords = ["fall", "struck by", "crane", "collapse", "machinery", "fatality"]
        keyword_score = sum(5 for keyword in record["keywords"] if any(risk in keyword.lower() for risk in risk_keywords))
        
        return min(base_score + keyword_score, 100.0)

class RealOshaAccidentAdapter(BaseAdapter):
    """Real OSHA Accident/Investigation adapter - would scrape from actual OSHA database"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = "https://www.osha.gov/pls/imis/accidentsearch.search"
        self.throttle_ms = config.get("throttle_ms", 3000)
    
    async def pull(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        companies: Optional[List[str]] = None,
        projects: Optional[List[str]] = None
    ) -> List[NormalizedEvent]:
        print("WARNING: Real OSHA accident adapter not fully implemented. Use MockOshaAccidentAdapter for testing.")
        return []