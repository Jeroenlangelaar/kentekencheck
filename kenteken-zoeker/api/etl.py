import io
import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values
from .mapping import map_header_columns, normalize_plate

class ETL:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def _conn(self):
        return psycopg2.connect(self.db_url)

    def ingest_excel(self, source_name: str, file_name: str, content: bytes, schema_hint: dict | None = None):
        xls = pd.ExcelFile(io.BytesIO(content))
        frames = []
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            if df.empty:
                continue
            df.columns = [str(c).strip() for c in df.columns]
            frames.append(df)
        if not frames:
            return {"rows": 0}
        df = pd.concat(frames, ignore_index=True)

        headers = list(df.columns)
        mapping = map_header_columns(headers) if not schema_hint else schema_hint

        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                "insert into public.sources (name, file_name, schema_hint) values (%s,%s,%s) returning id",
                (source_name, file_name, json.dumps(mapping))
            )
            source_id = cur.fetchone()[0]

        raw_rows = []
        canon_rows = []
        for _, row in df.iterrows():
            row_dict = {str(k): (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            k_val = row_dict.get(mapping.get("kenteken")) if mapping.get("kenteken") else None
            kenteken_norm = normalize_plate(k_val) if k_val else None
            raw_rows.append((source_id, json.dumps(row_dict), k_val, kenteken_norm))

            if kenteken_norm:
                canon = {
                    "kenteken": kenteken_norm,
                    "bandenmaat": row_dict.get(mapping.get("bandenmaat")),
                    "meldcode": row_dict.get(mapping.get("meldcode")),
                    "leasemaatschappij": row_dict.get(mapping.get("leasemaatschappij")),
                    "wiba_status": row_dict.get(mapping.get("wiba_status"))
                }
                canon_rows.append(canon)

        with self._conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                "insert into public.facts_raw (source_id, row_data, kenteken_raw, kenteken_norm) values %s",
                raw_rows
            )

        upsert_values = [
            (
                r["kenteken"],
                r.get("bandenmaat"),
                r.get("meldcode"),
                r.get("leasemaatschappij"),
                r.get("wiba_status")
            ) for r in canon_rows
        ]
        if upsert_values:
            with self._conn() as conn, conn.cursor() as cur:
                cur.execute(
                    "create temp table if not exists tmp_upsert (kenteken text, bandenmaat text, meldcode text, leasemaatschappij text, wiba_status text) on commit drop;"
                )
                execute_values(cur, "insert into tmp_upsert values %s", upsert_values)
                cur.execute(
                    "insert into public.vehicles as v (kenteken, bandenmaat, meldcode, leasemaatschappij, wiba_status, first_seen_at, last_seen_at) "
                    "select t.kenteken, t.bandenmaat, t.meldcode, t.leasemaatschappij, t.wiba_status, now(), now() "
                    "from tmp_upsert t "
                    "on conflict (kenteken) do update set "
                    "bandenmaat = coalesce(excluded.bandenmaat, v.bandenmaat), "
                    "meldcode = coalesce(excluded.meldcode, v.meldcode), "
                    "leasemaatschappij = coalesce(excluded.leasemaatschappij, v.leasemaatschappij), "
                    "wiba_status = coalesce(excluded.wiba_status, v.wiba_status), "
                    "last_seen_at = now();"
                )

        return {"rows": len(canon_rows)}

    def search_by_kenteken(self, kenteken: str):
        k = normalize_plate(kenteken)
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                "select kenteken, bandenmaat, meldcode, leasemaatschappij, wiba_status, last_seen_at from public.public_vehicles where kenteken = %s",
                (k,)
            )
            row = cur.fetchone()
            if not row:
                return None
            keys = ["kenteken", "bandenmaat", "meldcode", "leasemaatschappij", "wiba_status", "last_seen_at"]
            return dict(zip(keys, row))