import re
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import fuzz
from sqlmodel import Session, select
from models import Company, CompanyAlias, SubRelationship, Project
import csv
import io

class EntityResolver:
    def __init__(self, fuzzy_threshold: float = 85.0):
        self.fuzzy_threshold = fuzzy_threshold
        
    def normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching"""
        if not name:
            return ""
        
        # Convert to uppercase and strip
        name = name.strip().upper()
        
        # Remove common business suffixes
        suffixes = [
            r'\b(INC|INCORPORATED)\b\.?',
            r'\bLLC\b\.?', 
            r'\bCORP\b\.?',
            r'\bCORPORATION\b\.?',
            r'\bCO\b\.?',
            r'\bLTD\b\.?',
            r'\bLIMITED\b\.?',
            r'\bLP\b\.?',
            r'\bLLP\b\.?',
            r'\bPLC\b\.?'
        ]
        
        for suffix in suffixes:
            name = re.sub(suffix, '', name)
        
        # Remove special characters except spaces and hyphens
        name = re.sub(r'[^\w\s\-]', '', name)
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name.strip()
    
    def find_similar_companies(self, session: Session, company_name: str, limit: int = 5) -> List[Tuple[Company, float]]:
        """Find companies with similar names using fuzzy matching"""
        normalized_name = self.normalize_company_name(company_name)
        
        # Get all companies for fuzzy matching
        companies = session.exec(select(Company)).all()
        matches = []
        
        for company in companies:
            # Check direct normalized name match
            score = fuzz.ratio(normalized_name, company.normalized_name)
            if score >= self.fuzzy_threshold:
                matches.append((company, score))
            
            # Check against aliases
            for alias in company.aliases:
                alias_score = fuzz.ratio(normalized_name, self.normalize_company_name(alias.alias))
                if alias_score >= self.fuzzy_threshold:
                    matches.append((company, alias_score))
        
        # Sort by score and remove duplicates
        matches = sorted(set(matches), key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def resolve_company(self, session: Session, company_name: str, company_data: Dict[str, Any] = None) -> Optional[Company]:
        """Resolve a company name to an existing company or suggest creating new one"""
        if not company_name:
            return None
        
        normalized_name = self.normalize_company_name(company_name)
        
        # First try exact normalized name match
        company = session.exec(
            select(Company).where(Company.normalized_name == normalized_name)
        ).first()
        
        if company:
            return company
        
        # Try fuzzy matching
        similar_companies = self.find_similar_companies(session, company_name, limit=1)
        if similar_companies and similar_companies[0][1] >= 95:  # Very high confidence
            return similar_companies[0][0]
        
        # No match found
        return None
    
    def add_company_alias(self, session: Session, company_id: int, alias: str, confidence: float = 1.0):
        """Add an alias for a company"""
        normalized_alias = self.normalize_company_name(alias)
        
        # Check if alias already exists
        existing_alias = session.exec(
            select(CompanyAlias).where(
                CompanyAlias.company_id == company_id,
                CompanyAlias.alias == normalized_alias
            )
        ).first()
        
        if not existing_alias:
            new_alias = CompanyAlias(
                company_id=company_id,
                alias=normalized_alias,
                confidence=confidence
            )
            session.add(new_alias)
    
    def link_subcontractor_relationships(
        self, 
        session: Session, 
        sub_company: Company, 
        event_data: Dict[str, Any],
        location: Optional[str] = None
    ) -> List[SubRelationship]:
        """Try to link a subcontractor to potential GCs/owners based on geography and timing"""
        potential_links = []
        
        # Look for projects in the same location around the same time
        if location and event_data.get("occurred_on"):
            event_date = event_data["occurred_on"]
            
            # Find projects in the same area
            projects_query = select(Project).where(Project.location.ilike(f"%{location}%"))
            projects = session.exec(projects_query).all()
            
            for project in projects:
                # Check if timing makes sense (event within project timeframe or close to it)
                if self._is_timing_compatible(event_date, project.start_date, project.end_date):
                    # Create potential relationship with low confidence
                    if project.gc_id:
                        relationship = SubRelationship(
                            gc_id=project.gc_id,
                            owner_id=project.owner_id,
                            sub_id=sub_company.id,
                            project_id=project.id
                        )
                        potential_links.append(relationship)
        
        return potential_links
    
    def _is_timing_compatible(self, event_date, project_start, project_end) -> bool:
        """Check if event timing is compatible with project timeline"""
        if not event_date:
            return False
        
        # If we have project dates, check if event is within or close to project timeline
        if project_start and project_end:
            # Allow some buffer before and after project
            from datetime import timedelta
            buffer = timedelta(days=180)  # 6 months buffer
            return project_start - buffer <= event_date <= project_end + buffer
        
        # If no project dates, assume compatible
        return True
    
    def process_csv_mappings(self, session: Session, csv_content: str, mapping_type: str) -> Dict[str, Any]:
        """Process CSV files for company relationships and aliases"""
        results = {"processed": 0, "errors": [], "created": 0}
        
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            
            if mapping_type == "sub_relationships":
                results.update(self._process_sub_relationships_csv(session, reader))
            elif mapping_type == "company_aliases":
                results.update(self._process_company_aliases_csv(session, reader))
            else:
                results["errors"].append(f"Unknown mapping type: {mapping_type}")
        
        except Exception as e:
            results["errors"].append(f"CSV processing error: {str(e)}")
        
        return results
    
    def _process_sub_relationships_csv(self, session: Session, reader) -> Dict[str, Any]:
        """Process subcontractor relationships CSV"""
        results = {"processed": 0, "errors": [], "created": 0}
        
        for row in reader:
            try:
                # Find or create companies
                gc = self._find_or_create_company_from_csv(session, row.get("gc_name"))
                owner = self._find_or_create_company_from_csv(session, row.get("owner_name"), "Owner")
                sub = self._find_or_create_company_from_csv(session, row.get("sub_name"), "Sub")
                
                # Find or create project
                project = None
                if row.get("project_name"):
                    project = self._find_or_create_project_from_csv(session, row, gc, owner)
                
                # Create relationship
                from datetime import datetime
                relationship = SubRelationship(
                    gc_id=gc.id if gc else None,
                    owner_id=owner.id if owner else None,
                    sub_id=sub.id,
                    project_id=project.id if project else None,
                    trade=row.get("trade"),
                    po_value=float(row.get("po_value", 0)) if row.get("po_value") else None,
                    start_date=datetime.fromisoformat(row.get("start_date")) if row.get("start_date") else None,
                    end_date=datetime.fromisoformat(row.get("end_date")) if row.get("end_date") else None
                )
                session.add(relationship)
                results["created"] += 1
                results["processed"] += 1
                
            except Exception as e:
                results["errors"].append(f"Row error: {str(e)}")
        
        session.commit()
        return results
    
    def _process_company_aliases_csv(self, session: Session, reader) -> Dict[str, Any]:
        """Process company aliases CSV"""
        results = {"processed": 0, "errors": [], "created": 0}
        
        for row in reader:
            try:
                canonical_name = row.get("canonical_name")
                alias_name = row.get("alias")
                
                if not canonical_name or not alias_name:
                    continue
                
                # Find the canonical company
                company = self.resolve_company(session, canonical_name)
                if not company:
                    # Create the canonical company if it doesn't exist
                    from models import CompanyType
                    company = Company(
                        name=canonical_name,
                        normalized_name=self.normalize_company_name(canonical_name),
                        type=CompanyType.UNKNOWN
                    )
                    session.add(company)
                    session.flush()
                
                # Add the alias
                self.add_company_alias(session, company.id, alias_name, confidence=0.9)
                results["created"] += 1
                results["processed"] += 1
                
            except Exception as e:
                results["errors"].append(f"Row error: {str(e)}")
        
        session.commit()
        return results
    
    def _find_or_create_company_from_csv(self, session: Session, company_name: str, company_type: str = "Unknown") -> Optional[Company]:
        """Find or create company from CSV data"""
        if not company_name:
            return None
        
        company = self.resolve_company(session, company_name)
        if not company:
            from models import CompanyType
            company = Company(
                name=company_name,
                normalized_name=self.normalize_company_name(company_name),
                type=CompanyType(company_type) if hasattr(CompanyType, company_type.upper()) else CompanyType.UNKNOWN
            )
            session.add(company)
            session.flush()
        
        return company
    
    def _find_or_create_project_from_csv(self, session: Session, row: Dict[str, str], gc: Company, owner: Company) -> Project:
        """Find or create project from CSV data"""
        project_name = row.get("project_name")
        
        # Try to find existing project
        project = session.exec(
            select(Project).where(Project.name == project_name)
        ).first()
        
        if not project:
            from datetime import datetime
            project = Project(
                name=project_name,
                location=row.get("location"),
                gc_id=gc.id if gc else None,
                owner_id=owner.id if owner else None,
                start_date=datetime.fromisoformat(row.get("start_date")) if row.get("start_date") else None,
                end_date=datetime.fromisoformat(row.get("end_date")) if row.get("end_date") else None
            )
            session.add(project)
            session.flush()
        
        return project