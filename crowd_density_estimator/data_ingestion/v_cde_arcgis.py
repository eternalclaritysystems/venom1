import os
import yaml
from arcgis.gis import GIS
from arcgis.geoenrichment import Country

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

ESRI_API_KEY = config["esri_token"].strip()
gis = GIS(api_key=ESRI_API_KEY)

def ingest_data(study_area="New York, NY"):
    print("[+] Fetching ArcGIS data...")
    try:
        country = Country("usa", gis=gis)
        vars = [
            "populationtotals.totpop_cy",
            "householdtotals.tothh_cy",
            "householdincome.medhinc_cy"
        ]
        enrich_df = country.enrich(
            study_areas=[study_area],
            enrich_variables=vars,
            return_geometry=False
        )
        print("[+] ArcGIS demographic data received.")
        return enrich_df
    except Exception as e:
        print(f"[!] ArcGIS error: {e}")
        return {}

if __name__ == "__main__":
    data = ingest_data()
    print(data.head() if not data.empty else data)
