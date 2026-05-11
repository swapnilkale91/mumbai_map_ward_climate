"""
Pull a dry-season Land Surface Temperature (LST) composite for T-ward (Mulund)
from Landsat 8 + 9 Collection 2 Level-2, using Google Earth Engine.

Prereqs:
  pip install -r requirements.txt
  earthengine authenticate          # one-time
  export EE_PROJECT=your-gcp-project # GEE now requires a Cloud project

Pipeline:
  1. read T-ward polygon from data/raw/t_ward.geojson  (run fetch_boundary.py first)
  2. merge LC08 + LC09 C2L2, filter to AOI + dry-season window
  3. cloud/shadow mask via QA_PIXEL bits
  4. scale ST_B10 -> Kelvin -> Celsius
  5. median composite, clip to T-ward
  6. export:
       - data/raw/t_ward_lst.tif    (GeoTIFF, ~30 m, via getDownloadURL)
       - output/t_ward_lst_quicklook.png  (thumbnail, for an instant look)
     and print min / mean / max LST over the ward.

Notes:
  - getDownloadURL works because one BMC ward is small. For larger AOIs switch to
    ee.batch.Export.image.toDrive().
  - Default window is the hot pre-monsoon season (Mar-May) across 2 years to get
    enough clear scenes. Override with --start / --end.
"""

import argparse
import io
import json
import os
import sys
import zipfile
from pathlib import Path

import requests

try:
    import ee
except ImportError:
    sys.exit("earthengine-api not installed. Run: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parents[2]
T_WARD_PATH = ROOT / "data" / "raw" / "t_ward.geojson"
TIF_OUT = ROOT / "data" / "raw" / "t_ward_lst.tif"
PNG_OUT = ROOT / "output" / "t_ward_lst_quicklook.png"

# Landsat C2 L2 surface-temperature scaling (USGS): K = DN*0.00341802 + 149.0
ST_MULT, ST_ADD = 0.00341802, 149.0
KELVIN_TO_C = -273.15

DEFAULT_START = "2022-03-01"
DEFAULT_END = "2024-06-01"
DRY_MONTHS = [3, 4, 5]  # pre-monsoon, hottest & clearest


def init_ee() -> None:
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project) if project else ee.Initialize()
    except Exception:
        # First run on a machine: trigger the auth flow, then retry.
        ee.Authenticate()
        ee.Initialize(project=project) if project else ee.Initialize()


def load_aoi() -> "ee.Geometry":
    if not T_WARD_PATH.exists():
        sys.exit(f"Missing {T_WARD_PATH}. Run python/etl/fetch_boundary.py first.")
    fc = json.loads(T_WARD_PATH.read_text())
    geom = fc["features"][0]["geometry"]
    return ee.Geometry(geom)


def mask_l2_clouds(img: "ee.Image") -> "ee.Image":
    """Mask cloud, cloud-shadow, dilated-cloud and cirrus using QA_PIXEL bits."""
    qa = img.select("QA_PIXEL")
    # Bit 1 dilated cloud, 3 cloud, 4 cloud shadow, 2 cirrus
    bad = (
        qa.bitwiseAnd(1 << 1).neq(0)
        .Or(qa.bitwiseAnd(1 << 2).neq(0))
        .Or(qa.bitwiseAnd(1 << 3).neq(0))
        .Or(qa.bitwiseAnd(1 << 4).neq(0))
    )
    return img.updateMask(bad.Not())


def to_lst_celsius(img: "ee.Image") -> "ee.Image":
    lst_c = (
        img.select("ST_B10")
        .multiply(ST_MULT).add(ST_ADD)   # -> Kelvin
        .add(KELVIN_TO_C)                 # -> Celsius
        .rename("LST_C")
    )
    return lst_c.copyProperties(img, ["system:time_start"])


def build_lst_composite(aoi: "ee.Geometry", start: str, end: str) -> "ee.Image":
    col = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2"))
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.calendarRange(DRY_MONTHS[0], DRY_MONTHS[-1], "month"))
        .filter(ee.Filter.lt("CLOUD_COVER", 60))
        .map(mask_l2_clouds)
        .map(to_lst_celsius)
    )
    n = col.size().getInfo()
    if n == 0:
        sys.exit("No Landsat scenes matched the AOI/date filters. Widen --start/--end.")
    print(f"  {n} masked Landsat scenes in composite ({start} → {end}, months {DRY_MONTHS})")
    return col.median().clip(aoi)


def report_stats(img: "ee.Image", aoi: "ee.Geometry") -> None:
    stats = img.reduceRegion(
        reducer=ee.Reducer.min().combine(ee.Reducer.mean(), sharedInputs=True)
        .combine(ee.Reducer.max(), sharedInputs=True),
        geometry=aoi, scale=30, maxPixels=1e9,
    ).getInfo()
    print(f"  LST over T-ward (°C): min={stats.get('LST_C_min'):.1f}  "
          f"mean={stats.get('LST_C_mean'):.1f}  max={stats.get('LST_C_max'):.1f}")


def download_geotiff(img: "ee.Image", aoi: "ee.Geometry") -> None:
    url = img.getDownloadURL({
        "scale": 30, "region": aoi, "format": "GEO_TIFF", "bands": ["LST_C"],
    })
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    TIF_OUT.parent.mkdir(parents=True, exist_ok=True)
    content = r.content
    # getDownloadURL may hand back a zip for some formats; handle both.
    if content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            tif_name = next(n for n in z.namelist() if n.lower().endswith(".tif"))
            TIF_OUT.write_bytes(z.read(tif_name))
    else:
        TIF_OUT.write_bytes(content)
    print(f"  saved → {TIF_OUT}")


def download_quicklook(img: "ee.Image", aoi: "ee.Geometry") -> None:
    vis = {"min": 24, "max": 42,
           "palette": ["#2c7bb6", "#abd9e9", "#ffffbf", "#fdae61", "#d7191c"]}
    url = img.getThumbURL({**vis, "region": aoi, "dimensions": 700, "format": "png"})
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)
    PNG_OUT.write_bytes(r.content)
    print(f"  saved → {PNG_OUT}  (blue≈24°C → red≈42°C)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--no-tif", action="store_true", help="skip the GeoTIFF download")
    args = ap.parse_args()

    print("Initialising Earth Engine...")
    init_ee()
    aoi = load_aoi()
    print("Building Landsat 8/9 LST composite for T-ward (Mulund)...")
    lst = build_lst_composite(aoi, args.start, args.end)
    report_stats(lst, aoi)
    download_quicklook(lst, aoi)
    if not args.no_tif:
        download_geotiff(lst, aoi)
    print("\nDone. Next: overlay OSM green cover (fetch_osm_green.py) and plot the "
          "SGNP-edge → interior gradient.")


if __name__ == "__main__":
    main()
