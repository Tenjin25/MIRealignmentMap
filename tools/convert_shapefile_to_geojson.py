"""
Convert Michigan county shapefile to GeoJSON
"""
import geopandas as gpd
import json
from pathlib import Path

# Paths
script_dir = Path(__file__).parent
data_dir = script_dir.parent / 'data'
shapefile = data_dir / 'tl_2020_26_county20' / 'tl_2020_26_county20.shp'
output_file = data_dir / 'tl_2020_26_county20.geojson'

print(f"Reading shapefile: {shapefile}")
gdf = gpd.read_file(shapefile)

# Convert to WGS84 (standard lat/lon)
print("Converting to WGS84...")
gdf = gdf.to_crs(epsg=4326)

# Display info
print(f"\nShapefile info:")
print(f"  Counties: {len(gdf)}")
print(f"  Columns: {list(gdf.columns)}")
print(f"\nFirst few counties:")
print(gdf[['NAME20', 'COUNTYFP20', 'GEOID20']].head())

# Save as GeoJSON
print(f"\nSaving to: {output_file}")
gdf.to_file(output_file, driver='GeoJSON')

# Verify file size
file_size = output_file.stat().st_size / (1024 * 1024)
print(f"GeoJSON created: {file_size:.2f} MB")
print("Done!")
