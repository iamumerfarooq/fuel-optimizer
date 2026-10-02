import math

from shapely.geometry import LineString, Point


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographic coordinates in miles.
    """

    earth_radius_miles = 3958.8

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_miles * c


def build_route_distances(route_coordinates):
    """
    Calculate cumulative mileage for every point in the route.
    """

    distances = [0.0]

    for i in range(1, len(route_coordinates)):
        lon1, lat1 = route_coordinates[i - 1]
        lon2, lat2 = route_coordinates[i]

        segment_distance = haversine_distance(
            lat1,
            lon1,
            lat2,
            lon2,
        )

        distances.append(
            distances[-1] + segment_distance
        )

    return distances


def find_stations_near_route(
    route_geometry,
    route_distance_miles,
    stations,
    max_distance_miles=10,
):
    """
    Find fuel stations near the route and calculate their
    approximate position in miles from the start.
    """

    route_coordinates = route_geometry["coordinates"]

    route_line = LineString(route_coordinates)

    # Approximate conversion for identifying nearby stations.
    max_distance_degrees = max_distance_miles / 69

    # Calculate the cumulative physical distance along the route.
    cumulative_distances = build_route_distances(
        route_coordinates
    )

    total_calculated_distance = cumulative_distances[-1]

    candidates = []

    for _, station in stations.iterrows():

        point = Point(
            station["longitude"],
            station["latitude"],
        )

        distance_from_route = route_line.distance(point)

        if distance_from_route <= max_distance_degrees:

            # Find the closest point on the route.
            projected_distance = route_line.project(point)

            # Convert that geometric position into a fraction.
            route_fraction = (
                projected_distance / route_line.length
                if route_line.length > 0
                else 0
            )

            # Convert fraction into actual miles.
            route_distance = (
                route_fraction * total_calculated_distance
            )

            station_data = station.copy()

            station_data["route_fraction"] = route_fraction
            station_data["route_distance_miles"] = route_distance

            candidates.append(station_data)

    if not candidates:
        return stations.iloc[0:0].copy()

    candidates_df = (
        __import__("pandas")
        .DataFrame(candidates)
        .sort_values("route_distance_miles")
        .reset_index(drop=True)
    )

    return candidates_df