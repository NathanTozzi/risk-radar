#!/usr/bin/env python3
"""
Display the compelling RiskRadar scenarios for demo purposes
"""

from sqlmodel import Session, select
from database import get_session
from models import *
from datetime import datetime, timedelta
import json

def show_demo_scenarios():
    """Display the key scenarios that demonstrate RiskRadar's value"""
    
    session = next(get_session())
    
    print("🎯 RiskRadar Demo Scenarios")
    print("=" * 60)
    
    # Get recent high-severity incidents
    recent_incidents = session.exec(
        select(Event, Company)
        .join(Company)
        .where(Event.severity_score > 75)
        .where(Event.occurred_on > datetime.now() - timedelta(days=60))
        .order_by(Event.severity_score.desc())
    ).all()
    
    print(f"\n🚨 HIGH-PRIORITY SALES OPPORTUNITIES ({len(recent_incidents)} recent incidents)")
    print("-" * 60)
    
    for event, company in recent_incidents:
        data = event.data or {}
        days_ago = (datetime.now() - event.occurred_on).days
        
        print(f"\n📊 SCORE: {event.severity_score}/100 | {days_ago} days ago")
        print(f"🏢 Subcontractor: {company.name}")
        print(f"🏗️  Project: {data.get('project_name', 'Unknown')}")
        print(f"👷 GC: {data.get('gc_name', 'Unknown')}")
        print(f"🏛️  Owner: {data.get('owner_name', 'Unknown')}")
        print(f"💥 Incident: {data.get('injury_type', 'Safety incident')}")
        
        if data.get('penalty'):
            print(f"💰 OSHA Penalty: ${data['penalty']:,}")
        
        # Determine talk track
        if event.severity_score > 90:
            talk_track = "🎯 POST-INCIDENT CRISIS MANAGEMENT"
            print(f"📞 Talk Track: {talk_track}")
            print("   → Immediate risk mitigation consultation")
            print("   → Enhanced prequal requirements discussion")
        elif event.severity_score > 80:
            talk_track = "🎯 PREVENTIVE SAFETY ENHANCEMENT"
            print(f"📞 Talk Track: {talk_track}")
            print("   → Safety program improvement consultation")
            print("   → Future incident prevention strategies")
        else:
            talk_track = "🎯 PROACTIVE RISK MANAGEMENT"
            print(f"📞 Talk Track: {talk_track}")
            print("   → Safety performance benchmarking")
            print("   → Best practices sharing")
    
    # Show repeat offender patterns
    repeat_offenders = session.exec(
        select(Company.name, Event.company_id)
        .join(Event)
        .where(Event.occurred_on > datetime.now() - timedelta(days=180))
        .where(Event.severity_score > 60)
    ).all()
    
    from collections import Counter
    repeat_counts = Counter([company_name for company_name, _ in repeat_offenders])
    repeat_offenders_list = [(name, count) for name, count in repeat_counts.items() if count > 1]
    
    if repeat_offenders_list:
        print(f"\n🔄 REPEAT OFFENDER PATTERNS")
        print("-" * 60)
        for company_name, incident_count in sorted(repeat_offenders_list, key=lambda x: x[1], reverse=True):
            print(f"⚠️  {company_name}: {incident_count} incidents in last 6 months")
            print("   → High-priority target for enhanced prequal discussion")
    
    # Show high-value project contexts
    print(f"\n🏗️  HIGH-VALUE PROJECT CONTEXTS")
    print("-" * 60)
    
    major_projects = [
        ("One World Trade Center Phase II", "New York, NY", "$850M", "Turner Construction", "Related Companies"),
        ("Amazon HQ3 Campus Development", "Austin, TX", "$1.2B", "Mortenson Construction", "Hines Real Estate"),
        ("Boston Biotech Research Complex", "Boston, MA", "$400M", "Suffolk Construction", "Boston Properties"),
        ("Los Angeles Metro Expansion", "Los Angeles, CA", "$680M", "DPR Construction", "Kilroy Realty"),
        ("Denver Airport Terminal Renovation", "Denver, CO", "$320M", "Hensel Phelps", "Brookfield Properties")
    ]
    
    for project_name, location, value, gc, owner in major_projects:
        print(f"\n🏗️  {project_name}")
        print(f"   📍 Location: {location}")  
        print(f"   💰 Value: {value}")
        print(f"   👷 GC: {gc}")
        print(f"   🏛️  Owner: {owner}")
    
    print(f"\n📈 BUSINESS IMPACT SUMMARY")
    print("-" * 60)
    print("• Target Audience: Risk Management, Procurement, Safety Directors")
    print("• Decision Makers: VPs of Risk Management, Chief Safety Officers")
    print("• Average Deal Size: $50K - $250K annually per major GC/Owner")
    print("• Sales Cycle: 3-6 months for new accounts, 30-60 days for add-ons")
    print("• Use Cases: Enhanced prequal, safety training, risk assessment")
    
    session.close()

if __name__ == "__main__":
    show_demo_scenarios()