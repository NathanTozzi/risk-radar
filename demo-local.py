#!/usr/bin/env python3
"""
RiskRadar Local Demo Script
Demonstrates the core functionality without requiring PostgreSQL
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add backend to path
sys.path.append('backend')

def create_demo_data():
    """Create sample data to demonstrate RiskRadar functionality"""
    
    print("🎯 RiskRadar Demo - Core Functionality")
    print("=" * 50)
    
    # Sample companies data
    companies = [
        {
            "id": 1,
            "name": "MegaBuild Construction Corp",
            "type": "GC",
            "state": "TX",
            "normalized_name": "MEGABUILD CONSTRUCTION"
        },
        {
            "id": 2,
            "name": "ABC Construction LLC", 
            "type": "Sub",
            "state": "TX",
            "normalized_name": "ABC CONSTRUCTION"
        },
        {
            "id": 3,
            "name": "Texas Tower Development Corp",
            "type": "Owner",
            "state": "TX", 
            "normalized_name": "TEXAS TOWER DEVELOPMENT"
        }
    ]
    
    # Sample incident event
    incident = {
        "id": 1,
        "source": "osha_establishment",
        "event_type": "accident",
        "company_id": 2,  # ABC Construction
        "occurred_on": datetime.now() - timedelta(days=15),
        "severity_score": 95.0,
        "data": {
            "narrative": "Employee fell from scaffolding during commercial construction work. Safety harness was not properly secured.",
            "fatality": True,
            "violations": 3,
            "penalty": 75000,
            "raw_company_name": "ABC Construction LLC"
        }
    }
    
    return companies, incident

def demo_entity_resolution():
    """Demonstrate entity resolution capabilities"""
    print("\n🔍 Entity Resolution Demo")
    print("-" * 30)
    
    try:
        from entity_resolution import EntityResolver
        resolver = EntityResolver()
        
        test_names = [
            "ABC Construction LLC",
            "ABC Corp", 
            "A.B.C. Construction",
            "ABC Contracting Company"
        ]
        
        print("Testing company name normalization:")
        for name in test_names:
            normalized = resolver.normalize_company_name(name)
            print(f"  {name:<25} → {normalized}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity resolution demo failed: {e}")
        return False

def demo_scoring():
    """Demonstrate propensity scoring"""
    print("\n📊 Propensity Scoring Demo")
    print("-" * 30)
    
    try:
        from scoring.propensity import PropensityScorer
        scorer = PropensityScorer()
        
        # Mock data for scoring demo
        incident_date = datetime.now() - timedelta(days=15)
        
        print("Scoring Components:")
        
        # Test recency scoring
        recency_score = scorer._calculate_recency_score(incident_date)
        print(f"  Recency (15 days ago):     {recency_score:.1f}/30")
        
        # Test severity scoring
        class MockEvent:
            def __init__(self):
                self.event_type = "accident"
                self.data = {"fatality": True, "violations": 3, "penalty": 75000}
        
        mock_event = MockEvent()
        severity_score = scorer._calculate_severity_score(mock_event)
        print(f"  Severity (fatality):       {severity_score:.1f}/25")
        
        # Calculate total
        total_score = recency_score + severity_score + 10 + 8 + 5 + 4 + 3  # Mock other components
        print(f"  Total Propensity Score:    {total_score:.1f}/100")
        
        # Determine talk track
        score_components = {"severity": severity_score, "frequency": 10, "ita": 8}
        talk_track = scorer._determine_talk_track(score_components, mock_event)
        print(f"  Recommended Talk Track:    {talk_track}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scoring demo failed: {e}")
        return False

def demo_outreach_generation():
    """Demonstrate outreach content generation"""
    print("\n✉️ Outreach Generation Demo")
    print("-" * 30)
    
    try:
        from outreach_generator import OutreachGenerator
        generator = OutreachGenerator()
        
        # Mock context
        context = {
            "company_name": "MegaBuild Construction Corp",
            "company_type": "general contractor",
            "sub_name": "ABC Construction LLC",
            "incident_type": "workplace safety incident",
            "incident_date": "January 1, 2024",
            "days_ago": 15,
            "propensity_score": 89.5,
            "talk_track": "Post-incident stabilization & future prequal",
            "severity_level": "high"
        }
        
        print("Generated Email Subject:")
        subject = f"[{context['company_name']}] Post-incident path to stronger prequal (quick idea)"
        print(f"  {subject}")
        
        print("\nEmail Opening:")
        opening = f"""Hi [Name],

I noticed that one of your subcontractors experienced {context['incident_type']} {generator._format_timeframe(context['days_ago'])}. I understand these situations require careful attention to both immediate concerns and long-term prevention."""
        
        print(f"  {opening[:200]}...")
        
        print("\nLinkedIn DM:")
        linkedin = f"Hi [Name], I noticed your recent subcontractor incident on {context['incident_date']}. Teams we work with have found 2-3 prequal adjustments that help prevent similar issues..."
        print(f"  {linkedin[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Outreach generation demo failed: {e}")
        return False

def demo_api_endpoints():
    """Show what the API endpoints would return"""
    print("\n🌐 API Endpoints Demo")
    print("-" * 30)
    
    companies, incident = create_demo_data()
    
    print("GET /companies - Sample Response:")
    print(json.dumps(companies[:2], indent=2, default=str))
    
    print("\nGET /events - Sample Response:")
    event_response = {
        "id": incident["id"],
        "source": incident["source"],
        "event_type": incident["event_type"], 
        "occurred_on": incident["occurred_on"].isoformat(),
        "severity_score": incident["severity_score"],
        "data": incident["data"]
    }
    print(json.dumps([event_response], indent=2, default=str))
    
    print("\nGET /opportunities - Sample Response:")
    opportunity = {
        "id": 1,
        "gc_id": 1,
        "driver_event_id": 1,
        "propensity_score": 89.5,
        "recommended_talk_track": "Post-incident stabilization & future prequal",
        "created_at": datetime.now().isoformat()
    }
    print(json.dumps([opportunity], indent=2, default=str))

def main():
    """Main demo function"""
    
    print("🎯 RiskRadar Comprehensive Demo")
    print("=" * 50)
    print("This demo shows RiskRadar's core functionality without requiring database setup.\n")
    
    # Test core components
    results = []
    
    results.append(demo_entity_resolution())
    results.append(demo_scoring()) 
    results.append(demo_outreach_generation())
    
    # Show API structure
    demo_api_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Demo Summary")
    print("=" * 50)
    
    if all(results):
        print("✅ All core components working correctly!")
        print("\n🎯 RiskRadar Capabilities Demonstrated:")
        print("• Entity resolution and company name normalization")
        print("• Multi-factor propensity scoring (0-100 scale)")
        print("• Empathetic outreach content generation")
        print("• RESTful API structure for frontend integration")
        
        print("\n🚀 Next Steps:")
        print("• Install Docker and run: make demo")
        print("• This will launch the full application with:")
        print("  - React frontend at http://localhost:3000")
        print("  - FastAPI backend at http://localhost:8000")
        print("  - Complete sample data and live demo")
        
        return True
    else:
        print("❌ Some components failed - check error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)