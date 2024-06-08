# This script outputs a geojson file containing the amsterdam wijken with their corresponding criminality scores.

import json
import pandas as pd

raw_wijken_geojson = 'amsterdam_wijken_raw.geojson'
criminality_csv = 'criminaliteit-wijken-2023-3.csv'
output_geojson = 'amsterdam_wijken.geojson'

# Load the GeoJSON file
with open(raw_wijken_geojson, 'r') as f:
    geojson_data = json.load(f)

# Load the CSV file
csv_data = pd.read_csv(criminality_csv)

# Manual pain
criminal_scores = {
    "Reigersbos" : 186,
    "Amstel III/Bullewijk" : 186,
    "Tuindorp Buiksloot" : 66,
    "De Aker" : 65,
    "Sloterdijk Nieuw-West" : 111, # assumption : Sloterdijk Nieuw-West == Landlust / Sloterdijk-West
    "Oostzanerwerf" : 109,
    "Prinses Irenebuurt e.o." : 133,
    "Geerdinkhof/Kantershof" : 61,
    "Bloemendalerpolder" : 25,
    "Nieuwendammerdijk/Buiksloterdijk" : 66,
    "Frederik Hendrikbuurt" : 106,
    "Nieuwmarkt/Lastage" : 180,
    "Zeeburgereiland/Bovendiep" : 143,
    "Lutkemeer/Ookmeer" : 65,
    "Tuindorp Nieuwendam" : 66,
    "IJburg-Oost" : 54,
    "Landlust" : 111,
    "Weesperbuurt/Plantage" : 119,
    "Houthavens" : 130,
    "Havens-West" : 130, # assumption : encompassed in Spaarndammerbuurt / Zeeheldenbuurt / Houthavens
    "Weesp Binnenstad/Zuid" : 59,
    "Helmersbuurt" : 148,
    "Centrale Markt" : 106,
    "Kadoelen" : 109,
    "IJburg-Zuid" : 54,
    "Noordelijke IJ-oevers-Oost" : 138,
    "Oostelijke Eilanden/Kadijken" : 95,
    "Coenhaven/Minervahaven" : 130, # it seems that Houthavens (in csv) includes these two regions?
    "Sloten/Nieuw-Sloten" : 70,
    "Vondelparkbuurt" : 148,
    "Sloterdijk-West" : 111,
    "Zuidas" : 133,
    "IJplein/Vogelbuurt" : 138,
    "Aetsveld/Oostelijke Vechtoever" : 54,
    "Omval/Overamstel" : 126,
    "Spaarndammerbuurt/Zeeheldenbuurt" : 130
    }


# Function to find the criminality score for a given neighborhood
def get_criminality_score(wijk_name):
    wijk_name = wijk_name.replace(' / ', '/').replace(' /', '/').replace('/ ', '/')
    row = csv_data[csv_data['naam'] == wijk_name]
    if not row.empty:
        return int(row['waarde'].values[0])
    elif wijk_name in criminal_scores:
        return criminal_scores[wijk_name]

    print("Not found : ", wijk_name)
    return None

# Add the criminality score to the GeoJSON properties
for feature in geojson_data['features']:
    wijk_name = feature['properties']['Wijk']
    criminality_score = get_criminality_score(wijk_name)
    feature['properties']['CriminalityScore'] = criminality_score

# Save the updated GeoJSON to a new file
with open(output_geojson, 'w') as f:
    json.dump(geojson_data, f, indent=2)

print(f"Criminality scores added to GeoJSON and saved to '{output_geojson}'")
