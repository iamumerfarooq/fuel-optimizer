from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from routing.services.location_service import get_location_coordinates
from routing.services.route_service import get_route
from routing.services.fuel_service import prepare_fuel_stations
from routing.services.station_service import find_stations_near_route
from routing.services.fuel_optimizer import (
    select_fuel_stops,
    calculate_fuel_cost,
)


@api_view(["POST"])
def calculate_route(request):
    """
    Calculate a driving route and optimal fuel stops.
    """

    try:
        start = request.data.get("start")
        finish = request.data.get("finish")

        if not start or not finish:
            return Response(
                {
                    "error": (
                        "Both start and finish locations "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_city = start.get("city")
        start_state = start.get("state")

        finish_city = finish.get("city")
        finish_state = finish.get("state")

        if not all(
            [
                start_city,
                start_state,
                finish_city,
                finish_state,
            ]
        ):
            return Response(
                {
                    "error": (
                        "Each location must include "
                        "city and state."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve city/state to coordinates.
        start_location = get_location_coordinates(
            start_city,
            start_state,
        )

        finish_location = get_location_coordinates(
            finish_city,
            finish_state,
        )

        # Get driving route from OSRM.
        route = get_route(
            start_location["latitude"],
            start_location["longitude"],
            finish_location["latitude"],
            finish_location["longitude"],
        )

        # Load fuel stations.
        stations = prepare_fuel_stations()

        # Find stations close to the route.
        candidates = find_stations_near_route(
            route["geometry"],
            route["distance_miles"],
            stations,
        )

        # Find globally cost-effective fuel stops.
        selected_stops = select_fuel_stops(
            route["distance_miles"],
            candidates,
        )

        # Calculate fuel cost.
        fuel_result = calculate_fuel_cost(
            route["distance_miles"],
            selected_stops,
        )

        return Response(
            {
                "start": start_location,
                "finish": finish_location,
                "route": {
                    "distance_miles": round(
                        route["distance_miles"],
                        2,
                    ),
                    "duration_minutes": round(
                        route["duration_minutes"],
                        2,
                    ),
                    "geometry": route["geometry"],
                },
                "fuel": {
                    "efficiency_mpg": 10,
                    "max_range_miles": 500,
                    "total_gallons_consumed": round(
                        route["distance_miles"] / 10,
                        2,
                    ),
                    "total_gallons_purchased": (
                        fuel_result[
                            "total_gallons_purchased"
                        ]
                    ),
                    "total_cost": fuel_result[
                        "total_cost"
                    ],
                    "stops": fuel_result["stops"],
                },
                "candidate_station_count": len(
                    candidates
                ),
            }
        )

    except ValueError as error:
        return Response(
            {
                "error": str(error),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as error:
        return Response(
            {
                "error": (
                    "An unexpected error occurred."
                ),
                "details": str(error),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )