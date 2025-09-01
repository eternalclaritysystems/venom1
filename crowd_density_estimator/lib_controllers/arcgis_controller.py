# controllers/arcgis_controller.py

from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
from arcgis.geoenrichment import Country
from arcgis.geometry import Point
import pandas as pd

gis = GIS()  # anonymous for public layers

def search_feature_layer(query, item_type="Feature Layer", outside_org=True):
    results = gis.content.search(query, item_type, outside_org=outside_org, max_items=1)
    return results[0] if results else None

def fetch_layer_attributes(layer_name, bbox=None):
    item = search_feature_layer(layer_name)
    if not item:
        return []
    layer = FeatureLayerCollection(item).layers[0]
    if bbox:
        query = layer.query(geometry_filter={
            'xmin': bbox[0], 'ymin': bbox[1],
            'xmax': bbox[2], 'ymax': bbox[3],
            'spatialReference': {'wkid': 4326}
        }, out_fields="*")
    else:
        query = layer.query(out_fields="*")
    return [f.attributes for f in query.features]

def fetch_demographics(address_or_point=None):
    country = Country("usa", gis=gis)
    vars = [
        "populationtotals.totpop_cy",
        "householdtotals.tothh_cy",
        "householdincome.medhinc_cy"
    ]
    study_areas = [address_or_point] if isinstance(address_or_point, Point) else ["New York, NY"]
    enrich_df = country.enrich(
        study_areas=study_areas,
        enrich_variables=vars,
        return_geometry=False
    )
    return enrich_df.to_dict(orient="records")

def fetch_combined_data():
    combined = {}

    # Permits / Events
    combined["permits_and_events"] = fetch_layer_attributes("special event permits")

    # Demographics
    combined["demographics"] = fetch_demographics()

    # Traffic (optional bbox example for NYC)
    sample_bbox = (-74.03, 40.70, -73.90, 40.80)
    combined["traffic"] = fetch_layer_attributes("Live Traffic", sample_bbox)

    # POIs / Land Use
    combined["points_of_interest"] = fetch_layer_attributes("Land Use")

    # Weather / Hazards
    combined["weather_hazards"] = fetch_layer_attributes("NOAA Hazards")

    return combined

if __name__ == "__main__":
    import json
    data = fetch_combined_data()
    print(json.dumps(data, indent=2))
