import duckdb
import requests
import json
import pandas as pd

# URL of the dataset
url = "https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?KAARTLAAG=LICHTPUNTEN&THEMA=lichtpunten"

# Fetch the dataset
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    data = None

# Initialize DuckDB and create a connection
con = duckdb.connect(database=':memory:')

# Load the dataset into DuckDB
if data:
    # Extract the properties and coordinates from the GeoJSON data
    records = []
    for feature in data["features"]:
        coordinates = feature["geometry"]["coordinates"]
        records.append({
            "longitude": coordinates[0],
            "latitude": coordinates[1]
        })

    # Convert records to a DataFrame
    df = pd.DataFrame(records)

    # Write the DataFrame to a CSV file
    df.to_csv('street_lights.csv', index=False)

    # Create a table in DuckDB and insert data from CSV
    con.execute("CREATE TABLE street_lights AS SELECT * FROM 'street_lights.csv'")

    # Filter the data for Amsterdam (latitude and longitude bounds)
    query = """
    SELECT * FROM street_lights 
    WHERE longitude BETWEEN 4.73 AND 5.03 
      AND latitude BETWEEN 52.28 AND 52.42
    """

    result = con.execute(query).df()

    # Save the filtered data to a GeoJSON file
    features = []
    for _, row in result.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            },
            "properties": {k: v for k, v in row.items() if k not in ["longitude", "latitude"]}
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open('amsterdam_street_lights.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)

    print('Street light data written to amsterdam_street_lights.geojson')
else:
    print("No data to process")

# Close the connection
con.close()
