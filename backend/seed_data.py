import asyncio
from datetime import datetime, timedelta
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import *
from ingestion import IngestionService
from scoring import PropensityScorer
from outreach_generator import OutreachGenerator

async def seed_database():
    """Seed database with comprehensive sample data"""
    
    print("🌱 Starting database seeding...")
    
    # Create tables
    create_db_and_tables()
    
    # Get session
    session = next(get_session())
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        for kit in session.exec(select(OutreachKit)).all():
            session.delete(kit)
        for opp in session.exec(select(TargetOpportunity)).all():
            session.delete(opp)
        for event in session.exec(select(Event)).all():
            session.delete(event)
        for rel in session.exec(select(SubRelationship)).all():
            session.delete(rel)
        for metric in session.exec(select(MetricsITA)).all():
            session.delete(metric)
        for alias in session.exec(select(CompanyAlias)).all():
            session.delete(alias)
        for project in session.exec(select(Project)).all():
            session.delete(project)
        for company in session.exec(select(Company)).all():
            session.delete(company)
        session.commit()
        
        # Create companies
        print("Creating companies...")
        companies = create_companies(session)
        
        # Create projects
        print("Creating projects...")
        projects = create_projects(session, companies)
        
        # Create relationships
        print("Creating subcontractor relationships...")
        create_relationships(session, companies, projects)
        
        # Create ITA metrics
        print("Creating ITA metrics...")
        create_ita_metrics(session, companies)
        
        # Create realistic incidents instead of running complex ingestion
        print("Creating compelling safety incidents...")
        try:
            import subprocess
            import sys
            result = subprocess.run([sys.executable, "create_realistic_incidents.py"], 
                                  capture_output=True, text=True, cwd="/app")
            if result.returncode == 0:
                print("✅ Realistic incidents created successfully")
            else:
                print(f"⚠️  Incident creation had issues: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Could not create incidents: {e}")
            print("Continuing with basic seed data...")
        
        # Generate target opportunities
        print("Generating target opportunities...")
        scorer = PropensityScorer()
        scorer.rebuild_opportunities(session)
        
        # Generate some outreach kits
        print("Generating sample outreach kits...")
        generate_sample_outreach_kits(session)
        
        print("✅ Database seeding completed successfully!")
        print(f"📊 Created {len(companies)} companies, {len(projects)} projects")
        
        # Show summary stats
        show_summary_stats(session)
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def create_companies(session: Session) -> dict:
    """Create realistic sample companies with compelling use cases"""
    
    # Major General Contractors (High-value targets)
    gcs = [
        Company(name="Turner Construction Company", type=CompanyType.GC, naics="236220", state="NY", website="https://turnerconstruction.com", normalized_name="TURNER CONSTRUCTION"),
        Company(name="Skanska USA Building Inc", type=CompanyType.GC, naics="236210", state="NY", website="https://skanska.com", normalized_name="SKANSKA USA BUILDING"),
        Company(name="Clark Construction Group", type=CompanyType.GC, naics="236220", state="MD", website="https://clarkconstruction.com", normalized_name="CLARK CONSTRUCTION GROUP"),
        Company(name="Mortenson Construction", type=CompanyType.GC, naics="236220", state="MN", website="https://mortenson.com", normalized_name="MORTENSON CONSTRUCTION"),
        Company(name="Suffolk Construction Company", type=CompanyType.GC, naics="236210", state="MA", website="https://suffolkco.com", normalized_name="SUFFOLK CONSTRUCTION"),
        Company(name="Hensel Phelps Construction", type=CompanyType.GC, naics="236220", state="CO", website="https://henselphelps.com", normalized_name="HENSEL PHELPS CONSTRUCTION"),
        Company(name="McCarthy Building Companies", type=CompanyType.GC, naics="236210", state="MO", website="https://mccarthy.com", normalized_name="MCCARTHY BUILDING COMPANIES"),
        Company(name="DPR Construction", type=CompanyType.GC, naics="236220", state="CA", website="https://dpr.com", normalized_name="DPR CONSTRUCTION")
    ]
    
    # Major Property Owners/Developers (High-value targets)
    owners = [
        Company(name="Brookfield Properties", type=CompanyType.OWNER, naics="531110", state="NY", website="https://brookfieldproperties.com", normalized_name="BROOKFIELD PROPERTIES"),
        Company(name="Hines Real Estate", type=CompanyType.OWNER, naics="531110", state="TX", website="https://hines.com", normalized_name="HINES REAL ESTATE"),
        Company(name="Related Companies", type=CompanyType.OWNER, naics="531110", state="NY", website="https://related.com", normalized_name="RELATED COMPANIES"),
        Company(name="Boston Properties Inc", type=CompanyType.OWNER, naics="531110", state="MA", website="https://bostonproperties.com", normalized_name="BOSTON PROPERTIES"),
        Company(name="Kilroy Realty Corporation", type=CompanyType.OWNER, naics="531110", state="CA", website="https://kilroyrealty.com", normalized_name="KILROY REALTY"),
        Company(name="Prologis Inc", type=CompanyType.OWNER, naics="531120", state="CA", website="https://prologis.com", normalized_name="PROLOGIS")
    ]
    
    # Subcontractors with realistic risk profiles
    subs = [
        # HIGH-RISK: Recent serious incidents - Prime targets for outreach
        Company(name="RapidFrame Steel Erectors", type=CompanyType.SUB, naics="238120", state="TX", normalized_name="RAPIDFRAME STEEL ERECTORS"),
        Company(name="Lightning Fast Electric Co", type=CompanyType.SUB, naics="238210", state="FL", normalized_name="LIGHTNING FAST ELECTRIC"),
        Company(name="CutCorner Roofing Solutions", type=CompanyType.SUB, naics="238160", state="CA", normalized_name="CUTCORNER ROOFING SOLUTIONS"),
        Company(name="FastTrack Demolition LLC", type=CompanyType.SUB, naics="238910", state="NY", normalized_name="FASTTRACK DEMOLITION"),
        
        # MEDIUM-RISK: Some violations, good rehabilitation opportunities  
        Company(name="Metropolitan HVAC Services", type=CompanyType.SUB, naics="238220", state="NY", normalized_name="METROPOLITAN HVAC SERVICES"),
        Company(name="Precision Concrete Contractors", type=CompanyType.SUB, naics="238110", state="CA", normalized_name="PRECISION CONCRETE CONTRACTORS"),
        Company(name="Reliable Plumbing Systems", type=CompanyType.SUB, naics="238220", state="TX", normalized_name="RELIABLE PLUMBING SYSTEMS"),
        Company(name="Advanced Electrical Solutions", type=CompanyType.SUB, naics="238210", state="MA", normalized_name="ADVANCED ELECTRICAL SOLUTIONS"),
        
        # LOW-RISK: Minimal issues, good safety records
        Company(name="Premier Finishing Contractors", type=CompanyType.SUB, naics="238320", state="CA", normalized_name="PREMIER FINISHING CONTRACTORS"),
        Company(name="Elite Mechanical Systems", type=CompanyType.SUB, naics="238220", state="NY", normalized_name="ELITE MECHANICAL SYSTEMS"),
        Company(name="SafeBuild Construction Services", type=CompanyType.SUB, naics="238990", state="FL", normalized_name="SAFEBUILD CONSTRUCTION SERVICES"),
        Company(name="Quality First Contractors", type=CompanyType.SUB, naics="238320", state="TX", normalized_name="QUALITY FIRST CONTRACTORS")
    ]
    
    all_companies = gcs + owners + subs
    
    for company in all_companies:
        session.add(company)
    session.commit()
    
    # Create some aliases
    aliases = [
        CompanyAlias(company_id=all_companies[0].id, alias="MegaBuild Corp", confidence=0.9),
        CompanyAlias(company_id=all_companies[0].id, alias="MegaBuild Construction", confidence=0.8),
        CompanyAlias(company_id=all_companies[10].id, alias="ABC Contracting", confidence=0.7),
        CompanyAlias(company_id=all_companies[10].id, alias="ABC Construction Company", confidence=0.8),
    ]
    
    for alias in aliases:
        session.add(alias)
    session.commit()
    
    return {
        "gcs": gcs,
        "owners": owners, 
        "subs": subs,
        "all": all_companies
    }

def create_projects(session: Session, companies: dict) -> list:
    """Create realistic high-value projects"""
    
    projects = [
        # Major commercial developments - High value targets
        Project(
            name="One World Trade Center Phase II", 
            location="New York, NY",
            owner_id=companies["owners"][2].id,  # Related Companies
            gc_id=companies["gcs"][0].id,        # Turner Construction
            start_date=datetime(2023, 2, 1),
            end_date=datetime(2025, 8, 30)
        ),
        Project(
            name="Amazon HQ3 Campus Development",
            location="Austin, TX", 
            owner_id=companies["owners"][1].id,  # Hines Real Estate
            gc_id=companies["gcs"][3].id,        # Mortenson Construction
            start_date=datetime(2023, 1, 15),
            end_date=datetime(2025, 12, 31)
        ),
        Project(
            name="Boston Biotech Research Complex",
            location="Boston, MA",
            owner_id=companies["owners"][3].id,  # Boston Properties
            gc_id=companies["gcs"][4].id,        # Suffolk Construction
            start_date=datetime(2022, 8, 1),
            end_date=datetime(2024, 4, 30)
        ),
        Project(
            name="Los Angeles Metro Expansion",
            location="Los Angeles, CA",
            owner_id=companies["owners"][4].id,  # Kilroy Realty
            gc_id=companies["gcs"][7].id,        # DPR Construction
            start_date=datetime(2023, 6, 1),
            end_date=datetime(2026, 3, 15)
        ),
        Project(
            name="Denver Airport Terminal Renovation",
            location="Denver, CO", 
            owner_id=companies["owners"][0].id,  # Brookfield Properties
            gc_id=companies["gcs"][5].id,        # Hensel Phelps Construction
            start_date=datetime(2023, 4, 1),
            end_date=datetime(2024, 11, 30)
        ),
        Project(
            name="Chicago Logistics Hub Development",
            location="Chicago, IL",
            owner_id=companies["owners"][5].id,  # Prologis
            gc_id=companies["gcs"][6].id,        # McCarthy Building Companies
            start_date=datetime(2023, 9, 1),
            end_date=datetime(2024, 8, 31)
        )
    ]
    
    for project in projects:
        session.add(project)
    session.commit()
    
    return projects

def create_relationships(session: Session, companies: dict, projects: list):
    """Create compelling subcontractor relationships that demonstrate business value"""
    
    relationships = [
        # One World Trade Center Phase II - HIGH VALUE TARGET SCENARIO
        # Turner Construction + Related Companies using RapidFrame Steel (RECENT INCIDENT!)
        SubRelationship(
            gc_id=companies["gcs"][0].id,    # Turner Construction  
            owner_id=companies["owners"][2].id,  # Related Companies
            sub_id=companies["subs"][0].id,  # RapidFrame Steel Erectors (HIGH-RISK)
            project_id=projects[0].id,      # One World Trade Center Phase II
            trade="Steel Erection",
            po_value=15000000.0,  # $15M steel contract
            start_date=datetime(2023, 2, 1),
            end_date=datetime(2024, 5, 30)
        ),
        SubRelationship(
            gc_id=companies["gcs"][0].id,
            owner_id=companies["owners"][3].id,
            sub_id=companies["subs"][4].id,  # SafetyFirst Steel
            project_id=projects[0].id,
            trade="Steel Erection",
            po_value=800000.0,
            start_date=datetime(2023, 3, 1),
            end_date=datetime(2023, 8, 30)
        ),
        
        # Luxury Residential Complex relationships
        SubRelationship(
            gc_id=companies["gcs"][1].id,
            owner_id=companies["owners"][2].id,
            sub_id=companies["subs"][3].id,  # XYZ Roofing (high-risk)
            project_id=projects[1].id,
            trade="Roofing",
            po_value=450000.0,
            start_date=datetime(2023, 6, 1),
            end_date=datetime(2024, 1, 15)
        ),
        SubRelationship(
            gc_id=companies["gcs"][1].id,
            owner_id=companies["owners"][2].id,
            sub_id=companies["subs"][7].id,  # Premium Finishing Works
            project_id=projects[1].id,
            trade="Interior Finishing",
            po_value=750000.0,
            start_date=datetime(2024, 3, 1),
            end_date=datetime(2024, 11, 30)
        ),
        
        # Industrial Manufacturing Facility relationships
        SubRelationship(
            gc_id=companies["gcs"][5].id,
            owner_id=companies["owners"][3].id,
            sub_id=companies["subs"][1].id,  # Danger Zone Demolition (high-risk)
            project_id=projects[2].id,
            trade="Demolition",
            po_value=300000.0,
            start_date=datetime(2022, 8, 15),
            end_date=datetime(2022, 12, 30)
        ),
        SubRelationship(
            gc_id=companies["gcs"][5].id,
            owner_id=companies["owners"][3].id,
            sub_id=companies["subs"][5].id,  # Reliable Electric Systems
            project_id=projects[2].id,
            trade="Electrical",
            po_value=650000.0,
            start_date=datetime(2023, 2, 1),
            end_date=datetime(2023, 12, 15)
        ),
        
        # Manhattan High-Rise relationships
        SubRelationship(
            gc_id=companies["gcs"][2].id,
            owner_id=companies["owners"][0].id,
            sub_id=companies["subs"][2].id,  # QuickBuild Contractors (high-risk)
            project_id=projects[4].id,
            trade="Structural Steel",
            po_value=1200000.0,
            start_date=datetime(2023, 4, 1),
            end_date=datetime(2024, 6, 30)
        ),
        
        # Medical Center Expansion relationships
        SubRelationship(
            gc_id=companies["gcs"][4].id,
            owner_id=companies["owners"][1].id,
            sub_id=companies["subs"][6].id,  # Expert Plumbing Solutions
            project_id=projects[3].id,
            trade="Plumbing",
            po_value=380000.0,
            start_date=datetime(2023, 7, 1),
            end_date=datetime(2024, 6, 30)
        )
    ]
    
    for relationship in relationships:
        session.add(relationship)
    session.commit()

def create_ita_metrics(session: Session, companies: dict):
    """Create ITA safety metrics"""
    
    metrics = [
        # High-risk subs with poor metrics
        MetricsITA(
            sub_id=companies["subs"][0].id,  # ABC Construction
            year=2023,
            recordables=8,
            darts=4,
            hours_worked=125000,
            dart_rate=6.4,
            source_link="https://osha.gov/ita/2023"
        ),
        MetricsITA(
            sub_id=companies["subs"][1].id,  # Danger Zone Demolition
            year=2023,
            recordables=12,
            darts=8,
            hours_worked=89000,
            dart_rate=18.0,
            source_link="https://osha.gov/ita/2023"
        ),
        MetricsITA(
            sub_id=companies["subs"][2].id,  # QuickBuild Contractors
            year=2023,
            recordables=15,
            darts=10,
            hours_worked=180000,
            dart_rate=11.1,
            source_link="https://osha.gov/ita/2023"
        ),
        MetricsITA(
            sub_id=companies["subs"][3].id,  # XYZ Roofing
            year=2023,
            recordables=3,
            darts=2,
            hours_worked=45000,
            dart_rate=8.9,
            source_link="https://osha.gov/ita/2023"
        ),
        
        # Medium-risk subs
        MetricsITA(
            sub_id=companies["subs"][4].id,  # SafetyFirst Steel
            year=2023,
            recordables=6,
            darts=3,
            hours_worked=150000,
            dart_rate=4.0,
            source_link="https://osha.gov/ita/2023"
        ),
        MetricsITA(
            sub_id=companies["subs"][5].id,  # Reliable Electric Systems
            year=2023,
            recordables=2,
            darts=1,
            hours_worked=85000,
            dart_rate=2.4,
            source_link="https://osha.gov/ita/2023"
        ),
        
        # Low-risk subs with good metrics
        MetricsITA(
            sub_id=companies["subs"][7].id,  # Premium Finishing Works
            year=2023,
            recordables=1,
            darts=0,
            hours_worked=65000,
            dart_rate=0.0,
            source_link="https://osha.gov/ita/2023"
        )
    ]
    
    for metric in metrics:
        session.add(metric)
    session.commit()

def generate_sample_outreach_kits(session: Session):
    """Generate outreach kits for top opportunities"""
    
    # Get top 3 opportunities
    opportunities = session.exec(
        select(TargetOpportunity)
        .order_by(TargetOpportunity.propensity_score.desc())
        .limit(3)
    ).all()
    
    generator = OutreachGenerator()
    
    for opportunity in opportunities:
        try:
            generator.generate_outreach_kit(session, opportunity)
            print(f"Generated outreach kit for opportunity {opportunity.id}")
        except Exception as e:
            print(f"Error generating outreach kit for {opportunity.id}: {e}")

def show_summary_stats(session: Session):
    """Show summary statistics"""
    
    companies_count = session.exec(select(Company)).all()
    events_count = session.exec(select(Event)).all()
    opportunities_count = session.exec(select(TargetOpportunity)).all()
    
    print("\n📈 Database Summary:")
    print(f"Companies: {len(companies_count)}")
    print(f"Events: {len(events_count)}")
    print(f"Target Opportunities: {len(opportunities_count)}")
    
    if opportunities_count:
        high_score_count = len([o for o in opportunities_count if o.propensity_score >= 70])
        print(f"High-Priority Opportunities (≥70): {high_score_count}")

if __name__ == "__main__":
    asyncio.run(seed_database())