"""
The payoff figure: T-ward (Mulund) Land Surface Temperature with OSM green cover
on top, plus a west→east LST transect showing the Sanjay Gandhi National Park
edge → built-interior heat gradient.

Inputs (produce these first):
  data/raw/t_ward_lst.tif      ← python/etl/fetch_lst.py
  data/raw/t_ward.geojson      ← python/etl/fetch_boundary.py
  data/raw/t_ward_green.geojson← python/etl/fetch_osm_green.py   (optional but recommended)

Output:
  output/t_ward_lst_green.png  ← two-panel figure (map + transect profile)
"""

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

try:
    import rasterio
    from rasterio.transform import rowcol
except ImportError:
    sys.exit("rasterio not installed. Run: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parents[2]
LST_TIF = ROOT / "data" / "raw" / "t_ward_lst.tif"
WARD_GEOJSON = ROOT / "data" / "raw" / "t_ward.geojson"
GREEN_GEOJSON = ROOT / "data" / "raw" / "t_ward_green.geojson"
OUT_PNG = ROOT / "output" / "t_ward_lst_green.png"

LST_PALETTE = ["#2c7bb6", "#abd9e9", "#ffffbf", "#fdae61", "#d7191c"]


def _rings(geometry):
    """Yield exterior rings [[lon,lat],...] from Polygon / MultiPolygon."""
    t, c = geometry["type"], geometry["coordinates"]
    if t == "Polygon":
        yield c[0]
    elif t == "MultiPolygon":
        for poly in c:
            yield poly[0]


def load_polygons(path: Path):
    if not path.exists():
        return []
    fc = json.loads(path.read_text())
    out = []
    for feat in fc["features"]:
        for ring in _rings(feat["geometry"]):
            out.append((ring, feat.get("properties", {})))
    return out


def sample_transect(src, lst, row_frac=0.5, n=200):
    """Sample LST along a west→east line at a fixed fraction down the raster."""
    h, w = lst.shape
    r = int(h * row_frac)
    cols = np.linspace(0, w - 1, n).astype(int)
    vals = lst[r, cols]
    # x positions in metres from the west edge (transform[0] = pixel width in CRS units)
    px = abs(src.transform.a)
    # If CRS is geographic (degrees), convert to approx metres at this latitude.
    if src.crs and src.crs.is_geographic:
        lon0, lat0 = src.xy(r, 0)
        m_per_deg = 111_320 * np.cos(np.deg2rad(lat0))
        dist_m = cols * px * m_per_deg
    else:
        dist_m = cols * px
    lat_of_row = src.xy(r, 0)[1]
    return dist_m, vals, lat_of_row


def main() -> None:
    if not LST_TIF.exists():
        sys.exit(f"Missing {LST_TIF}. Run python/etl/fetch_lst.py first.")

    with rasterio.open(LST_TIF) as src:
        lst = src.read(1, masked=True).filled(np.nan)
        left, bottom, right, top = src.bounds
        extent = (left, right, bottom, top)
        dist_m, transect, transect_lat = sample_transect(src, lst)

    finite = lst[np.isfinite(lst)]
    vmin, vmax = (np.nanpercentile(finite, 2), np.nanpercentile(finite, 98)) if finite.size else (24, 42)

    ward_polys = load_polygons(WARD_GEOJSON)
    green_polys = load_polygons(GREEN_GEOJSON)

    fig, (ax_map, ax_prof) = plt.subplots(
        1, 2, figsize=(15, 8), gridspec_kw={"width_ratios": [1.3, 1]}
    )

    # --- left: LST map + green overlay + ward outline + transect line ---
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("lst", LST_PALETTE)
    im = ax_map.imshow(lst, extent=extent, origin="upper", cmap=cmap, vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(im, ax=ax_map, fraction=0.045, pad=0.02)
    cbar.set_label("Land Surface Temperature (°C)")

    if green_polys:
        patches = [MplPolygon(ring, closed=True) for ring, _ in green_polys]
        ax_map.add_collection(PatchCollection(
            patches, facecolor="none", edgecolor="#1a7d1a", linewidths=1.0, alpha=0.9))
        # one legend proxy
        ax_map.plot([], [], color="#1a7d1a", lw=1.5, label="OSM green cover")

    for ring, _ in ward_polys:
        ax_map.add_patch(MplPolygon(ring, closed=True, facecolor="none",
                                    edgecolor="black", linewidth=2.0))
    ax_map.plot([], [], color="black", lw=2, label="T-ward boundary")

    ax_map.axhline(transect_lat, color="magenta", lw=1.6, ls="--")
    ax_map.plot([], [], color="magenta", lw=1.6, ls="--", label="W→E transect")

    ax_map.set_xlim(left, right)
    ax_map.set_ylim(bottom, top)
    ax_map.set_aspect("equal")
    ax_map.set_title("T-ward (Mulund) — Landsat 8/9 dry-season LST + OSM green cover")
    ax_map.set_xlabel("Longitude")
    ax_map.set_ylabel("Latitude")
    ax_map.legend(loc="lower right", fontsize=9, framealpha=0.9)

    # --- right: transect profile (SGNP edge on the west → built interior east) ---
    ax_prof.plot(dist_m / 1000.0, transect, color="#d7191c", lw=2)
    ax_prof.fill_between(dist_m / 1000.0, transect, np.nanmin(transect), alpha=0.15, color="#d7191c")
    ax_prof.set_xlabel("Distance east from ward's west edge (km)")
    ax_prof.set_ylabel("LST (°C)")
    ax_prof.set_title(f"LST gradient along W→E transect (lat ≈ {transect_lat:.3f}°)\n"
                      "left = Sanjay Gandhi National Park side → right = built interior")
    ax_prof.grid(alpha=0.3)
    if np.isfinite(transect).any():
        ax_prof.annotate(f"Δ ≈ {np.nanmax(transect) - np.nanmin(transect):.1f} °C",
                         xy=(0.5, 0.92), xycoords="axes fraction", ha="center",
                         fontsize=11, fontweight="bold")

    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=130)
    print(f"saved → {OUT_PNG}")


if __name__ == "__main__":
    main()
