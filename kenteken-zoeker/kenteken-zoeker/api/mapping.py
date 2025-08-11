from rapidfuzz import process, fuzz
import re

COLUMN_SYNONYMS = {
    "kenteken": ["kenteken", "licenseplate", "license_plate", "lp", "plate", "kenteken_nr"],
    "bandenmaat": ["bandenmaat", "bandmaat", "maat", "band_size", "tyresize", "bandenmaten"],
    "meldcode": ["meldcode", "mc", "meld_code"],
    "leasemaatschappij": ["leasemaatschappij", "lease maatschappij", "lease", "leaser", "lessor", "lease_company"],
    "wiba_status": ["wiba", "wiba_status", "wiba status", "status_wiba"]
}

CANONICAL_COLUMNS = list(COLUMN_SYNONYMS.keys())

def normalize_plate(value):
    if value is None:
        return None
    import re
    v = re.sub(r"[^A-Za-z0-9]", "", str(value)).upper()
    return v or None

def map_header_columns(headers):
    mapping = {}
    if not headers:
        return {c: None for c in CANONICAL_COLUMNS}
    for canon in CANONICAL_COLUMNS:
        candidates = COLUMN_SYNONYMS[canon]
        best = None
        best_score = -1
        for h in headers:
            for syn in candidates:
                from rapidfuzz import fuzz
                s = fuzz.token_set_ratio(h.lower(), syn)
                if s > best_score:
                    best_score = s
                    best = h
        if best and best_score >= 80:
            mapping[canon] = best
        else:
            match = process.extractOne(canon, headers, scorer=fuzz.token_set_ratio)
            if match and match[1] >= 80:
                mapping[canon] = match[0]
            else:
                mapping[canon] = None
    return mapping