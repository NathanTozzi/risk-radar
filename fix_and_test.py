#!/usr/bin/env python3
"""
Quick fix and test script for RiskRadar models
Run this to verify the models are working correctly
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all imports work correctly"""
    try:
        print("🔍 Testing imports...")
        
        # Test core dependencies
        import sqlmodel
        import sqlalchemy
        print("  ✅ SQLModel and SQLAlchemy imported")
        
        # Test our models
        from backend.models import (
            CompanyType, EventType, Company, Event, 
            TargetOpportunity, OutreachKit
        )
        print("  ✅ Model classes imported")
        
        # Test database connection setup
        from backend.database import engine, create_db_and_tables
        print("  ✅ Database utilities imported")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("  💡 Solution: Run 'pip install -r backend/requirements.txt'")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_model_creation():
    """Test that models can be instantiated"""
    try:
        print("\n🏗️  Testing model creation...")
        
        from backend.models import Company, CompanyType
        
        # Test company creation
        company = Company(
            name="Test Company LLC",
            type=CompanyType.GC,
            state="TX",
            normalized_name="TEST COMPANY"
        )
        
        print("  ✅ Company model created successfully")
        print(f"     Name: {company.name}")
        print(f"     Type: {company.type}")
        print(f"     State: {company.state}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 RiskRadar Models Test & Fix")
    print("=" * 40)
    
    # Test imports
    import_success = test_imports()
    if not import_success:
        print("\n❌ Import tests failed. Please install requirements first:")
        print("   cd backend && pip install -r requirements.txt")
        return False
    
    # Test model creation
    model_success = test_model_creation()
    if not model_success:
        print("\n❌ Model creation tests failed.")
        return False
    
    print("\n🎉 All tests passed!")
    print("\nNext steps:")
    print("1. Start the application: make dev")
    print("2. Or run step by step:")
    print("   docker-compose build")
    print("   docker-compose up -d")
    print("   docker-compose exec api python seed_data.py")
    print("\n🌐 Access points:")
    print("   Frontend: http://localhost:3000")
    print("   API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)