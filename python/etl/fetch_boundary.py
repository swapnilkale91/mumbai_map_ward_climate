"""
Fetch BMC ward boundaries from datameet/Municipal_Spatial_Data and isolate T-ward (Mulund).

Source: https://github.com/datameet/Municipal_Spatial_Data/blob/master/Mumbai/BMC_Wards.geojson
  - FeatureCollection with 24 BMC administrative wards
  - Each feature has: { "gid": <int>, "name": "<letter>" }
  - T-ward (Mulund) => gid=13, name="T"

Outputs:
  data/raw/bmc_wards.geojson   full 24-ward file
  data/raw/t_ward.geojson      T-ward polygon only
"""

import json
import sys
from pathlib import Path

import requests

SOURCE_URL = (
    "https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data"
    "/master/Mumbai/BMC_Wards.geojson"
)
TARGET_WARD = "T"

OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def fetch_geojson(url: str) -> dict:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"Expected FeatureCollection, got {data.get('type')!r}")
    return data


def find_ward(geojson: dict, name: str) -> dict:
    """Return the GeoJSON Feature whose 'name' property matches *name* (case-insensitive)."""
    matches = [
        f for f in geojson["features"]
        if str(f.get("properties", {}).get("name", "")).upper() == name.upper()
    ]
    if not matches:
        available = sorted(f["properties"].get("name") for f in geojson["features"])
        raise LookupError(
            f"Ward {name!r} not found. Available names: {available}"
        )
    if len(matches) > 1:
        raise LookupError(f"Multiple features match ward name {name!r}: {matches}")
    return matches[0]


def save_geojson(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    print(f"  saved → {path}")


def summarise_feature(feature: dict) -> None:
    props = feature["properties"]
    geom = feature["geometry"]
    coords = geom.get("coordinates", [])

    # Flatten all coordinate pairs to compute bbox
    def _flatten(c):
        if isinstance(c[0], (int, float)):
            yield c
        else:
            for sub in c:
                yield from _flatten(sub)

    all_pts = list(_flatten(coords))
    lons = [p[0] for p in all_pts]
    lats = [p[1] for p in all_pts]
    bbox = (min(lons), min(lats), max(lons), max(lats))

    print(f"  gid        : {props['gid']}")
    print(f"  name       : {props['name']}")
    print(f"  geom type  : {geom['type']}")
    print(f"  bbox (W,S,E,N): {bbox[0]:.5f}, {bbox[1]:.5f}, {bbox[2]:.5f}, {bbox[3]:.5f}")
    print(f"  ring count : {len(coords)}")


def main() -> None:
    print(f"Fetching BMC ward boundaries from:\n  {SOURCE_URL}\n")
    geojson = fetch_geojson(SOURCE_URL)

    n = len(geojson["features"])
    print(f"Valid FeatureCollection — {n} ward features found.")
    print(f"Wards: {sorted(f['properties']['name'] for f in geojson['features'])}\n")

    # Save full file
    save_geojson(geojson, OUT_DIR / "bmc_wards.geojson")

    # Isolate T-ward
    print(f"\nSearching for ward {TARGET_WARD!r} (Mulund)...")
    t_ward = find_ward(geojson, TARGET_WARD)
    print(f"Found ward {TARGET_WARD!r}:")
    summarise_feature(t_ward)

    # Wrap as standalone FeatureCollection
    t_fc = {"type": "FeatureCollection", "features": [t_ward]}
    save_geojson(t_fc, OUT_DIR / "t_ward.geojson")

    print("\nAll checks passed. T-ward boundary is ready for LST/OSM overlay.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
