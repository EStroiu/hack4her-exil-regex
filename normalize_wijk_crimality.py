# This script normalizes the criminality scores in amsterdam wijken geojson and creates a new output file

import pandas as pd
import json

unnormalized_input = "amsterdam_wijken.geojson"
normalized_output = "amsterdam_wijken_normalized.geojson"
csv_file = 'criminaliteit-wijken-2023-3.csv'

def get_min_max():
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Extract the column
    column_name = 'waarde'
    column_data = df[column_name]

    # Find the minimum and maximum values
    return [column_data.min(), column_data.max()]

def normalize_score(score, min_value, max_value):
    return (score - min_value) / (max_value - min_value)

def normalize_criminality_scores():
    # Load the existing GeoJSON file
    with open(unnormalized_input, 'r') as f:
        geojson_data = json.load(f)
    
    min_value, max_value = get_min_max()

    # Update the GeoJSON properties with normalized scores
    for feature in geojson_data['features']:
        score = feature['properties'].get('CriminalityScore')
        if score is not None:
            normalized_score = normalize_score(score, min_value, max_value)
            feature['properties']['CriminalityScore'] = normalized_score

    # Save the new GeoJSON file with normalized scores
    with open(normalized_output, 'w') as f:
        json.dump(geojson_data, f, indent=2)

    print("Normalized criminality scores added to GeoJSON and saved to 'normalized_raw_file.geojson'")

normalize_criminality_scores()