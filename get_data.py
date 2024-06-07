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

query = """
SELECT
    names.primary as name,
    height,
    level,
    ST_AsGeoJSON(ST_GeomFromWKB(geometry)) as geometry
FROM read_parquet('azure://release/2024-05-16-beta.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
WHERE bbox.xmin > -122.68 AND bbox.xmax < -121.98
AND bbox.ymin > 47.36 AND bbox.ymax < 47.79
"""

result = con.execute(query)
rows = result.fetchall()
with open('seattle_buildings.geojson', 'w') as f:
    f.write('{"type": "FeatureCollection", "features": [\n')
    first = True
    for row in rows:
        if not first:
            f.write(',\n')
        first = False
        f.write(row['geometry'].as_py())
    f.write('\n]}')

con.close()