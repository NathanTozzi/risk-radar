import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from models import Company, CompanyType, Event, EventType
from sqlmodel import Session

def test_read_root(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RiskRadar API is running"}

def test_get_companies_empty(client: TestClient):
    """Test getting companies when none exist"""
    response = client.get("/companies")
    assert response.status_code == 200
    assert response.json() == []

def test_get_companies(client: TestClient, session: Session):
    """Test getting companies"""
    # Create test companies
    company1 = Company(
        name="Test GC",
        type=CompanyType.GC,
        state="TX",
        normalized_name="TEST GC"
    )
    company2 = Company(
        name="Test Sub",
        type=CompanyType.SUB,
        state="CA",
        normalized_name="TEST SUB"
    )
    session.add(company1)
    session.add(company2)
    session.commit()
    
    response = client.get("/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 2

def test_get_companies_filtered(client: TestClient, session: Session):
    """Test filtering companies by type"""
    company1 = Company(name="GC", type=CompanyType.GC, normalized_name="GC")
    company2 = Company(name="Sub", type=CompanyType.SUB, normalized_name="SUB")
    session.add(company1)
    session.add(company2)
    session.commit()
    
    response = client.get("/companies?type=GC")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 1
    assert companies[0]["type"] == "GC"

def test_get_company_by_id(client: TestClient, session: Session):
    """Test getting a specific company"""
    company = Company(name="Test Company", type=CompanyType.GC, normalized_name="TEST COMPANY")
    session.add(company)
    session.commit()
    session.refresh(company)
    
    response = client.get(f"/companies/{company.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["id"] == company.id

def test_get_company_not_found(client: TestClient):
    """Test getting non-existent company"""
    response = client.get("/companies/999")
    assert response.status_code == 404

def test_get_events(client: TestClient, session: Session):
    """Test getting events"""
    # Create company and event
    company = Company(name="Test Company", type=CompanyType.SUB, normalized_name="TEST COMPANY")
    session.add(company)
    session.commit()
    
    event = Event(
        source="test",
        event_type=EventType.INSPECTION,
        company_id=company.id,
        occurred_on=datetime.now(),
        severity_score=50.0,
        data={"test": "data"}
    )
    session.add(event)
    session.commit()
    
    response = client.get("/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["source"] == "test"

def test_get_opportunities_empty(client: TestClient):
    """Test getting opportunities when none exist"""
    response = client.get("/opportunities")
    assert response.status_code == 200
    assert response.json() == []