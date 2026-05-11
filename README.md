# Mumbai Ward-Level Heat Vulnerability Dashboard

Spike: Land Surface Temperature (LST) gradient from Sanjay Gandhi National Park edge into the built interior of **T-ward (Mulund)**, overlaid with OSM green cover.

## Stack
- Python 3.11+
- Google Earth Engine (via `earthengine-api`)
- Landsat 8/9 Collection 2 Level-2 (ST_B10 band → LST)
- OSM green cover via Overpass API
- GeoPandas, Matplotlib / Folium for visualisation

## Data Sources
| Layer | Source | Notes |
|---|---|---|
| Ward boundaries | [datameet/Municipal_Spatial_Data](https://github.com/datameet/Municipal_Spatial_Data/blob/master/Mumbai/BMC_Wards.geojson) | 24 BMC admin wards, `name` field (e.g. `"T"`) |
| LST | Landsat 8/9 via GEE | ST_B10 scaled → °C |
| Green cover | OSM Overpass API | `landuse=forest/park`, `natural=wood` |

## Ward Reference
Mumbai has 24 administrative wards (A–T). T-ward (Mulund) is `gid=13, name="T"` in the BMC GeoJSON.

## ETL Pipeline

```
python/etl/
  fetch_boundary.py   ← Step 1: download & validate BMC ward GeoJSON, isolate T-ward
  fetch_lst.py        ← Step 2 (TODO): pull Landsat LST via GEE for T-ward bbox
  fetch_osm_green.py  ← Step 3 (TODO): pull OSM green polygons via Overpass
```

## Setup

```bash
pip install -r requirements.txt
# Authenticate GEE once:
earthengine authenticate
```

## Running the T-ward spike

```bash
python python/etl/fetch_boundary.py
# Outputs: data/raw/bmc_wards.geojson  (full 24-ward file)
#          data/raw/t_ward.geojson      (T-ward polygon only)
```
