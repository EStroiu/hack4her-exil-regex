# import duckdb
# import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# con = duckdb.connect()

# con.execute("INSTALL spatial;")
# con.execute("LOAD spatial;")

# con.execute("CREATE OR REPLACE SCHEMA spatial;")
# con.execute("CREATE OR REPLACE SCHEMA azure;")
# con.execute("SET azure_transport_option_type = 'curl';")

# azure_storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=overturemapswestus2;AccountKey=;EndpointSuffix=core.windows.net'
# con.execute(f"SET azure_storage_connection_string = '{azure_storage_connection_string}';")

# query = """
# SELECT
#     names.primary as name,
#     height,
#     level,
#     ST_AsGeoJSON(ST_GeomFromWKB(geometry)) as geometry
# FROM read_parquet('azure://release/2024-05-16-beta.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
# WHERE bbox.xmin > 4.73 AND bbox.xmax < 5.03
# AND bbox.ymin > 52.28 AND bbox.ymax < 52.42
# """

# result = con.execute(query)
# rows = result.fetchall()
# with open('amsterdam_buildings.geojson', 'w') as f:
#     f.write('{"type": "FeatureCollection", "features": [\n')
#     first = True
#     for row in rows:
#         if not first:
#             f.write(',\n')
#         first = False
#         f.write(row[3])  # Access the geometry field from the row
#     f.write('\n]}')

# con.close()
import duckdb
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Connect to DuckDB
con = duckdb.connect()

# Install and load necessary extensions
con.execute("INSTALL spatial;")
con.execute("LOAD spatial;")

# Set up schemas and connection strings
con.execute("CREATE OR REPLACE SCHEMA spatial;")
con.execute("CREATE OR REPLACE SCHEMA azure;")
con.execute("SET azure_transport_option_type = 'curl';")

azure_storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=overturemapswestus2;AccountKey=;EndpointSuffix=core.windows.net'
con.execute(f"SET azure_storage_connection_string = '{azure_storage_connection_string}';")

# Define bounding box for Amsterdam
bbox_filter = """
WHERE bbox.xmin > 4.73 AND bbox.xmax < 5.03
AND bbox.ymin > 52.28 AND bbox.ymax < 52.42
"""

# Function to fetch and save buildings data
def fetch_buildings():
    query = f"""
    SELECT
        names.primary as name,
        height,
        level,
        ST_AsGeoJSON(ST_GeomFromWKB(geometry)) as geometry
    FROM read_parquet('azure://release/2024-05-16-beta.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
    {bbox_filter}
    """
    result = con.execute(query)
    rows = result.fetchall()
    with open('amsterdam_buildings.geojson', 'w') as f:
        f.write('{"type": "FeatureCollection", "features": [\n')
        first = True
        for row in rows:
            if not first:
                f.write(',\n')
            first = False
            f.write(row[3])  # Access the geometry field from the row
        f.write('\n]}')
    print('Buildings data written to amsterdam_buildings.geojson')

def fetch_transportation():
    query = f"""
    SELECT
        names.primary AS name,
        JSON_EXTRACT_STRING(road, '$.class') AS class,
        ST_AsGeoJSON(ST_GeomFromWKB(geometry)) as geometry
    FROM read_parquet('azure://release/2024-05-16-beta.0/theme=transportation/type=segment/*', filename=true, hive_partitioning=1)
    WHERE
        subtype = 'road'
        AND bbox.xmin > 4.73 AND bbox.xmax < 5.03
        AND bbox.ymin > 52.28 AND bbox.ymax < 52.42
    """
    result = con.execute(query)
    rows = result.fetchall()
    # Debugging: print the fetched rows
    print("Fetched transportation rows:", rows)
    with open('amsterdam_transportation.geojson', 'w') as f:
        f.write('{"type": "FeatureCollection", "features": [\n')
        first = True
        for row in rows:
            if not first:
                f.write(',\n')
            first = False
            f.write(row[2])  # Access the geometry field from the row
        f.write('\n]}')
    print('Transportation data written to amsterdam_transportation.geojson')

# Function to fetch and save places data
def fetch_places():
    query = f"""
    SELECT
        names.primary AS name,
        categories.main as category,
        ROUND(confidence,2) as confidence,
        ST_AsGeoJSON(ST_GeomFromWKB(geometry)) as geometry
    FROM read_parquet('azure://release/2024-05-16-beta.0/theme=places/*/*', filename=true, hive_partitioning=1)
    WHERE
        bbox.xmin BETWEEN 4.73 AND 5.03 AND
        bbox.ymin BETWEEN 52.28 AND 52.42
    """
    result = con.execute(query)
    rows = result.fetchall()
    with open('amsterdam_places.geojson', 'w') as f:
        f.write('{"type": "FeatureCollection", "features": [\n')
        first = True
        for row in rows:
            if not first:
                f.write(',\n')
            first = False
            f.write(row[3])  # Access the geometry field from the row
        f.write('\n]}')
    print('Places data written to amsterdam_places.geojson')

# Fetch and save data for buildings, transportation, and places
fetch_buildings()
fetch_transportation()
fetch_places()

# Close the connection
con.close()
