import pytest
from datetime import datetime
from models import Company, CompanyType, Event, EventType, TargetOpportunity
from sqlmodel import Session

def test_company_creation(session: Session):
    """Test creating a company"""
    company = Company(
        name="Test Construction LLC",
        type=CompanyType.GC,
        naics="236220",
        state="TX",
        normalized_name="TEST CONSTRUCTION"
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    
    assert company.id is not None
    assert company.name == "Test Construction LLC"
    assert company.type == CompanyType.GC
    assert company.normalized_name == "TEST CONSTRUCTION"

def test_event_creation(session: Session):
    """Test creating an event"""
    # First create a company
    company = Company(
        name="Test Construction LLC",
        type=CompanyType.SUB,
        normalized_name="TEST CONSTRUCTION"
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    
    # Create event
    event = Event(
        source="test_source",
        event_type=EventType.INSPECTION,
        company_id=company.id,
        occurred_on=datetime.now(),
        severity_score=75.0,
        data={"violations": 3, "penalty": 15000}
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    
    assert event.id is not None
    assert event.company_id == company.id
    assert event.severity_score == 75.0
    assert event.data["violations"] == 3

def test_target_opportunity_creation(session: Session):
    """Test creating a target opportunity"""
    # Create companies
    gc = Company(name="GC Corp", type=CompanyType.GC, normalized_name="GC")
    sub = Company(name="Sub Corp", type=CompanyType.SUB, normalized_name="SUB")
    session.add(gc)
    session.add(sub)
    session.commit()
    
    # Create event
    event = Event(
        source="test",
        event_type=EventType.ACCIDENT,
        company_id=sub.id,
        occurred_on=datetime.now(),
        severity_score=85.0,
        data={"fatality": True}
    )
    session.add(event)
    session.commit()
    
    # Create opportunity
    opportunity = TargetOpportunity(
        gc_id=gc.id,
        driver_event_id=event.id,
        propensity_score=89.5,
        confidence=0.9,
        recommended_talk_track="Post-incident stabilization"
    )
    session.add(opportunity)
    session.commit()
    session.refresh(opportunity)
    
    assert opportunity.id is not None
    assert opportunity.gc_id == gc.id
    assert opportunity.propensity_score == 89.5