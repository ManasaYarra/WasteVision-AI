import os
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth 
    in kilometers using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 2)

class GeolocationService:
    """Service to load waste collection facilities and perform location-based searching."""

    def __init__(self, facilities_path=None):
        if facilities_path is None:
            facilities_path = BASE_DIR / "data" / "facilities.json"
        
        self.facilities_path = Path(facilities_path)
        self.facilities = self._load_facilities()

    def _load_facilities(self):
        """Load facility JSON dataset."""
        try:
            if self.facilities_path.exists():
                with open(self.facilities_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading facilities.json: {e}")
        return []

    def get_nearby_facilities(self, user_lat=12.9716, user_lon=77.5946, category_filter=None, max_distance_km=50.0):
        """
        Calculate distance from user location to each facility and filter by category/distance.
        Returns list of facilities sorted by distance.
        """
        results = []
        for fac in self.facilities:
            fac_lat = fac.get("latitude")
            fac_lon = fac.get("longitude")

            if fac_lat is not None and fac_lon is not None:
                dist = haversine_distance(user_lat, user_lon, fac_lat, fac_lon)
            else:
                dist = 0.0

            # Filter by category if requested
            if category_filter and category_filter != "All":
                accepted = fac.get("categories", [])
                if category_filter not in accepted and "All Categories Accepted (Segregated Lanes)" not in fac.get("accepted_items", []):
                    continue

            fac_item = dict(fac)
            fac_item["distance_km"] = dist
            fac_item["map_url"] = f"https://www.google.com/maps/search/?api=1&query={fac_lat},{fac_lon}"
            results.append(fac_item)

        results.sort(key=lambda x: x["distance_km"])
        return results
