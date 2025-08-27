import pytest
from datetime import datetime, timedelta
from sqlmodel import Session
from models import Company, CompanyType, Event, EventType
from scoring.propensity import PropensityScorer

@pytest.fixture
def scorer():
    return PropensityScorer()

def test_calculate_recency_score(scorer):
    """Test recency score calculation"""
    # Recent incident (15 days ago)
    recent_date = datetime.now() - timedelta(days=15)
    score = scorer._calculate_recency_score(recent_date)
    assert score == 30.0
    
    # Older incident (100 days ago)
    old_date = datetime.now() - timedelta(days=100)
    score = scorer._calculate_recency_score(old_date)
    assert 0 < score < 30.0
    
    # Very old incident (200 days ago)
    very_old_date = datetime.now() - timedelta(days=200)
    score = scorer._calculate_recency_score(very_old_date)
    assert score == 0.0

def test_calculate_severity_score(scorer):
    """Test severity score calculation"""
    # Fatality incident
    fatal_event = Event(
        source="test",
        event_type=EventType.ACCIDENT,
        company_id=1,
        occurred_on=datetime.now(),
        severity_score=0,
        data={"fatality": True}
    )
    score = scorer._calculate_severity_score(fatal_event)
    assert score >= 45.0  # Should be high for fatality
    
    # Serious violation
    serious_event = Event(
        source="test", 
        event_type=EventType.CITATION,
        company_id=1,
        occurred_on=datetime.now(),
        severity_score=0,
        data={"severity_type": "Serious", "violations": 2}
    )
    score = scorer._calculate_severity_score(serious_event)
    assert 10.0 <= score <= 20.0
    
    # Minor violation
    minor_event = Event(
        source="test",
        event_type=EventType.CITATION,
        company_id=1,
        occurred_on=datetime.now(),
        severity_score=0,
        data={"severity_type": "Other-Than-Serious", "violations": 1}
    )
    score = scorer._calculate_severity_score(minor_event)
    assert score <= 10.0

def test_get_incident_description(scorer):
    """Test incident description generation"""
    # Accident with fatality
    fatal_event = Event(
        source="test",
        event_type=EventType.ACCIDENT,
        company_id=1,
        occurred_on=datetime.now(),
        severity_score=95,
        data={"fatality": True}
    )
    desc = scorer._get_incident_description(fatal_event)
    assert "serious" in desc.lower()
    
    # Regular inspection
    inspection_event = Event(
        source="test",
        event_type=EventType.INSPECTION,
        company_id=1,
        occurred_on=datetime.now(),
        severity_score=30,
        data={"violations": 2}
    )
    desc = scorer._get_incident_description(inspection_event)
    assert "inspection" in desc.lower()

def test_format_timeframe(scorer):
    """Test timeframe formatting"""
    assert scorer._format_timeframe(3) == "last week"
    assert scorer._format_timeframe(10) == "a couple weeks ago"
    assert scorer._format_timeframe(25) == "last month"
    assert scorer._format_timeframe(45) == "recently"
    assert scorer._format_timeframe(120) == "a few months ago"

def test_determine_talk_track(scorer):
    """Test talk track determination"""
    # High severity should trigger post-incident
    high_severity = {"severity": 25, "frequency": 5, "ita": 5}
    track = scorer._determine_talk_track(high_severity, None)
    assert "post-incident" in track.lower()
    
    # High frequency should trigger trend analysis
    high_frequency = {"severity": 10, "frequency": 12, "ita": 5}
    track = scorer._determine_talk_track(high_frequency, None)
    assert "trend" in track.lower()
    
    # High ITA should trigger portfolio risk
    high_ita = {"severity": 10, "frequency": 5, "ita": 12}
    track = scorer._determine_talk_track(high_ita, None)
    assert "portfolio" in track.lower() or "risk" in track.lower()