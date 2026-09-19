import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.geolocation_service import GeolocationService, haversine_distance

def test_haversine_distance():
    dist = haversine_distance(12.9716, 77.5946, 12.9352, 77.6245)
    assert 4.0 <= dist <= 6.0

def test_geolocation_service():
    geo_service = GeolocationService()
    facilities = geo_service.get_nearby_facilities(user_lat=12.9716, user_lon=77.5946)
    
    assert len(facilities) > 0
    assert "distance_km" in facilities[0]
    assert "map_url" in facilities[0]
    
    for i in range(len(facilities) - 1):
        assert facilities[i]["distance_km"] <= facilities[i+1]["distance_km"]

if __name__ == "__main__":
    test_haversine_distance()
    test_geolocation_service()
    print("[SUCCESS] Geolocation facilities tests passed!")
