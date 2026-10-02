import requests


OSRM_BASE_URL = "https://router.project-osrm.org/route/v1/driving"


def get_route(start_lat, start_lon, end_lat, end_lon):
    """
    Get a driving route between two coordinates using OSRM.
    """

    coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"

    url = f"{OSRM_BASE_URL}/{coordinates}"

    params = {
        "overview": "full",
        "geometries": "geojson",
    }

    response = requests.get(url, params=params, timeout=30)

    response.raise_for_status()

    data = response.json()

    if data["code"] != "Ok":
        raise ValueError("No route could be found between the locations.")

    route = data["routes"][0]

    return {
        "distance_miles": route["distance"] / 1609.344,
        "duration_minutes": route["duration"] / 60,
        "geometry": route["geometry"],
    }