#!/usr/bin/env python3
"""
Simple script to test that models can be imported correctly
"""

try:
    print("Testing model imports...")
    
    # Test SQLModel import
    from sqlmodel import SQLModel, Field, Relationship
    print("✅ SQLModel imports successful")
    
    # Test individual model imports
    from models import (
        CompanyType, EventType, Company, CompanyAlias, 
        Project, SubRelationship, Event, MetricsITA, 
        TargetOpportunity, OutreachKit, User, AuditLog
    )
    print("✅ All model classes imported successfully")
    
    # Test enum values
    assert CompanyType.GC == "GC"
    assert EventType.INSPECTION == "inspection"
    print("✅ Enum values working correctly")
    
    # Test model instantiation
    company = Company(
        name="Test Company",
        type=CompanyType.GC,
        normalized_name="TEST COMPANY"
    )
    print("✅ Model instantiation successful")
    
    print("\n🎉 All model tests passed! Models are working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure you have installed the requirements:")
    print("pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    pass