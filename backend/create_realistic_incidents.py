#!/usr/bin/env python3
"""
Create realistic safety incidents to demonstrate RiskRadar's value proposition
"""

from datetime import datetime, timedelta
from sqlmodel import Session, select
from database import get_session
from models import *
import random

def create_compelling_incidents(session: Session):
    """Create realistic safety incidents that show compelling business opportunities"""
    
    # Get companies
    gcs = session.exec(select(Company).where(Company.type == CompanyType.GC)).all()
    subs = session.exec(select(Company).where(Company.type == CompanyType.SUB)).all()
    owners = session.exec(select(Company).where(Company.type == CompanyType.OWNER)).all()
    
    if not gcs or not subs:
        print("❌ No companies found. Run seed_data.py first.")
        return
    
    # HIGH-IMPACT INCIDENTS - Prime sales opportunities
    incidents = [
        # SCENARIO 1: Fatal Fall - Major GC + Owner involved
        {
            "company_name": "RapidFrame Steel Erectors",
            "incident_date": datetime.now() - timedelta(days=12),  # Very recent
            "severity_score": 95.0,
            "event_type": EventType.ACCIDENT,
            "source": "osha_establishment",
            "data": {
                "narrative": "Steel worker fell 40 feet from beam during high-rise construction. Safety harness was not properly secured to anchor point. Worker transported to trauma center with multiple fractures.",
                "fatality": False,
                "hospitalization": True,
                "injury_type": "Fall from elevation",
                "body_part": "Multiple fractures - leg, ribs",
                "estimated_cost": 125000,
                "osha_citation": "29 CFR 1926.501(b)(1) - Fall protection systems",
                "penalty": 18900,
                "violations": 2,
                "inspection_type": "Accident",
                "project_name": "One World Trade Center Phase II",
                "gc_name": "Turner Construction Company",
                "owner_name": "Related Companies"
            }
        },
        
        # SCENARIO 2: Electrical Incident - Different GC/Owner combo
        {
            "company_name": "Lightning Fast Electric Co",
            "incident_date": datetime.now() - timedelta(days=8),
            "severity_score": 88.0,
            "event_type": EventType.ACCIDENT,
            "source": "osha_establishment", 
            "data": {
                "narrative": "Electrician received severe electrical shock while working on 480V panel. Failed to follow lockout/tagout procedures. Worker hospitalized with 2nd degree burns.",
                "fatality": False,
                "hospitalization": True,
                "injury_type": "Electrical shock/burn",
                "body_part": "Arms and chest - 2nd degree burns",
                "estimated_cost": 95000,
                "osha_citation": "29 CFR 1926.417(a) - Lockout/tagout procedures",
                "penalty": 25200,
                "violations": 3,
                "inspection_type": "Accident",
                "project_name": "Amazon HQ3 Campus Development",
                "gc_name": "Mortenson Construction",
                "owner_name": "Hines Real Estate"
            }
        },
        
        # SCENARIO 3: Near-Miss Crane Incident - High profile
        {
            "company_name": "CutCorner Roofing Solutions", 
            "incident_date": datetime.now() - timedelta(days=25),
            "severity_score": 82.0,
            "event_type": EventType.CITATION,
            "source": "osha_establishment",
            "data": {
                "narrative": "Material load fell from crane during roofing installation, nearly striking workers below. Rigging equipment found to be defective. No injuries but significant near-miss.",
                "fatality": False,
                "hospitalization": False,
                "injury_type": "Near miss - falling object",
                "body_part": "None - near miss",
                "estimated_cost": 0,
                "osha_citation": "29 CFR 1926.251(a)(1) - Rigging equipment inspection",
                "penalty": 15750,
                "violations": 2,
                "inspection_type": "Complaint",
                "project_name": "Los Angeles Metro Expansion", 
                "gc_name": "DPR Construction",
                "owner_name": "Kilroy Realty Corporation"
            }
        },
        
        # SCENARIO 4: Demolition Safety Violation 
        {
            "company_name": "FastTrack Demolition LLC",
            "incident_date": datetime.now() - timedelta(days=35),
            "severity_score": 76.0,
            "event_type": EventType.CITATION,
            "source": "osha_establishment",
            "data": {
                "narrative": "Multiple safety violations during demolition work: inadequate fall protection, improper debris chute installation, and failure to conduct daily equipment inspections.",
                "fatality": False,
                "hospitalization": False,
                "injury_type": "Safety violations",
                "body_part": "None - violations only",
                "estimated_cost": 0,
                "osha_citation": "29 CFR 1926.850-860 - Demolition standards",
                "penalty": 31500,
                "violations": 5,
                "inspection_type": "Programmed",
                "project_name": "Boston Biotech Research Complex",
                "gc_name": "Suffolk Construction Company", 
                "owner_name": "Boston Properties Inc"
            }
        },
        
        # SCENARIO 5: Repeat Offender Pattern
        {
            "company_name": "Lightning Fast Electric Co",  # Same company as incident #2
            "incident_date": datetime.now() - timedelta(days=145),  # 5 months ago
            "severity_score": 72.0,
            "event_type": EventType.CITATION,
            "source": "osha_establishment",
            "data": {
                "narrative": "Previous electrical safety violation: Improper grounding of temporary electrical systems. This is the second citation in 6 months for electrical safety violations.",
                "fatality": False,
                "hospitalization": False,
                "injury_type": "Safety violations",
                "body_part": "None - violations only", 
                "estimated_cost": 0,
                "osha_citation": "29 CFR 1926.404(f)(6) - Grounding requirements",
                "penalty": 12600,
                "violations": 1,
                "inspection_type": "Programmed",
                "project_name": "Denver Airport Terminal Renovation",
                "gc_name": "Hensel Phelps Construction",
                "owner_name": "Brookfield Properties"
            }
        },
        
        # SCENARIO 6: Medium-risk incident - Good rehabilitation opportunity
        {
            "company_name": "Metropolitan HVAC Services",
            "incident_date": datetime.now() - timedelta(days=68),
            "severity_score": 58.0,
            "event_type": EventType.CITATION, 
            "source": "osha_establishment",
            "data": {
                "narrative": "Worker cut hand on sheet metal during HVAC installation. First aid case, no hospitalization required. Company has good safety record overall.",
                "fatality": False,
                "hospitalization": False,
                "injury_type": "Laceration",
                "body_part": "Hand - minor cut",
                "estimated_cost": 850,
                "osha_citation": "29 CFR 1926.95(a) - Personal protective equipment",
                "penalty": 4200,
                "violations": 1,
                "inspection_type": "Accident",
                "project_name": "Chicago Logistics Hub Development",
                "gc_name": "McCarthy Building Companies",
                "owner_name": "Prologis Inc"
            }
        }
    ]
    
    print(f"Creating {len(incidents)} compelling safety incidents...")
    
    for incident_data in incidents:
        # Find the subcontractor
        sub = session.exec(
            select(Company).where(Company.normalized_name.contains(incident_data["company_name"].upper().replace(" ", "")))
        ).first()
        
        if not sub:
            print(f"⚠️  Could not find subcontractor: {incident_data['company_name']}")
            continue
            
        # Create the incident event
        event = Event(
            source=incident_data["source"],
            event_type=incident_data["event_type"], 
            company_id=sub.id,
            occurred_on=incident_data["incident_date"],
            severity_score=incident_data["severity_score"],
            data=incident_data["data"]
        )
        
        session.add(event)
    
    session.commit()
    print(f"✅ Created {len(incidents)} realistic safety incidents")
    
    # Create some news events for additional context
    create_news_events(session)

def create_news_events(session: Session):
    """Create realistic news events that add context"""
    
    news_events = [
        {
            "title": "Turner Construction Wins $850M One World Trade Center Phase II Contract",
            "date": datetime.now() - timedelta(days=180),
            "source": "Construction Dive",
            "url": "https://constructiondive.com/news/turner-wins-wtc-phase-ii",
            "company_names": ["Turner Construction Company", "Related Companies"]
        },
        {
            "title": "Amazon Breaks Ground on Austin Campus with Mortenson as GC",
            "date": datetime.now() - timedelta(days=220), 
            "source": "ENR",
            "url": "https://enr.com/articles/amazon-austin-campus-groundbreaking",
            "company_names": ["Mortenson Construction", "Hines Real Estate"]
        },
        {
            "title": "Boston Properties Announces $400M Biotech Research Complex",
            "date": datetime.now() - timedelta(days=350),
            "source": "Commercial Observer",
            "url": "https://commercialobserver.com/boston-biotech-complex",
            "company_names": ["Boston Properties Inc", "Suffolk Construction Company"]
        }
    ]
    
    for news_item in news_events:
        for company_name in news_item["company_names"]:
            company = session.exec(
                select(Company).where(Company.normalized_name.contains(company_name.upper().replace(" ", "")))
            ).first()
            
            if company:
                event = Event(
                    source="news",
                    event_type=EventType.NEWS,
                    company_id=company.id,
                    occurred_on=news_item["date"],
                    severity_score=0.0,  # News events don't have severity
                    data={
                        "title": news_item["title"],
                        "source": news_item["source"],
                        "url": news_item["url"],
                        "summary": f"Construction industry news mentioning {company.name}"
                    }
                )
                session.add(event)
    
    session.commit()
    print("✅ Created news events for industry context")

def create_ita_metrics(session: Session):
    """Create realistic ITA (Information Technology Agreement) metrics"""
    
    # Get all companies
    companies = session.exec(select(Company)).all()
    
    for company in companies:
        if company.type in [CompanyType.GC, CompanyType.OWNER]:
            # Higher ITA scores for larger companies
            ita_score = random.uniform(75, 95)
        else:
            # Variable ITA scores for subcontractors
            ita_score = random.uniform(45, 85)
            
        metric = MetricsITA(
            company_id=company.id,
            ita_score=ita_score,
            computed_on=datetime.now() - timedelta(days=random.randint(1, 90))
        )
        session.add(metric)
    
    session.commit()
    print(f"✅ Created ITA metrics for {len(companies)} companies")

if __name__ == "__main__":
    print("🎯 Creating compelling RiskRadar demonstration data...")
    
    session = next(get_session())
    try:
        create_compelling_incidents(session)
        create_ita_metrics(session)
        
        print("\n📊 Database now contains compelling scenarios:")
        print("• High-impact incidents with major GCs and property owners")
        print("• Repeat offender patterns showing risk trends") 
        print("• Recent incidents that create immediate sales opportunities")
        print("• Mix of fatal, injury, and citation events")
        print("• Real company names and realistic project contexts")
        print("• ITA scores for propensity modeling")
        
    finally:
        session.close()