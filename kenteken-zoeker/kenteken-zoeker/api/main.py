import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .etl import ETL

load_dotenv()
app = FastAPI(title="Kenteken Zoeker API")

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DATABASE_URL")
UPLOAD_TOKEN = os.getenv("UPLOAD_TOKEN")
etl = ETL(DB_URL)

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/search")
async def search(kenteken: str):
    if not kenteken:
        raise HTTPException(status_code=400, detail="kenteken is verplicht")
    res = etl.search_by_kenteken(kenteken)
    if not res:
        return {"found": False}
    return {"found": True, "data": res}

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    source_name: str = Form("Upload"),
    x_upload_token: str | None = Header(default=None, alias="X-Upload-Token")
):
    if not UPLOAD_TOKEN:
        raise HTTPException(status_code=500, detail="Server is niet geconfigureerd met UPLOAD_TOKEN")
    if x_upload_token != UPLOAD_TOKEN:
        raise HTTPException(status_code=401, detail="Ongeldig of ontbrekend X-Upload-Token")

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Upload een Excel (.xlsx/.xls)")
    content = await file.read()
    result = etl.ingest_excel(source_name=source_name, file_name=file.filename, content=content)
    return {"ok": True, **result}