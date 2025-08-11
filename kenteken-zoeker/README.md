
# Kenteken Zoeker — MVP (Supabase + FastAPI + Next.js)

Deze bundel is gegenereerd op 2025-08-11T14:09:07.221098Z.

## Mappen
- `db/` — Postgres schema (Supabase)
- `api/` — FastAPI + ETL (Python)
- `web/` — Next.js frontend

## Snel starten (lokaal)
1. Maak een database (bijv. Supabase) en kopieer je `DATABASE_URL`.
2. Voer `db/schema.sql` uit in je database (Supabase SQL Editor).
3. API installeren/starten:
   ```bash
   cd api
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   export DATABASE_URL=postgresql://...   # jouw connectiestring
   export ALLOWED_ORIGINS=http://localhost:3000
   export UPLOAD_TOKEN=vervang-door-een-lang-token
   uvicorn api.main:app --reload --port 8000
   ```
4. Web starten:
   ```bash
   cd web
   npm i
   export NEXT_PUBLIC_API_BASE=http://localhost:8000
   npm run dev
   ```

## Upload voorbeeld (met token)
```bash
curl -X POST   -H "X-Upload-Token: <jouw-token>"   -F "file=@./voorbeeld.xlsx"   -F "source_name=TestUpload"   http://localhost:8000/upload
```

## Deploy
- **DB:** Supabase → voer `db/schema.sql` uit.
- **API:** Render (Root: `api/`; Build: `pip install -r api/requirements.txt`; Start: `uvicorn api.main:app --host 0.0.0.0 --port 10000`).
  - Env: `DATABASE_URL`, `ALLOWED_ORIGINS`, `UPLOAD_TOKEN`.
- **Web:** Vercel (Root: `web/`; Env: `NEXT_PUBLIC_API_BASE` = jouw API URL).
