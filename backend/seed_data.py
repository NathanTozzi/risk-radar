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
        session.query(OutreachKit).delete()
        session.query(TargetOpportunity).delete()
        session.query(Event).delete()
        session.query(SubRelationship).delete()
        session.query(MetricsITA).delete()
        session.query(CompanyAlias).delete()
        session.query(Project).delete()
        session.query(Company).delete()
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
        
        # Run ingestion to create events
        print("Running data ingestion...")
        ingestion_service = IngestionService()
        await ingestion_service.run_ingestion(
            sources=["osha_establishment", "osha_accidents", "news", "ita"],
            since=datetime.now() - timedelta(days=180)
        )
        
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
    """Create sample companies"""
    
    # General Contractors
    gcs = [
        Company(name="MegaBuild Construction Corp", type=CompanyType.GC, naics="236220", state="TX", website="https://megabuild.com", normalized_name="MEGABUILD CONSTRUCTION"),
        Company(name="Premier General Contractors LLC", type=CompanyType.GC, naics="236210", state="CA", website="https://premierGC.com", normalized_name="PREMIER GENERAL CONTRACTORS"),
        Company(name="Skyline Construction Group", type=CompanyType.GC, naics="236220", state="NY", website="https://skylineconstruction.com", normalized_name="SKYLINE CONSTRUCTION GROUP"),
        Company(name="Golden State Builders Inc", type=CompanyType.GC, naics="236220", state="CA", website="https://goldenstatebuilders.com", normalized_name="GOLDEN STATE BUILDERS"),
        Company(name="Atlantic Construction Partners", type=CompanyType.GC, naics="236210", state="FL", website="https://atlanticcp.com", normalized_name="ATLANTIC CONSTRUCTION PARTNERS"),
        Company(name="Lone Star Development Co", type=CompanyType.GC, naics="236220", state="TX", website="https://lonestardevelopment.com", normalized_name="LONE STAR DEVELOPMENT")
    ]
    
    # Owners/Developers
    owners = [
        Company(name="Metro Property Development", type=CompanyType.OWNER, naics="531110", state="NY", website="https://metroprop.com", normalized_name="METRO PROPERTY DEVELOPMENT"),
        Company(name="Sunshine Real Estate Holdings", type=CompanyType.OWNER, naics="531110", state="FL", website="https://sunshineREH.com", normalized_name="SUNSHINE REAL ESTATE HOLDINGS"),
        Company(name="Pacific Coast Properties LLC", type=CompanyType.OWNER, naics="531110", state="CA", website="https://pacificcoastprop.com", normalized_name="PACIFIC COAST PROPERTIES"),
        Company(name="Texas Tower Development Corp", type=CompanyType.OWNER, naics="531110", state="TX", website="https://texastower.com", normalized_name="TEXAS TOWER DEVELOPMENT")
    ]
    
    # Subcontractors (some with issues)
    subs = [
        # High-risk subs
        Company(name="ABC Construction LLC", type=CompanyType.SUB, naics="236220", state="TX", normalized_name="ABC CONSTRUCTION"),
        Company(name="Danger Zone Demolition", type=CompanyType.SUB, naics="238910", state="CA", normalized_name="DANGER ZONE DEMOLITION"),
        Company(name="QuickBuild Contractors", type=CompanyType.SUB, naics="238120", state="NY", normalized_name="QUICKBUILD CONTRACTORS"),
        Company(name="XYZ Roofing Inc", type=CompanyType.SUB, naics="238160", state="CA", normalized_name="XYZ ROOFING"),
        
        # Medium-risk subs
        Company(name="SafetyFirst Steel Co", type=CompanyType.SUB, naics="238120", state="NY", normalized_name="SAFETYFIRST STEEL"),
        Company(name="Reliable Electric Systems", type=CompanyType.SUB, naics="238210", state="FL", normalized_name="RELIABLE ELECTRIC SYSTEMS"),
        Company(name="Expert Plumbing Solutions", type=CompanyType.SUB, naics="238220", state="TX", normalized_name="EXPERT PLUMBING SOLUTIONS"),
        
        # Low-risk subs
        Company(name="Premium Finishing Works", type=CompanyType.SUB, naics="238320", state="CA", normalized_name="PREMIUM FINISHING WORKS")
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
    """Create sample projects"""
    
    projects = [
        Project(
            name="Downtown Office Tower", 
            location="Dallas, TX",
            owner_id=companies["owners"][3].id,  # Texas Tower Development
            gc_id=companies["gcs"][0].id,        # MegaBuild Construction
            start_date=datetime(2023, 1, 15),
            end_date=datetime(2024, 6, 30)
        ),
        Project(
            name="Luxury Residential Complex",
            location="Los Angeles, CA", 
            owner_id=companies["owners"][2].id,  # Pacific Coast Properties
            gc_id=companies["gcs"][1].id,        # Premier General Contractors
            start_date=datetime(2023, 3, 1),
            end_date=datetime(2024, 12, 15)
        ),
        Project(
            name="Industrial Manufacturing Facility",
            location="Houston, TX",
            owner_id=companies["owners"][3].id,  # Texas Tower Development
            gc_id=companies["gcs"][5].id,        # Lone Star Development
            start_date=datetime(2022, 8, 1),
            end_date=datetime(2024, 2, 28)
        ),
        Project(
            name="Medical Center Expansion",
            location="Miami, FL",
            owner_id=companies["owners"][1].id,  # Sunshine Real Estate Holdings
            gc_id=companies["gcs"][4].id,        # Atlantic Construction Partners
            start_date=datetime(2023, 5, 1),
            end_date=datetime(2024, 8, 30)
        ),
        Project(
            name="Manhattan High-Rise",
            location="New York, NY",
            owner_id=companies["owners"][0].id,  # Metro Property Development
            gc_id=companies["gcs"][2].id,        # Skyline Construction Group
            start_date=datetime(2023, 2, 1),
            end_date=datetime(2025, 1, 15)
        ),
        Project(
            name="Tech Campus Phase 2",
            location="San Francisco, CA",
            owner_id=companies["owners"][2].id,  # Pacific Coast Properties
            gc_id=companies["gcs"][3].id,        # Golden State Builders
            start_date=datetime(2023, 4, 1),
            end_date=datetime(2024, 10, 30)
        )
    ]
    
    for project in projects:
        session.add(project)
    session.commit()
    
    return projects

def create_relationships(session: Session, companies: dict, projects: list):
    """Create subcontractor relationships"""
    
    relationships = [
        # Downtown Office Tower relationships
        SubRelationship(
            gc_id=companies["gcs"][0].id,
            owner_id=companies["owners"][3].id,
            sub_id=companies["subs"][0].id,  # ABC Construction (high-risk)
            project_id=projects[0].id,
            trade="General Construction",
            po_value=2500000.0,
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