from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from database import get_session, create_db_and_tables
from models import *
from ingestion import IngestionService
from scoring import PropensityScorer
from outreach_generator import OutreachGenerator
from pdf_generator import ProspectPackGenerator
from entity_resolution import EntityResolver
from typing import List, Optional
from datetime import datetime
import io
import os

app = FastAPI(title="RiskRadar API", description="BDR application for identifying GCs and asset owners after subcontractor incidents", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://risk-radar-8d3m.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files in production
dist_dir = "./dist"
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=f"{dist_dir}/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend files for all non-API routes"""
        # Skip API routes and docs
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Try to serve specific file
        file_path = f"{dist_dir}/{full_path}"
        if os.path.isfile(file_path) and not full_path.startswith("assets/"):
            return FileResponse(file_path)
        
        # Default to index.html for SPA routing
        return FileResponse(f"{dist_dir}/index.html")

ingestion_service = IngestionService()
scorer = PropensityScorer()
outreach_generator = OutreachGenerator()
pdf_generator = ProspectPackGenerator()
entity_resolver = EntityResolver()

# Create API router
api_router = APIRouter(prefix="/api")

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "RiskRadar API is running"}

# Companies
@api_router.get("/companies", response_model=List[Company])
def get_companies(
    type: Optional[CompanyType] = None,
    q: Optional[str] = None,
    session: Session = Depends(get_session)
):
    statement = select(Company)
    if type:
        statement = statement.where(Company.type == type)
    if q:
        statement = statement.where(Company.name.ilike(f"%{q}%"))
    companies = session.exec(statement).all()
    return companies

@api_router.get("/companies/{company_id}", response_model=Company)
def get_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# Events
@api_router.get("/events")
def get_events(
    company_id: Optional[int] = None,
    event_type: Optional[EventType] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    session: Session = Depends(get_session)
):
    statement = select(Event)
    if company_id:
        statement = statement.where(Event.company_id == company_id)
    if event_type:
        statement = statement.where(Event.event_type == event_type)
    if since:
        statement = statement.where(Event.occurred_on >= datetime.fromisoformat(since.replace('Z', '+00:00')))
    if until:
        statement = statement.where(Event.occurred_on <= datetime.fromisoformat(until.replace('Z', '+00:00')))
    events = session.exec(statement.order_by(Event.occurred_on.desc())).all()
    return events

# Opportunities
@api_router.get("/opportunities")
def get_opportunities(
    min_score: Optional[float] = 0,
    limit: Optional[int] = 100,
    session: Session = Depends(get_session)
):
    statement = select(TargetOpportunity).where(TargetOpportunity.propensity_score >= min_score)
    statement = statement.order_by(TargetOpportunity.propensity_score.desc()).limit(limit)
    opportunities = session.exec(statement).all()
    return opportunities

@api_router.get("/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: int, session: Session = Depends(get_session)):
    opportunity = session.get(TargetOpportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@api_router.post("/opportunities/rebuild")
async def rebuild_opportunities(
    since: Optional[str] = None,
    until: Optional[str] = None,
    session: Session = Depends(get_session)
):
    since_dt = datetime.fromisoformat(since.replace('Z', '+00:00')) if since else None
    until_dt = datetime.fromisoformat(until.replace('Z', '+00:00')) if until else None
    
    result = scorer.rebuild_opportunities(session, since_dt, until_dt)
    return result

# Outreach
@api_router.post("/outreach/generate")
def generate_outreach_kit(
    target_id: int,
    session: Session = Depends(get_session)
):
    opportunity = session.get(TargetOpportunity, target_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Target opportunity not found")
    
    outreach_kit = outreach_generator.generate_outreach_kit(session, opportunity)
    return {"id": outreach_kit.id, "message": "Outreach kit generated successfully"}

@api_router.get("/outreach/{kit_id}")
def get_outreach_kit(kit_id: int, session: Session = Depends(get_session)):
    kit = session.get(OutreachKit, kit_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Outreach kit not found")
    return kit

@api_router.post("/outreach/{kit_id}/export/pdf")
def export_prospect_pack(kit_id: int, session: Session = Depends(get_session)):
    kit = session.get(OutreachKit, kit_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Outreach kit not found")
    
    opportunity = session.get(TargetOpportunity, kit.target_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Target opportunity not found")
    
    pdf_bytes = pdf_generator.generate_prospect_pack(session, opportunity, kit)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=prospect-pack-{kit_id}.pdf"}
    )

# Ingestion
@api_router.post("/ingest/run")
async def run_ingestion(
    sources: List[str],
    since: Optional[str] = None,
    until: Optional[str] = None,
    companies: Optional[List[str]] = None
):
    since_dt = datetime.fromisoformat(since.replace('Z', '+00:00')) if since else None
    until_dt = datetime.fromisoformat(until.replace('Z', '+00:00')) if until else None
    
    result = await ingestion_service.run_ingestion(sources, since_dt, until_dt, companies)
    return result

@api_router.get("/ingest/status")
def get_ingestion_status():
    return {"status": "idle", "last_run": None}

# File uploads
@api_router.post("/uploads/{mapping_type}")
async def upload_csv(
    mapping_type: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if mapping_type not in ["sub_relationships", "company_aliases", "sub_profile"]:
        raise HTTPException(status_code=400, detail="Invalid mapping type")
    
    contents = await file.read()
    csv_content = contents.decode('utf-8')
    
    result = entity_resolver.process_csv_mappings(session, csv_content, mapping_type)
    return result

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)