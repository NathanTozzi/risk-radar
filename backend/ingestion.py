import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session
from database import get_session
from models import Company, Event, CompanyType, EventType
from connectors import (
    MockOshaEstablishmentAdapter,
    MockOshaAccidentAdapter, 
    MockNewsAdapter,
    ITAAdapter
)

class IngestionService:
    def __init__(self):
        self.adapters = {
            "osha_establishment": MockOshaEstablishmentAdapter(),
            "osha_accidents": MockOshaAccidentAdapter(),
            "news": MockNewsAdapter(),
            "ita": ITAAdapter()
        }
    
    async def run_ingestion(
        self,
        sources: List[str],
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        companies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run data ingestion from specified sources"""
        results = {
            "total_events": 0,
            "new_companies": 0,
            "sources_processed": [],
            "errors": []
        }
        
        with Session(next(get_session())) as session:
            for source in sources:
                if source not in self.adapters:
                    results["errors"].append(f"Unknown source: {source}")
                    continue
                
                try:
                    adapter = self.adapters[source]
                    events = await adapter.pull(since=since, until=until, companies=companies)
                    
                    for event in events:
                        # Find or create company
                        company = self._find_or_create_company(session, event.company_name, event.data)
                        
                        # Create event record
                        db_event = Event(
                            source=event.source,
                            event_type=EventType(event.event_type),
                            company_id=company.id,
                            occurred_on=event.occurred_on,
                            severity_score=event.severity_score,
                            data=event.data,
                            link=event.link
                        )
                        session.add(db_event)
                        results["total_events"] += 1
                    
                    session.commit()
                    results["sources_processed"].append(source)
                    
                except Exception as e:
                    results["errors"].append(f"Error processing {source}: {str(e)}")
                    session.rollback()
        
        return results
    
    def _find_or_create_company(self, session: Session, normalized_name: str, event_data: Dict[str, Any]) -> Company:
        """Find existing company or create new one"""
        # Try to find existing company by normalized name
        from sqlmodel import select
        statement = select(Company).where(Company.normalized_name == normalized_name)
        company = session.exec(statement).first()
        
        if company:
            return company
        
        # Create new company
        company_type = self._infer_company_type(event_data.get("raw_company_name", normalized_name))
        
        company = Company(
            name=event_data.get("raw_company_name", normalized_name),
            normalized_name=normalized_name,
            type=company_type,
            naics=event_data.get("naics"),
            state=event_data.get("state")
        )
        session.add(company)
        session.flush()  # Get the ID
        return company
    
    def _infer_company_type(self, company_name: str) -> CompanyType:
        """Infer company type from name patterns"""
        name_lower = company_name.lower()
        
        # Simple heuristics for company type
        if any(word in name_lower for word in ["construction", "contracting", "contractor", "builders"]):
            return CompanyType.GC
        elif any(word in name_lower for word in ["roofing", "steel", "demolition", "electric", "plumbing"]):
            return CompanyType.SUB
        elif any(word in name_lower for word in ["development", "properties", "real estate", "corp"]):
            return CompanyType.OWNER
        else:
            return CompanyType.UNKNOWN