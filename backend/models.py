from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CompanyType(str, Enum):
    GC = "GC"
    OWNER = "Owner" 
    SUB = "Sub"
    UNKNOWN = "Unknown"

class EventType(str, Enum):
    INSPECTION = "inspection"
    CITATION = "citation"
    ACCIDENT = "accident"
    NEWS = "news"
    ITA = "ita"

class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: CompanyType = Field(index=True)
    naics: Optional[str] = None
    state: Optional[str] = Field(index=True)
    website: Optional[str] = None
    normalized_name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    aliases: List["CompanyAlias"] = Relationship(back_populates="company")
    events: List["Event"] = Relationship(back_populates="company")
    gc_relationships: List["SubRelationship"] = Relationship(back_populates="gc", sa_relationship_kwargs={"foreign_keys": "SubRelationship.gc_id"})
    owner_relationships: List["SubRelationship"] = Relationship(back_populates="owner", sa_relationship_kwargs={"foreign_keys": "SubRelationship.owner_id"})
    sub_relationships: List["SubRelationship"] = Relationship(back_populates="sub", sa_relationship_kwargs={"foreign_keys": "SubRelationship.sub_id"})
    ita_metrics: List["MetricsITA"] = Relationship(back_populates="sub")

class CompanyAlias(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    alias: str = Field(index=True)
    confidence: float = Field(default=1.0)
    
    company: Company = Relationship(back_populates="aliases")

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    location: Optional[str] = None
    owner_id: Optional[int] = Field(foreign_key="company.id", index=True)
    gc_id: Optional[int] = Field(foreign_key="company.id", index=True)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    relationships: List["SubRelationship"] = Relationship(back_populates="project")
    events: List["Event"] = Relationship(back_populates="project")

class SubRelationship(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gc_id: Optional[int] = Field(foreign_key="company.id", index=True)
    owner_id: Optional[int] = Field(foreign_key="company.id", index=True)
    sub_id: int = Field(foreign_key="company.id", index=True)
    project_id: Optional[int] = Field(foreign_key="project.id", index=True)
    trade: Optional[str] = None
    po_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    gc: Optional[Company] = Relationship(sa_relationship_kwargs={"foreign_keys": "SubRelationship.gc_id"})
    owner: Optional[Company] = Relationship(sa_relationship_kwargs={"foreign_keys": "SubRelationship.owner_id"})
    sub: Company = Relationship(sa_relationship_kwargs={"foreign_keys": "SubRelationship.sub_id"})
    project: Optional[Project] = Relationship(back_populates="relationships")

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)
    event_type: EventType = Field(index=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    project_id: Optional[int] = Field(foreign_key="project.id", index=True)
    occurred_on: datetime = Field(index=True)
    severity_score: float = Field(default=0.0)
    data: Dict[str, Any] = Field(default_factory=dict, sa_column_kwargs={"type_": "JSON"})
    link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    company: Company = Relationship(back_populates="events")
    project: Optional[Project] = Relationship(back_populates="events")

class MetricsITA(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sub_id: int = Field(foreign_key="company.id", index=True)
    year: int = Field(index=True)
    recordables: Optional[int] = None
    darts: Optional[int] = None
    hours_worked: Optional[int] = None
    dart_rate: Optional[float] = None
    source_link: Optional[str] = None
    
    sub: Company = Relationship(back_populates="ita_metrics")

class TargetOpportunity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gc_id: Optional[int] = Field(foreign_key="company.id", index=True)
    owner_id: Optional[int] = Field(foreign_key="company.id", index=True)
    driver_event_id: int = Field(foreign_key="event.id", index=True)
    propensity_score: float = Field(index=True)
    confidence: float = Field(default=0.0)
    recommended_talk_track: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    outreach_kits: List["OutreachKit"] = Relationship(back_populates="target")

class OutreachKit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="targetopportunity.id", index=True)
    email_md: str = ""
    linkedin_md: str = ""
    call_notes_md: str = ""
    attachments: Dict[str, Any] = Field(default_factory=dict, sa_column_kwargs={"type_": "JSON"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    target: TargetOpportunity = Relationship(back_populates="outreach_kits")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    role: str = Field(default="user")
    hashed_password: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(index=True)
    user_id: Optional[int] = Field(foreign_key="user.id", index=True)
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column_kwargs={"type_": "JSON"})
    created_at: datetime = Field(default_factory=datetime.utcnow)