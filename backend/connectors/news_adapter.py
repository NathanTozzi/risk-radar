import feedparser
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .base import BaseAdapter, NormalizedEvent

class MockNewsAdapter(BaseAdapter):
    """Mock news adapter with construction industry incident articles"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.mock_articles = [
            {
                "title": "ABC Construction Cited for Safety Violations After Jobsite Incident",
                "url": "https://constructionnews.com/abc-construction-violations",
                "summary": "Local construction company faces OSHA penalties following workplace accident that injured two workers.",
                "publish_date": datetime.now() - timedelta(days=3),
                "company_mentions": ["ABC Construction LLC"],
                "keywords": ["safety violations", "jobsite accident", "OSHA penalties"]
            },
            {
                "title": "Subcontractor Default Delays Major Downtown Project",
                "url": "https://localnews.com/project-delay",
                "summary": "A subcontractor's sudden departure from a $50M commercial project has left the general contractor scrambling for replacements.",
                "publish_date": datetime.now() - timedelta(days=12),
                "company_mentions": ["QuickBuild Contractors", "Downtown Development Corp"],
                "keywords": ["subcontractor default", "project delay", "commercial construction"]
            },
            {
                "title": "Steel Erection Accident Shuts Down Construction Site",
                "url": "https://safetynews.com/steel-accident",
                "summary": "Work halted after steel beam fell during high-rise construction, prompting safety investigation.",
                "publish_date": datetime.now() - timedelta(days=18),
                "company_mentions": ["SafetyFirst Steel Co"],
                "keywords": ["steel erection", "construction accident", "safety investigation"]
            },
            {
                "title": "Roofing Contractor Faces Lawsuit Over Quality Issues",
                "url": "https://legalnews.com/roofing-lawsuit",
                "summary": "Property owner files suit claiming defective roof installation led to water damage in new building.",
                "publish_date": datetime.now() - timedelta(days=35),
                "company_mentions": ["XYZ Roofing Inc"],
                "keywords": ["quality issues", "defective installation", "lawsuit"]
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
        
        for article in self.mock_articles:
            if since and article["publish_date"] < since:
                continue
            if until and article["publish_date"] > until:
                continue
            
            # Check if any of the mentioned companies match our search criteria
            relevant_companies = article["company_mentions"]
            if companies:
                relevant_companies = [comp for comp in relevant_companies 
                                   if any(search_comp.lower() in comp.lower() for search_comp in companies)]
                if not relevant_companies:
                    continue
            
            # Create events for each mentioned company
            for company_name in relevant_companies:
                severity_score = self._calculate_severity_score(article)
                
                event = NormalizedEvent(
                    source="news_rss",
                    event_type="news",
                    company_name=self.normalize_company_name(company_name),
                    occurred_on=article["publish_date"],
                    severity_score=severity_score,
                    data={
                        "title": article["title"],
                        "summary": article["summary"],
                        "keywords": article["keywords"],
                        "all_mentions": article["company_mentions"],
                        "raw_company_name": company_name
                    },
                    link=article["url"]
                )
                events.append(event)
        
        return events
    
    def _calculate_severity_score(self, article: Dict[str, Any]) -> float:
        base_score = 15.0
        
        # Increase score based on negative keywords
        high_impact_keywords = ["fatality", "death", "lawsuit", "violation", "accident", "default"]
        medium_impact_keywords = ["delay", "quality issues", "investigation", "citation"]
        
        title_lower = article["title"].lower()
        summary_lower = article["summary"].lower()
        keywords_text = " ".join(article["keywords"]).lower()
        
        all_text = f"{title_lower} {summary_lower} {keywords_text}"
        
        for keyword in high_impact_keywords:
            if keyword in all_text:
                base_score += 15
        
        for keyword in medium_impact_keywords:
            if keyword in all_text:
                base_score += 8
        
        return min(base_score, 100.0)

class RealNewsAdapter(BaseAdapter):
    """Real RSS news adapter for construction industry feeds"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.rss_feeds = config.get("rss_feeds", [
            "https://feeds.construction.com/news/rss",
            "https://www.constructionequipment.com/rss",
            "https://www.enr.com/rss/all"
        ])
        self.throttle_ms = config.get("throttle_ms", 1000)
    
    async def pull(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        companies: Optional[List[str]] = None,
        projects: Optional[List[str]] = None
    ) -> List[NormalizedEvent]:
        events = []
        
        for feed_url in self.rss_feeds:
            try:
                await asyncio.sleep(self.throttle_ms / 1000)
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # Parse publication date
                    pub_date = datetime.fromtimestamp(entry.published_parsed) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                    
                    if since and pub_date < since:
                        continue
                    if until and pub_date > until:
                        continue
                    
                    # Extract company mentions (basic implementation)
                    company_mentions = self._extract_company_mentions(entry, companies)
                    
                    if not company_mentions:
                        continue
                    
                    for company_name in company_mentions:
                        event = NormalizedEvent(
                            source="news_rss",
                            event_type="news",
                            company_name=self.normalize_company_name(company_name),
                            occurred_on=pub_date,
                            severity_score=self._calculate_news_severity(entry),
                            data={
                                "title": entry.title,
                                "summary": getattr(entry, 'summary', ''),
                                "feed_url": feed_url,
                                "raw_company_name": company_name
                            },
                            link=entry.link
                        )
                        events.append(event)
            
            except Exception as e:
                print(f"Error processing RSS feed {feed_url}: {e}")
                continue
        
        return events
    
    def _extract_company_mentions(self, entry, target_companies: Optional[List[str]] = None) -> List[str]:
        """Extract company names from news entry"""
        mentions = []
        text = f"{entry.title} {getattr(entry, 'summary', '')}"
        
        if target_companies:
            for company in target_companies:
                if company.lower() in text.lower():
                    mentions.append(company)
        
        return mentions
    
    def _calculate_news_severity(self, entry) -> float:
        """Calculate severity score based on news content"""
        text = f"{entry.title} {getattr(entry, 'summary', '')}".lower()
        
        base_score = 10.0
        negative_keywords = ["accident", "violation", "death", "injury", "lawsuit", "default", "delay"]
        
        for keyword in negative_keywords:
            if keyword in text:
                base_score += 10
        
        return min(base_score, 100.0)