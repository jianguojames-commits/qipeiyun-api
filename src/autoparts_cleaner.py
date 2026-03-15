import argparse
import csv
import json
import re
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_decimal(x):
    if x is None:
        return None
    if isinstance(x, (int, float, Decimal)):
        try:
            return Decimal(str(x))
        except InvalidOperation:
            return None
    s = str(x).strip().replace(",", "")
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def normalize_part_number(x):
    if not x:
        return None
    s = str(x).upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s or None

def normalize_brand(x, brand_aliases):
    if not x:
        return None, False
    s = str(x).strip()
    key = s.lower()
    if key in brand_aliases:
        return brand_aliases[key], True
    return s, False

def map_category(x, category_map):
    if not x:
        return None
    s = str(x).strip().lower()
    return category_map.get(s, s.title())

def parse_vehicle(text):
    if not text:
        return None, None, None
    t = str(text).strip()
    m = re.match(r"^([A-Za-z\u4e00-\u9fa5\-\s]+)\s+([A-Za-z0-9\u4e00-\u9fa5\-\s]+)\s+(\d{4})(?:\s*[-~]\s*(\d{4}|\+))?", t)
    if m:
        make = m.group(1).strip()
        model = m.group(2).strip()
        y1 = int(m.group(3))
        y2 = m.group(4)
        y2v = None if not y2 or y2 == "+" else int(y2)
        return make, model, (y1, y2v)
    parts = t.split(" ")
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:]), (None, None)
    return t, None, (None, None)

def to_kg(weight, unit):
    if weight is None:
        return None
    w = safe_decimal(weight)
    if w is None:
        return None
    u = (unit or "kg").strip().lower()
    if u in ["kg", "kilogram", "公斤"]:
        return float(w)
    if u in ["g", "gram", "克"]:
        return float(w / Decimal("1000"))
    if u in ["lb", "lbs", "pound"]:
        return float(w * Decimal("0.45359237"))
    return float(w)

def mm_tuple(l, w, h):
    lv = safe_decimal(l)
    wv = safe_decimal(w)
    hv = safe_decimal(h)
    return (
        float(lv) if lv is not None else None,
        float(wv) if wv is not None else None,
        float(hv) if hv is not None else None,
    )

def stable_id(*values):
    base = "|".join([str(v) for v in values if v])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

def record_key(rec):
    return (
        rec.get("brand"),
        rec.get("oe_number") or rec.get("sku") or rec.get("part_id"),
    )

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def iter_raw_records(raw_dir: Path):
    for p in raw_dir.glob("**/*"):
        if p.is_file() and p.suffix.lower() == ".csv":
            with open(p, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
        elif p.is_file() and p.suffix.lower() == ".json":
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, dict):
                            yield row
                elif isinstance(data, dict):
                    yield data

def clean_record(row, brand_aliases, category_map, default_currency):
    oe = normalize_part_number(row.get("oe_number") or row.get("oe") or row.get("OE") or row.get("part_no"))
    sku = normalize_part_number(row.get("sku") or row.get("SKU") or row.get("mpn"))
    brand_raw = row.get("brand") or row.get("Brand") or row.get("manufacturer")
    brand, brand_was_alias = normalize_brand(brand_raw, brand_aliases)
    category = map_category(row.get("category") or row.get("Category") or row.get("type"), category_map)
    name = row.get("name") or row.get("Name") or row.get("title")
    desc = row.get("description") or row.get("desc")
    vehicle_text = row.get("vehicle") or row.get("fitment") or row.get("compatible_with")
    make, model, years = parse_vehicle(vehicle_text)
    pos = row.get("position") or row.get("Position")
    specs_raw = row.get("specs") or row.get("attributes")
    if isinstance(specs_raw, dict):
        specs = specs_raw
    else:
        try:
            specs = json.loads(specs_raw) if specs_raw else {}
        except Exception:
            specs = {}
    uom = row.get("uom") or row.get("unit")
    qty_per_unit = safe_decimal(row.get("qty_per_unit") or row.get("ppu") or 1)
    price = safe_decimal(row.get("price") or row.get("Price"))
    currency = (row.get("currency") or row.get("Currency") or default_currency).upper()
    supplier = row.get("supplier") or row.get("Supplier")
    barcode = str(row.get("barcode") or row.get("ean") or "").strip() or None
    weight_kg = to_kg(row.get("weight"), row.get("weight_unit"))
    lmm, wmm, hmm = mm_tuple(row.get("length_mm"), row.get("width_mm"), row.get("height_mm"))
    ystart = years[0] if years else None
    yend = years[1] if years else None
    pid = stable_id(brand, oe or sku)
    return {
        "part_id": pid,
        "oe_number": oe,
        "sku": sku,
        "brand": brand,
        "category": category,
        "name": name,
        "description": desc,
        "vehicle_make": make,
        "vehicle_model": model,
        "vehicle_year_start": ystart,
        "vehicle_year_end": yend,
        "position": pos,
        "specs": json.dumps(specs, ensure_ascii=False, sort_keys=True),
        "uom": uom,
        "qty_per_unit": float(qty_per_unit) if qty_per_unit is not None else None,
        "price": float(price) if price is not None else None,
        "currency": currency,
        "supplier": supplier,
        "barcode": barcode,
        "weight_kg": weight_kg,
        "length_mm": lmm,
        "width_mm": wmm,
        "height_mm": hmm,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "_brand_alias_used": brand_was_alias,
    }

def deduplicate(records):
    seen = {}
    out = []
    for r in records:
        k = record_key(r)
        if k in seen:
            continue
        seen[k] = True
        out.append(r)
    return out

def write_clean_csv(recs, out_path: Path):
    if not recs:
        return
    headers = [
        "part_id","oe_number","sku","brand","category","name","description","vehicle_make","vehicle_model","vehicle_year_start","vehicle_year_end","position","specs","uom","qty_per_unit","price","currency","supplier","barcode","weight_kg","length_mm","width_mm","height_mm","created_at"
    ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k) for k in headers})

def build_triples(recs):
    triples = []
    for r in recs:
        pid = r["part_id"]
        brand = r.get("brand")
        category = r.get("category")
        make = r.get("vehicle_make")
        model = r.get("vehicle_model")
        supplier = r.get("supplier")
        if brand:
            triples.append({"subject_id": f"part:{pid}", "subject_type": "Part", "predicate": "MADE_BY", "object_id": f"brand:{brand}", "object_type": "Brand", "label": brand})
        if category:
            triples.append({"subject_id": f"part:{pid}", "subject_type": "Part", "predicate": "BELONGS_TO", "object_id": f"category:{category}", "object_type": "Category", "label": category})
        if make:
            vid = f"vehicle:{make}:{model or ''}"
            triples.append({"subject_id": f"part:{pid}", "subject_type": "Part", "predicate": "COMPATIBLE_WITH", "object_id": vid, "object_type": "Vehicle", "label": (model or make)})
        if supplier:
            triples.append({"subject_id": f"supplier:{supplier}", "subject_type": "Supplier", "predicate": "SUPPLIES", "object_id": f"part:{pid}", "object_type": "Part", "label": supplier})
    return triples

def write_triples_csv(triples, out_path: Path):
    if not triples:
        return
    headers = ["subject_id","subject_type","predicate","object_id","object_type","label"]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for t in triples:
            w.writerow(t)

def run_rules(recs, rules_cfg):
    issues = []
    stats = {"price_flags": 0, "missing_specs": 0, "brand_alias_used": 0}
    price_cfg = rules_cfg.get("price", {})
    req_specs = rules_cfg.get("required_specs_by_category", {})
    for r in recs:
        cat = (r.get("category") or "").lower()
        price = r.get("price")
        if cat in price_cfg and price is not None:
            rng = price_cfg[cat]
            low = rng.get("min")
            high = rng.get("max")
            flag = (low is not None and price < low) or (high is not None and price > high)
            if flag:
                stats["price_flags"] += 1
                issues.append({"part_id": r["part_id"], "type": "price_out_of_range", "category": r.get("category"), "price": price})
        need = req_specs.get(cat)
        if need:
            try:
                s = json.loads(r.get("specs") or "{}")
            except Exception:
                s = {}
            missing = [k for k in need if k not in s or s.get(k) in (None, "", 0)]
            if missing:
                stats["missing_specs"] += 1
                issues.append({"part_id": r["part_id"], "type": "missing_specs", "missing": ",".join(missing)})
        if r.get("_brand_alias_used"):
            stats["brand_alias_used"] += 1
    return stats, issues

def write_issues_csv(issues, out_path: Path):
    if not issues:
        return
    keys = sorted({k for d in issues for k in d.keys()})
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for it in issues:
            w.writerow(it)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--configs", required=True)
    ap.add_argument("--currency", default="CNY")
    args = ap.parse_args()
    raw_dir = Path(args.raw)
    out_dir = Path(args.out)
    cfg_dir = Path(args.configs)
    ensure_dir(out_dir)
    brand_aliases = {}
    p = cfg_dir / "brand_aliases.json"
    if p.exists():
        tmp = load_json(p)
        brand_aliases = {k.lower(): v for k, v in tmp.items()}
    category_map = {}
    p = cfg_dir / "category_map.json"
    if p.exists():
        tmp = load_json(p)
        category_map = {k.lower(): v for k, v in tmp.items()}
    rules_cfg = {}
    p = cfg_dir / "rules.json"
    if p.exists():
        rules_cfg = load_json(p)
    cleaned = []
    for row in iter_raw_records(raw_dir):
        rec = clean_record(row, brand_aliases, category_map, args.currency)
        cleaned.append(rec)
    cleaned = deduplicate(cleaned)
    write_clean_csv(cleaned, out_dir / "clean_parts.csv")
    triples = build_triples(cleaned)
    write_triples_csv(triples, out_dir / "triples.csv")
    stats, issues = run_rules(cleaned, rules_cfg)
    with open(out_dir / "decisions.json", "w", encoding="utf-8") as f:
        json.dump({"summary": stats, "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"}, f, ensure_ascii=False, indent=2)
    write_issues_csv(issues, out_dir / "issues.csv")

if __name__ == "__main__":
    main()

