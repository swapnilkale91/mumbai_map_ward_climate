"""
Pull OSM green-cover polygons (incl. the Sanjay Gandhi National Park edge) inside
the T-ward (Mulund) bounding box, via the Overpass API.

Prereq: run python/etl/fetch_boundary.py first (needs data/raw/t_ward.geojson).

What counts as "green":
  leisure   = park | garden | nature_reserve | recreation_ground
  landuse   = forest | grass | meadow | recreation_ground | village_green
  natural   = wood | scrub | heath | grassland
  boundary  = national_park        (Sanjay Gandhi National Park)

Output:
  data/raw/t_ward_green.geojson    FeatureCollection of polygons, each with
                                   properties {osm_id, osm_type, kind, name}

Notes:
  - Conversion is intentionally simple: closed ways -> Polygon; multipolygon
    relations -> one Polygon per outer member. Good enough for a heat-overlay
    spike; not a topologically perfect import.
  - Overpass is rate-limited; one query, ~25 s timeout. Re-run if it 429s.
"""

import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
T_WARD_PATH = ROOT / "data" / "raw" / "t_ward.geojson"
OUT_PATH = ROOT / "data" / "raw" / "t_ward_green.geojson"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# (tag key, set-of-values) -> these become the "kind" property
GREEN_TAGS = {
    "leisure": {"park", "garden", "nature_reserve", "recreation_ground"},
    "landuse": {"forest", "grass", "meadow", "recreation_ground", "village_green"},
    "natural": {"wood", "scrub", "heath", "grassland"},
    "boundary": {"national_park"},
}


def ward_bbox() -> tuple[float, float, float, float]:
    if not T_WARD_PATH.exists():
        sys.exit(f"Missing {T_WARD_PATH}. Run python/etl/fetch_boundary.py first.")
    fc = json.loads(T_WARD_PATH.read_text())
    coords = fc["features"][0]["geometry"]["coordinates"]

    def _pts(c):
        if isinstance(c[0], (int, float)):
            yield c
        else:
            for s in c:
                yield from _pts(s)

    pts = list(_pts(coords))
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    return (min(lats), min(lons), max(lats), max(lons))  # Overpass order: S,W,N,E


def build_query(bbox: tuple[float, float, float, float]) -> str:
    s, w, n, e = bbox
    clauses = []
    for key, values in GREEN_TAGS.items():
        regex = "|".join(sorted(values))
        for kind in ("way", "relation"):
            clauses.append(f'{kind}["{key}"~"^({regex})$"]({s},{w},{n},{e});')
    body = "\n  ".join(clauses)
    return f"[out:json][timeout:25];\n(\n  {body}\n);\nout geom;"


def run_overpass(query: str) -> dict:
    for attempt in range(3):
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in (429, 504):
            wait = 5 * (attempt + 1)
            print(f"  Overpass {resp.status_code}; retrying in {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
    sys.exit("Overpass kept returning 429/504. Try again later.")


def classify(tags: dict) -> str | None:
    for key, values in GREEN_TAGS.items():
        v = tags.get(key)
        if v in values:
            return f"{key}={v}"
    return None


def ring_from_geometry(geom: list) -> list | None:
    """geom is Overpass [{lat,lon},...]; return closed [[lon,lat],...] ring or None."""
    if not geom or len(geom) < 4:
        return None
    ring = [[p["lon"], p["lat"]] for p in geom]
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    if len(ring) < 4:
        return None
    return ring


def osm_to_features(data: dict) -> list[dict]:
    feats = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        kind = classify(tags)
        if not kind:
            continue
        name = tags.get("name", "")
        if el["type"] == "way":
            ring = ring_from_geometry(el.get("geometry", []))
            if not ring:
                continue
            geometry = {"type": "Polygon", "coordinates": [ring]}
            feats.append(_feat(el, "way", kind, name, geometry))
        elif el["type"] == "relation":
            polys = []
            for m in el.get("members", []):
                if m.get("role") == "outer" and m.get("type") == "way":
                    ring = ring_from_geometry(m.get("geometry", []))
                    if ring:
                        polys.append([ring])
            if not polys:
                continue
            geometry = (
                {"type": "Polygon", "coordinates": polys[0]} if len(polys) == 1
                else {"type": "MultiPolygon", "coordinates": polys}
            )
            feats.append(_feat(el, "relation", kind, name, geometry))
    return feats


def _feat(el: dict, osm_type: str, kind: str, name: str, geometry: dict) -> dict:
    return {
        "type": "Feature",
        "properties": {"osm_id": el["id"], "osm_type": osm_type, "kind": kind, "name": name},
        "geometry": geometry,
    }


def main() -> None:
    bbox = ward_bbox()
    print(f"T-ward bbox (S,W,N,E): {bbox[0]:.5f}, {bbox[1]:.5f}, {bbox[2]:.5f}, {bbox[3]:.5f}")
    query = build_query(bbox)
    print("Querying Overpass for green cover (parks, forest, SGNP edge)...")
    data = run_overpass(query)
    feats = osm_to_features(data)
    if not feats:
        sys.exit("No green features returned. Check the bbox / Overpass status.")

    by_kind: dict[str, int] = {}
    for f in feats:
        by_kind[f["properties"]["kind"]] = by_kind.get(f["properties"]["kind"], 0) + 1
    print(f"  {len(feats)} green polygons:")
    for k, c in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        print(f"    {k:32s} {c}")

    sgnp = [f for f in feats if "national_park" in f["properties"]["kind"]
            or "sanjay gandhi" in f["properties"]["name"].lower()]
    if sgnp:
        print(f"  Sanjay Gandhi National Park found: {[f['properties']['name'] for f in sgnp]}")
    else:
        print("  (No explicit SGNP polygon in bbox — park may be tagged outside the ward "
              "envelope; the forest/wood polygons along the west/north edge still capture it.)")

    fc = {"type": "FeatureCollection", "features": feats}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(fc, indent=2))
    print(f"  saved → {OUT_PATH}")
    print("\nDone. Next: python/viz/plot_lst.py overlays this on the Landsat LST raster.")


if __name__ == "__main__":
    main()
