import pytest
from sqlmodel import Session
from entity_resolution import EntityResolver
from models import Company, CompanyType

@pytest.fixture
def resolver():
    return EntityResolver()

def test_normalize_company_name(resolver):
    """Test company name normalization"""
    # Test suffix removal
    assert resolver.normalize_company_name("ABC Construction LLC") == "ABC CONSTRUCTION"
    assert resolver.normalize_company_name("XYZ Corp.") == "XYZ"
    assert resolver.normalize_company_name("Test Inc") == "TEST"
    
    # Test punctuation removal
    assert resolver.normalize_company_name("A&B Construction, Inc.") == "AB CONSTRUCTION"
    
    # Test whitespace normalization
    assert resolver.normalize_company_name("  Multi   Word   Company  ") == "MULTI WORD COMPANY"
    
    # Test empty string
    assert resolver.normalize_company_name("") == ""
    assert resolver.normalize_company_name("   ") == ""

def test_find_similar_companies(resolver, session: Session):
    """Test fuzzy company matching"""
    # Create test companies
    company1 = Company(name="ABC Construction LLC", type=CompanyType.GC, normalized_name="ABC CONSTRUCTION")
    company2 = Company(name="XYZ Roofing Inc", type=CompanyType.SUB, normalized_name="XYZ ROOFING")
    company3 = Company(name="ABC Contracting", type=CompanyType.GC, normalized_name="ABC CONTRACTING")
    
    session.add(company1)
    session.add(company2)  
    session.add(company3)
    session.commit()
    
    # Test exact match
    matches = resolver.find_similar_companies(session, "ABC Construction LLC")
    assert len(matches) >= 1
    assert matches[0][1] >= 95  # High similarity score
    
    # Test fuzzy match
    matches = resolver.find_similar_companies(session, "ABC Construction Company")
    assert len(matches) >= 1
    
    # Test no match
    matches = resolver.find_similar_companies(session, "Completely Different Company Name")
    assert len(matches) == 0

def test_resolve_company_exact_match(resolver, session: Session):
    """Test exact company resolution"""
    company = Company(name="Test Company", type=CompanyType.GC, normalized_name="TEST COMPANY")
    session.add(company)
    session.commit()
    
    resolved = resolver.resolve_company(session, "Test Company")
    assert resolved is not None
    assert resolved.id == company.id

def test_resolve_company_no_match(resolver, session: Session):
    """Test company resolution when no match exists"""
    resolved = resolver.resolve_company(session, "Nonexistent Company")
    assert resolved is None

def test_add_company_alias(resolver, session: Session):
    """Test adding company aliases"""
    company = Company(name="Test Company", type=CompanyType.GC, normalized_name="TEST COMPANY")
    session.add(company)
    session.commit()
    
    resolver.add_company_alias(session, company.id, "Test Corp", confidence=0.9)
    session.commit()
    
    # Verify alias was added
    from sqlmodel import select
    from models import CompanyAlias
    alias = session.exec(select(CompanyAlias).where(CompanyAlias.company_id == company.id)).first()
    assert alias is not None
    assert alias.alias == "TEST"  # Should be normalized
    assert alias.confidence == 0.9

def test_process_company_aliases_csv(resolver, session: Session):
    """Test processing company aliases CSV"""
    csv_content = """canonical_name,alias
ABC Construction LLC,ABC Corp
ABC Construction LLC,ABC Contracting
XYZ Company,XYZ Corp"""
    
    result = resolver.process_csv_mappings(session, csv_content, "company_aliases")
    assert result["processed"] == 3
    assert len(result["errors"]) == 0
    
    # Verify companies were created
    from sqlmodel import select
    companies = session.exec(select(Company)).all()
    assert len(companies) >= 2  # Should create ABC Construction and XYZ Company