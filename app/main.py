from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, String, Text, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import os, re

DB=os.getenv("DATABASE_URL","sqlite:///./opspilot.db")
engine=create_engine(DB,connect_args={"check_same_thread":False} if DB.startswith("sqlite") else {})
class Base(DeclarativeBase): pass
class Document(Base):
    __tablename__="documents"; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(160)); content:Mapped[str]=mapped_column(Text); department:Mapped[str]=mapped_column(String(80),default="General")
class Run(Base):
    __tablename__="runs"; id:Mapped[int]=mapped_column(primary_key=True); question:Mapped[str]=mapped_column(Text); answer:Mapped[str]=mapped_column(Text); citations:Mapped[str]=mapped_column(Text)
Base.metadata.create_all(engine)
app=FastAPI(title="Floresis OpsPilot AI",version="1.0.0",description="Auditable enterprise knowledge and AI workflow API")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
class DocIn(BaseModel): title:str; content:str; department:str="General"
class AskIn(BaseModel): question:str

def score(q,text):
    terms=set(re.findall(r"[a-zA-Z]{3,}",q.lower())); body=text.lower(); return sum(body.count(t) for t in terms)
def answer(q,docs):
    ranked=sorted(((score(q,d.title+' '+d.content),d) for d in docs),reverse=True,key=lambda x:x[0]); chosen=[d for s,d in ranked if s>0][:3]
    if not chosen: return "No grounded evidence was found. Add relevant documents before relying on an answer.",[]
    snippets=[]
    for d in chosen:
        sentences=re.split(r'(?<=[.!?])\s+',d.content)
        best=max(sentences,key=lambda s:score(q,s)) if sentences else d.content[:300]
        snippets.append(f"{best.strip()} [{d.id}]")
    return "Evidence-backed synthesis: "+" ".join(snippets),[{"document_id":d.id,"title":d.title} for d in chosen]
@app.get("/health")
def health(): return {"status":"ok","service":"opspilot"}
@app.post("/api/documents")
def add_doc(x:DocIn):
    with Session(engine) as s: d=Document(**x.model_dump()); s.add(d); s.commit(); s.refresh(d); return {"id":d.id,**x.model_dump()}
@app.get("/api/documents")
def docs():
    with Session(engine) as s: return [{"id":d.id,"title":d.title,"department":d.department} for d in s.scalars(select(Document)).all()]
@app.post("/api/ask")
def ask(x:AskIn):
    with Session(engine) as s:
        ds=s.scalars(select(Document)).all(); a,c=answer(x.question,ds); r=Run(question=x.question,answer=a,citations=str(c)); s.add(r); s.commit(); return {"answer":a,"citations":c,"grounded":bool(c)}
@app.post("/api/seed")
def seed():
    samples=[("Q3 Delivery Review","Project Atlas is 18 days behind schedule because vendor integration testing started late. Management review is required before the next release gate.","PMO"),("AI Governance Policy","High-risk AI workflows require human approval, source citations, audit logs, and quarterly evaluation for accuracy and harmful outputs.","Risk"),("Support Operations","Priority-one incidents require acknowledgement within 15 minutes and an incident review within two business days.","Operations")]
    with Session(engine) as s:
        if not s.scalar(select(Document.id).limit(1)):
            s.add_all([Document(title=a,content=b,department=c) for a,b,c in samples]); s.commit()
    return {"seeded":True}
@app.get("/",response_class=HTMLResponse)
def home(): return open("app/static/index.html").read()
