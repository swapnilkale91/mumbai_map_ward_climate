"""
Quick preview of the BMC ward boundaries with T-ward (Mulund) highlighted.

Reads data/raw/bmc_wards.geojson (produced by python/etl/fetch_boundary.py) and
renders output/t_ward_preview.png — a simple sanity-check map before we layer on
Landsat LST and OSM green cover.

Run python/etl/fetch_boundary.py first.
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

ROOT = Path(__file__).resolve().parents[2]
WARDS_PATH = ROOT / "data" / "raw" / "bmc_wards.geojson"
OUT_PATH = ROOT / "output" / "t_ward_preview.png"
TARGET_WARD = "T"


def iter_polygons(geometry):
    """Yield lists of (lon, lat) exterior rings from Polygon / MultiPolygon."""
    gtype = geometry["type"]
    coords = geometry["coordinates"]
    if gtype == "Polygon":
        yield coords[0]
    elif gtype == "MultiPolygon":
        for poly in coords:
            yield poly[0]
    else:
        raise ValueError(f"Unsupported geometry type: {gtype}")


def main() -> None:
    if not WARDS_PATH.exists():
        sys.exit(f"Missing {WARDS_PATH}. Run python/etl/fetch_boundary.py first.")

    geojson = json.loads(WARDS_PATH.read_text())
    fig, ax = plt.subplots(figsize=(9, 11))

    other_patches, t_patches = [], []
    for feat in geojson["features"]:
        name = feat["properties"]["name"]
        is_t = name.upper() == TARGET_WARD.upper()
        for ring in iter_polygons(feat["geometry"]):
            patch = MplPolygon(ring, closed=True)
            (t_patches if is_t else other_patches).append(patch)
        # label at centroid-ish (first ring mean)
        ring0 = next(iter_polygons(feat["geometry"]))
        cx = sum(p[0] for p in ring0) / len(ring0)
        cy = sum(p[1] for p in ring0) / len(ring0)
        ax.text(cx, cy, name, ha="center", va="center",
                fontsize=11 if is_t else 8,
                fontweight="bold" if is_t else "normal",
                color="darkred" if is_t else "#444")

    ax.add_collection(PatchCollection(other_patches, facecolor="#e8eef0",
                                      edgecolor="#888", linewidths=0.6))
    ax.add_collection(PatchCollection(t_patches, facecolor="#ffb3a7",
                                      edgecolor="darkred", linewidths=1.8, alpha=0.85))

    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_title("Mumbai BMC Wards — T-ward (Mulund) highlighted\n"
                 "Source: datameet/Municipal_Spatial_Data", fontsize=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=130)
    print(f"saved → {OUT_PATH}")


if __name__ == "__main__":
    main()
