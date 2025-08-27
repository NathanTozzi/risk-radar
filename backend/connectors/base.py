from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class NormalizedEvent:
    source: str
    event_type: str
    company_name: str
    occurred_on: datetime
    severity_score: float
    data: Dict[str, Any]
    link: Optional[str] = None
    project_name: Optional[str] = None
    location: Optional[str] = None

class BaseAdapter(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    async def pull(
        self, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        companies: Optional[List[str]] = None,
        projects: Optional[List[str]] = None
    ) -> List[NormalizedEvent]:
        pass
    
    def normalize_company_name(self, name: str) -> str:
        """Basic company name normalization"""
        import re
        name = name.strip().upper()
        name = re.sub(r'\b(INC|LLC|CORP|CO|LTD|LP|LLP)\.?$', '', name).strip()
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        return name