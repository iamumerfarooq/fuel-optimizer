MAX_RANGE_MILES = 500
FUEL_EFFICIENCY_MPG = 10


def select_fuel_stops(route_distance_miles, stations):
    """
    Find the minimum-cost sequence of fuel stops.

    Assumptions:
    - Vehicle starts with a full 500-mile tank.
    - Vehicle gets 10 MPG.
    - Every leg between selected stops must be <= 500 miles.
    """

    points = stations.copy()

    # Sort stations by their position along the route.
    points = points.sort_values(
        "route_distance_miles"
    ).reset_index(drop=True)

    # Create route nodes.
    # Node 0 = starting location
    # Middle nodes = fuel stations
    # Last node = destination
    nodes = [
        {
            "position": 0.0,
            "price": None,
            "station": None,
        }
    ]

    for _, station in points.iterrows():

        station_position = float(
            station["route_distance_miles"]
        )

        # Ignore stations beyond the destination.
        if station_position >= route_distance_miles:
            continue

        nodes.append(
            {
                "position": station_position,
                "price": float(station["price"]),
                "station": station,
            }
        )

    destination_index = len(nodes)

    nodes.append(
        {
            "position": float(route_distance_miles),
            "price": None,
            "station": None,
        }
    )

    # dp[i] = minimum fuel cost required to reach node i.
    dp = [float("inf")] * len(nodes)

    # Vehicle starts with a full tank.
    # Therefore no fuel cost is charged at the starting point.
    dp[0] = 0.0

    # Used later to reconstruct the cheapest route.
    previous = [None] * len(nodes)

    # Find the minimum-cost path.
    for i in range(len(nodes)):

        if dp[i] == float("inf"):
            continue

        current_position = nodes[i]["position"]

        for j in range(i + 1, len(nodes)):

            next_position = nodes[j]["position"]

            distance = (
                next_position - current_position
            )

            # Vehicle cannot travel more than 500 miles
            # between fuel stops.
            if distance > MAX_RANGE_MILES:
                break

            # Starting tank is already full.
            if i == 0:

                fuel_cost = 0.0

            else:

                gallons = (
                    distance / FUEL_EFFICIENCY_MPG
                )

                fuel_cost = (
                    gallons * nodes[i]["price"]
                )

            new_cost = dp[i] + fuel_cost

            if new_cost < dp[j]:

                dp[j] = new_cost
                previous[j] = i

    # Check whether the destination can be reached.
    if dp[destination_index] == float("inf"):

        raise ValueError(
            "No valid fuel-stop route exists within "
            "the vehicle's 500-mile range."
        )

    # Reconstruct the cheapest route.
    path = []

    current = destination_index

    while current is not None:

        path.append(current)

        current = previous[current]

    path.reverse()

    # Extract only fuel stations.
    # The starting point and destination are excluded.
    selected_stops = []

    for index in path:

        station = nodes[index]["station"]

        if station is not None:

            selected_stops.append(station)

    return selected_stops


def calculate_fuel_cost(
    route_distance_miles,
    selected_stops,
):
    """
    Calculate fuel purchased and total fuel cost.

    Assumptions:
    - Vehicle starts with a full 500-mile tank.
    - Vehicle gets 10 MPG.
    - Fuel is purchased at selected fuel stations.
    """

    total_cost = 0.0
    total_gallons = 0.0

    stop_details = []

    for index, stop in enumerate(selected_stops):

        stop_position = float(
            stop["route_distance_miles"]
        )

        # Determine the next point on the route.
        if index + 1 < len(selected_stops):

            next_position = float(
                selected_stops[index + 1][
                    "route_distance_miles"
                ]
            )

        else:

            # Last fuel stop -> destination.
            next_position = route_distance_miles

        # Distance from this fuel station
        # to the next station/destination.
        distance = (
            next_position - stop_position
        )

        # Fuel required for that distance.
        gallons = (
            distance / FUEL_EFFICIENCY_MPG
        )

        price = float(stop["price"])

        cost = gallons * price

        total_gallons += gallons
        total_cost += cost

        stop_details.append(
            {
                "station": stop["Truckstop Name"],
                "city": stop["City"],
                "state": stop["State"],
                "price_per_gallon": round(
                    price,
                    3,
                ),
                "distance_to_next_stop_miles": round(
                    distance,
                    2,
                ),
                "gallons": round(
                    gallons,
                    2,
                ),
                "cost": round(
                    cost,
                    2,
                ),
                "latitude": float(
                    stop["latitude"]
                ),
                "longitude": float(
                    stop["longitude"]
                ),
            }
        )

    return {
        "total_gallons_purchased": round(
            total_gallons,
            2,
        ),
        "total_cost": round(
            total_cost,
            2,
        ),
        "stops": stop_details,
    }