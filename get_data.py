import duckdb
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

con = duckdb.connect()

con.execute("INSTALL spatial;")
con.execute("LOAD spatial;")

con.execute("CREATE OR REPLACE SCHEMA spatial;")
con.execute("CREATE OR REPLACE SCHEMA azure;")
con.execute("SET azure_transport_option_type = 'curl';")

azure_storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=overturemapswestus2;AccountKey=;EndpointSuffix=core.windows.net'
con.execute(f"SET azure_storage_connection_string = '{azure_storage_connection_string}';")

bbox_filter = """
WHERE bbox.xmin > 4.73 AND bbox.xmax < 5.03
AND bbox.ymin > 52.28 AND bbox.ymax < 52.42
"""

def fetch_data(theme, type_name, output_file):
    query = f"""
    SELECT
        names.primary as name,
        height,
        level,
        ST_AsGeoJSON(ST_GeomFromWKB(geometry)) as geometry
    FROM read_parquet('azure://release/2024-05-16-beta.0/theme={theme}/type={type_name}/*', filename=true, hive_partitioning=1)
    {bbox_filter}
    """
    result = con.execute(query)
    rows = result.fetchall()
    with open(output_file, 'w') as f:
        f.write('{"type": "FeatureCollection", "features": [\n')
        first = True
        for row in rows:
            if not first:
                f.write(',\n')
            first = False
            f.write(row[3])  # Access the geometry field from the row
        f.write('\n]}')
    print(f'Data for {theme}/{type_name} written to {output_file}')

# Fetch and save data for buildings, transportation, and places
fetch_data('buildings', 'building', 'amsterdam_buildings.geojson')
fetch_data('transportation', 'road', 'amsterdam_transportation.geojson')
fetch_data('places', 'place', 'amsterdam_places.geojson')

con.close()
