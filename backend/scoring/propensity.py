import math
import yaml
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import Company, Event, TargetOpportunity, SubRelationship, MetricsITA
import os

class PropensityScorer:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load scoring configuration from YAML file"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "benchmarks.yaml")
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default config if file not found
            return {
                "dart_benchmarks": {"default": 4.0},
                "high_risk_trades": ["steel erection", "roofing", "excavation"],
                "scoring_config": {
                    "recency_decay_half_life_days": 90,
                    "max_recency_days": 180,
                    "severity_weights": {
                        "fatality": 50.0,
                        "catastrophe": 35.0,
                        "serious_violation": 25.0
                    }
                }
            }
    
    def calculate_propensity_score(
        self, 
        session: Session, 
        company: Company, 
        driver_event: Event
    ) -> Tuple[float, List[str], str]:
        """
        Calculate propensity score for a GC/Owner based on subcontractor incident
        
        Returns:
            - propensity_score: 0-100 
            - why_summary: List of bullet points explaining the score
            - talk_track: Recommended approach angle
        """
        score_components = {}
        why_points = []
        
        # Component 1: Incident recency (0-30 points)
        recency_score = self._calculate_recency_score(driver_event.occurred_on)
        score_components["recency"] = recency_score
        if recency_score > 20:
            why_points.append(f"Recent incident ({self._days_ago(driver_event.occurred_on)} days ago)")
        
        # Component 2: Incident severity (0-25 points)
        severity_score = self._calculate_severity_score(driver_event)
        score_components["severity"] = severity_score
        severity_desc = self._get_severity_description(driver_event)
        if severity_desc:
            why_points.append(f"High severity: {severity_desc}")
        
        # Component 3: Frequency - multiple incidents (0-15 points)
        frequency_score = self._calculate_frequency_score(session, company, driver_event)
        score_components["frequency"] = frequency_score
        if frequency_score > 5:
            why_points.append(f"Multiple incidents in past 24 months")
        
        # Component 4: ITA lagging indicators (0-15 points)
        ita_score = self._calculate_ita_score(session, company, driver_event)
        score_components["ita"] = ita_score
        if ita_score > 8:
            why_points.append("Subcontractor DART rate above industry benchmark")
        
        # Component 5: High-risk trades (0-5 points)
        trade_score = self._calculate_trade_risk_score(session, company, driver_event)
        score_components["trade_risk"] = trade_score
        if trade_score > 0:
            why_points.append("Involves high-risk trades")
        
        # Component 6: Relationship certainty (0-5 points)
        relationship_score = self._calculate_relationship_score(session, company, driver_event)
        score_components["relationship"] = relationship_score
        
        # Component 7: News negativity (0-5 points)
        news_score = self._calculate_news_score(driver_event)
        score_components["news"] = news_score
        if news_score > 2:
            why_points.append("Negative media coverage")
        
        # Calculate total score
        total_score = sum(score_components.values())
        
        # Determine talk track
        talk_track = self._determine_talk_track(score_components, driver_event)
        
        return min(total_score, 100.0), why_points, talk_track
    
    def _calculate_recency_score(self, occurred_on: datetime) -> float:
        """Calculate score based on how recent the incident was (0-30 points)"""
        days_ago = (datetime.now() - occurred_on).days
        max_days = self.config["scoring_config"]["recency_decay_half_life_days"] * 2
        
        if days_ago <= 30:
            return 30.0
        elif days_ago <= max_days:
            # Logistic decay
            decay_factor = math.exp(-days_ago / self.config["scoring_config"]["recency_decay_half_life_days"])
            return 30.0 * decay_factor
        else:
            return 0.0
    
    def _calculate_severity_score(self, event: Event) -> float:
        """Calculate score based on incident severity (0-25 points)"""
        severity_weights = self.config["scoring_config"]["severity_weights"]
        data = event.data
        
        if data.get("fatality"):
            return severity_weights.get("fatality", 25.0)
        elif data.get("catastrophe"):
            return severity_weights.get("catastrophe", 20.0)
        elif data.get("severity_type") == "Willful":
            return severity_weights.get("willful_violation", 20.0)
        elif data.get("severity_type") == "Serious":
            return severity_weights.get("serious_violation", 15.0)
        elif data.get("penalty", 0) > 50000:
            return 20.0  # High penalty indicates serious violation
        elif data.get("violations", 0) >= 5:
            return 15.0  # Multiple violations
        else:
            return severity_weights.get("other_than_serious", 5.0)
    
    def _calculate_frequency_score(self, session: Session, company: Company, driver_event: Event) -> float:
        """Calculate score based on frequency of incidents (0-15 points)"""
        cutoff_date = datetime.now() - timedelta(days=730)  # 24 months
        
        # Find the sub involved in the driver event
        sub_id = driver_event.company_id
        
        # Count incidents for this sub in the past 24 months
        incident_count = session.exec(
            select(Event).where(
                Event.company_id == sub_id,
                Event.occurred_on >= cutoff_date,
                Event.event_type.in_(["inspection", "citation", "accident"])
            )
        ).all()
        
        count = len(incident_count)
        if count >= 5:
            return 15.0
        elif count >= 3:
            return 10.0
        elif count >= 2:
            return 5.0
        else:
            return 0.0
    
    def _calculate_ita_score(self, session: Session, company: Company, driver_event: Event) -> float:
        """Calculate score based on ITA metrics vs benchmarks (0-15 points)"""
        sub_id = driver_event.company_id
        
        # Get most recent ITA metrics for the sub
        ita_metrics = session.exec(
            select(MetricsITA).where(MetricsITA.sub_id == sub_id)
            .order_by(MetricsITA.year.desc())
        ).first()
        
        if not ita_metrics or not ita_metrics.dart_rate:
            return 0.0
        
        # Get benchmark for the sub's NAICS
        sub_company = session.get(Company, sub_id)
        naics = sub_company.naics if sub_company else None
        benchmark = self.config["dart_benchmarks"].get(naics, 4.0)
        
        dart_rate = ita_metrics.dart_rate
        ratio = dart_rate / benchmark
        
        if ratio >= 2.0:
            return 15.0
        elif ratio >= 1.5:
            return 10.0
        elif ratio >= 1.2:
            return 5.0
        else:
            return 0.0
    
    def _calculate_trade_risk_score(self, session: Session, company: Company, driver_event: Event) -> float:
        """Calculate score based on high-risk trades involvement (0-5 points)"""
        high_risk_trades = self.config["high_risk_trades"]
        sub_id = driver_event.company_id
        
        # Check sub relationships for trade information
        relationships = session.exec(
            select(SubRelationship).where(SubRelationship.sub_id == sub_id)
        ).all()
        
        for relationship in relationships:
            if relationship.trade:
                for risk_trade in high_risk_trades:
                    if risk_trade.lower() in relationship.trade.lower():
                        return 5.0
        
        # Check event data for trade keywords
        event_text = f"{driver_event.data.get('narrative', '')} {' '.join(driver_event.data.get('keywords', []))}".lower()
        for risk_trade in high_risk_trades:
            if risk_trade.lower() in event_text:
                return 3.0
        
        return 0.0
    
    def _calculate_relationship_score(self, session: Session, company: Company, driver_event: Event) -> float:
        """Calculate score based on relationship certainty (0-5 points)"""
        sub_id = driver_event.company_id
        
        # Find relationships between this sub and the target company
        relationships = session.exec(
            select(SubRelationship).where(
                SubRelationship.sub_id == sub_id,
                (SubRelationship.gc_id == company.id) | (SubRelationship.owner_id == company.id)
            )
        ).all()
        
        if len(relationships) >= 2:
            return 5.0  # Multiple confirmed relationships
        elif len(relationships) == 1:
            rel = relationships[0]
            if rel.project_id and rel.start_date and rel.end_date:
                return 4.0  # Detailed relationship info
            else:
                return 2.0  # Basic relationship
        else:
            return 0.0  # No confirmed relationship
    
    def _calculate_news_score(self, event: Event) -> float:
        """Calculate score based on negative news coverage (0-5 points)"""
        if event.event_type != "news":
            return 0.0
        
        title = event.data.get("title", "").lower()
        summary = event.data.get("summary", "").lower()
        
        negative_keywords = ["lawsuit", "violation", "death", "fatality", "accident", "injury", "default", "delay", "penalty"]
        
        score = 0.0
        for keyword in negative_keywords:
            if keyword in title:
                score += 2.0
            elif keyword in summary:
                score += 1.0
        
        return min(score, 5.0)
    
    def _get_severity_description(self, event: Event) -> Optional[str]:
        """Get human-readable severity description"""
        data = event.data
        
        if data.get("fatality"):
            return "Fatality incident"
        elif data.get("catastrophe"):
            return "Catastrophic incident"
        elif data.get("severity_type") == "Willful":
            return "Willful OSHA violation"
        elif data.get("penalty", 0) > 100000:
            return f"High penalty (${data['penalty']:,})"
        elif data.get("violations", 0) >= 5:
            return f"Multiple violations ({data['violations']})"
        
        return None
    
    def _determine_talk_track(self, score_components: Dict[str, float], driver_event: Event) -> str:
        """Determine recommended talk track based on scoring components"""
        templates = self.config.get("talk_track_templates", {})
        
        if score_components.get("severity", 0) > 20:
            return templates.get("post_incident", "Post-incident stabilization")
        elif score_components.get("frequency", 0) > 10:
            return templates.get("trend_analysis", "Trend analysis & prevention")
        elif score_components.get("ita", 0) > 10:
            return templates.get("portfolio_risk", "Portfolio risk benchmarking")
        else:
            return templates.get("compliance_gaps", "Compliance gap assessment")
    
    def _days_ago(self, date: datetime) -> int:
        """Calculate days ago from given date"""
        return (datetime.now() - date).days
    
    def rebuild_opportunities(
        self, 
        session: Session, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Rebuild all target opportunities based on recent events"""
        results = {"created": 0, "updated": 0, "errors": []}
        
        try:
            # Get recent high-severity events
            event_query = select(Event).where(Event.severity_score >= 15.0)
            if since:
                event_query = event_query.where(Event.occurred_on >= since)
            if until:
                event_query = event_query.where(Event.occurred_on <= until)
            
            events = session.exec(event_query.order_by(Event.occurred_on.desc())).all()
            
            for event in events:
                try:
                    # Find GCs/Owners associated with this sub
                    sub_id = event.company_id
                    relationships = session.exec(
                        select(SubRelationship).where(SubRelationship.sub_id == sub_id)
                    ).all()
                    
                    for relationship in relationships:
                        for company_id in [relationship.gc_id, relationship.owner_id]:
                            if not company_id:
                                continue
                            
                            company = session.get(Company, company_id)
                            if not company:
                                continue
                            
                            # Calculate propensity score
                            score, why_summary, talk_track = self.calculate_propensity_score(session, company, event)
                            
                            if score >= 30.0:  # Only create opportunities for meaningful scores
                                # Check if opportunity already exists
                                existing = session.exec(
                                    select(TargetOpportunity).where(
                                        (TargetOpportunity.gc_id == company_id) if relationship.gc_id == company_id else (TargetOpportunity.owner_id == company_id),
                                        TargetOpportunity.driver_event_id == event.id
                                    )
                                ).first()
                                
                                if existing:
                                    existing.propensity_score = score
                                    existing.recommended_talk_track = talk_track
                                    results["updated"] += 1
                                else:
                                    opportunity = TargetOpportunity(
                                        gc_id=company_id if relationship.gc_id == company_id else None,
                                        owner_id=company_id if relationship.owner_id == company_id else None,
                                        driver_event_id=event.id,
                                        propensity_score=score,
                                        confidence=0.8,
                                        recommended_talk_track=talk_track
                                    )
                                    session.add(opportunity)
                                    results["created"] += 1
                
                except Exception as e:
                    results["errors"].append(f"Error processing event {event.id}: {str(e)}")
            
            session.commit()
            
        except Exception as e:
            results["errors"].append(f"Rebuild error: {str(e)}")
            session.rollback()
        
        return results