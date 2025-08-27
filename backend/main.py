from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ingestion_service = IngestionService()
scorer = PropensityScorer()
outreach_generator = OutreachGenerator()
pdf_generator = ProspectPackGenerator()
entity_resolver = EntityResolver()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "RiskRadar API is running"}

# Companies
@app.get("/companies", response_model=List[Company])
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

@app.get("/companies/{company_id}", response_model=Company)
def get_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# Events
@app.get("/events")
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
@app.get("/opportunities")
def get_opportunities(
    min_score: Optional[float] = 0,
    limit: Optional[int] = 100,
    session: Session = Depends(get_session)
):
    statement = select(TargetOpportunity).where(TargetOpportunity.propensity_score >= min_score)
    statement = statement.order_by(TargetOpportunity.propensity_score.desc()).limit(limit)
    opportunities = session.exec(statement).all()
    return opportunities

@app.get("/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: int, session: Session = Depends(get_session)):
    opportunity = session.get(TargetOpportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@app.post("/opportunities/rebuild")
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
@app.post("/outreach/generate")
def generate_outreach_kit(
    target_id: int,
    session: Session = Depends(get_session)
):
    opportunity = session.get(TargetOpportunity, target_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Target opportunity not found")
    
    outreach_kit = outreach_generator.generate_outreach_kit(session, opportunity)
    return {"id": outreach_kit.id, "message": "Outreach kit generated successfully"}

@app.get("/outreach/{kit_id}")
def get_outreach_kit(kit_id: int, session: Session = Depends(get_session)):
    kit = session.get(OutreachKit, kit_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Outreach kit not found")
    return kit

@app.post("/outreach/{kit_id}/export/pdf")
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
@app.post("/ingest/run")
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

@app.get("/ingest/status")
def get_ingestion_status():
    return {"status": "idle", "last_run": None}

# File uploads
@app.post("/uploads/{mapping_type}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)