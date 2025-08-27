import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter, NormalizedEvent

class ITAAdapter(BaseAdapter):
    """OSHA ITA (Injury Tracking Application) data adapter"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Mock ITA data - in reality this would come from OSHA's published CSV files
        self.mock_ita_data = [
            {
                "company_name": "ABC Construction LLC",
                "year": 2023,
                "naics": "236220",
                "state": "TX",
                "recordables": 8,
                "darts": 4,
                "hours_worked": 125000,
                "dart_rate": 6.4
            },
            {
                "company_name": "XYZ Roofing Inc",
                "year": 2023,
                "naics": "238160", 
                "state": "CA",
                "recordables": 3,
                "darts": 2,
                "hours_worked": 45000,
                "dart_rate": 8.9
            },
            {
                "company_name": "SafetyFirst Steel Co",
                "year": 2023,
                "naics": "238120",
                "state": "NY", 
                "recordables": 12,
                "darts": 8,
                "hours_worked": 200000,
                "dart_rate": 8.0
            },
            {
                "company_name": "QuickBuild Contractors",
                "year": 2023,
                "naics": "236210",
                "state": "FL",
                "recordables": 15,
                "darts": 10,
                "hours_worked": 180000,
                "dart_rate": 11.1
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
        
        for record in self.mock_ita_data:
            if companies and not any(company.lower() in record["company_name"].lower() for company in companies):
                continue
            
            # Convert year to datetime for the event
            event_date = datetime(record["year"], 12, 31)  # Use end of year as event date
            
            if since and event_date < since:
                continue
            if until and event_date > until:
                continue
            
            severity_score = self._calculate_ita_severity_score(record)
            
            event = NormalizedEvent(
                source="osha_ita",
                event_type="ita",
                company_name=self.normalize_company_name(record["company_name"]),
                occurred_on=event_date,
                severity_score=severity_score,
                data={
                    "year": record["year"],
                    "naics": record["naics"],
                    "state": record["state"],
                    "recordables": record["recordables"],
                    "darts": record["darts"],
                    "hours_worked": record["hours_worked"],
                    "dart_rate": record["dart_rate"],
                    "raw_company_name": record["company_name"]
                },
                link=f"https://osha.gov/ita/data/{record['year']}"
            )
            events.append(event)
        
        return events
    
    def _calculate_ita_severity_score(self, record: Dict[str, Any]) -> float:
        """Calculate severity based on DART rate compared to industry benchmarks"""
        dart_rate = record["dart_rate"]
        
        # Industry benchmark DART rates by NAICS (simplified)
        benchmarks = {
            "236220": 3.5,  # Commercial building construction
            "238160": 5.0,  # Roofing contractors
            "238120": 4.2,  # Structural steel contractors
            "236210": 4.8   # Industrial building construction
        }
        
        naics = record["naics"]
        benchmark = benchmarks.get(naics, 4.0)  # Default benchmark
        
        if dart_rate <= benchmark:
            return 10.0  # Below benchmark = low risk
        elif dart_rate <= benchmark * 1.5:
            return 30.0  # Moderately above benchmark
        elif dart_rate <= benchmark * 2.0:
            return 60.0  # Significantly above benchmark
        else:
            return 85.0  # Well above benchmark = high risk
    
    def parse_csv_file(self, csv_content: str) -> List[Dict[str, Any]]:
        """Parse ITA CSV data from uploaded file"""
        records = []
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in reader:
            try:
                record = {
                    "company_name": row.get("establishment_name", ""),
                    "year": int(row.get("year", 2023)),
                    "naics": row.get("naics", ""),
                    "state": row.get("state", ""),
                    "recordables": int(row.get("total_recordable_cases", 0)),
                    "darts": int(row.get("total_dart_cases", 0)),
                    "hours_worked": int(row.get("total_hours_worked", 0)),
                    "dart_rate": float(row.get("dart_rate", 0.0))
                }
                records.append(record)
            except (ValueError, TypeError) as e:
                print(f"Error parsing ITA CSV row: {e}")
                continue
        
        return records