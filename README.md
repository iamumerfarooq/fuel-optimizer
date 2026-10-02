# Fuel Route Optimization API

A Django REST API that calculates a driving route between two US locations and identifies cost-effective fuel stops along the route based on provided fuel-price data.

## Features

* Accepts start and finish locations within the USA
* Converts city/state locations into coordinates
* Calculates a driving route using a free routing API
* Identifies fuel stations located near the route
* Considers the vehicle's maximum range of 500 miles
* Assumes fuel efficiency of 10 miles per gallon
* Selects fuel stops based on fuel prices and vehicle range
* Calculates estimated fuel purchased and total fuel cost
* Returns route geometry that can be used to display the route on a map
* Validates missing or invalid locations
* Minimizes calls to the external routing service by calculating the route once per request

## Technology Stack

* Python 3
* Django 5.2
* Django REST Framework
* Pandas
* Shapely
* Requests
* OpenStreetMap / OSRM routing service

## Project Structure

```text
backend-fuel-assessment/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── routing/
│   ├── data/
│   │   ├── fuel-prices-for-be-assessment.csv
│   │   └── us_places/
│   │       └── 2025_Gaz_place_national.txt
│   │
│   ├── services/
│   │   ├── fuel_service.py
│   │   ├── route_service.py
│   │   ├── station_service.py
│   │   └── fuel_optimizer.py
│   │
│   └── ...
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd backend-fuel-assessment
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

Start the Django development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Usage

The API accepts a start and finish location within the USA.

Example:

```text
POST /api/route/
```

Example request:

```json
{
    "start": {
        "city": "Los Angeles",
        "state": "CA"
    },
    "finish": {
        "city": "New York",
        "state": "NY"
    }
}
```

The exact API endpoint can be verified from the project's URL configuration.

## Response

The API returns:

* Resolved start location
* Resolved finish location
* Route distance
* Route duration
* Route geometry
* Fuel efficiency
* Maximum vehicle range
* Total fuel consumed
* Total fuel purchased
* Total fuel cost
* Recommended fuel stops
* Number of candidate fuel stations

Example response structure:

```json
{
    "start": {
        "city": "Los Angeles",
        "state": "CA",
        "latitude": 34.019394,
        "longitude": -118.410825
    },
    "finish": {
        "city": "New York",
        "state": "NY",
        "latitude": 40.662712,
        "longitude": -73.938677
    },
    "route": {
        "distance_miles": 2810.7,
        "duration_minutes": 3023.28,
        "geometry": {
            "type": "LineString",
            "coordinates": []
        }
    },
    "fuel": {
        "efficiency_mpg": 10,
        "max_range_miles": 500,
        "total_gallons_consumed": 281.07,
        "total_gallons_purchased": 235.53,
        "total_cost": 715.90,
        "stops": []
    },
    "candidate_station_count": 544
}
```

The route geometry contains the coordinates returned by the routing service and can be used by a frontend mapping application to draw the route.

## Fuel Calculation

The assessment specifies:

* Maximum vehicle range: 500 miles
* Fuel efficiency: 10 MPG

Therefore:

```text
Fuel consumed = distance / 10
```

For example, a 400-mile leg requires:

```text
400 / 10 = 40 gallons
```

The fuel cost is calculated as:

```text
Fuel cost = gallons purchased × price per gallon
```

The vehicle is assumed to start with a full tank, so fuel required before the first selected fuel stop is not charged as a purchase.

## Fuel Stop Optimization

The application:

1. Finds fuel stations located close to the calculated route.
2. Determines each station's position along the route.
3. Sorts stations by route position.
4. Considers only stations that can be reached within the vehicle's maximum range.
5. Calculates the fuel cost required between stops.
6. Uses a dynamic-programming approach to find a minimum-cost sequence of reachable fuel stops.
7. Reconstructs the selected sequence of stations.
8. Calculates the total fuel purchased and total cost.

Each selected stop also includes:

* Station name
* City
* State
* Fuel price
* Distance to the next stop
* Gallons purchased
* Estimated cost
* Latitude
* Longitude

## External Routing Service

The application uses the free OSRM routing service with OpenStreetMap data to calculate the driving route.

The route API is called once for each assessment request, after the start and finish locations have been resolved.

Fuel station selection is performed locally using the supplied CSV data, reducing unnecessary external API calls.

## Input Validation

The API returns a `400 Bad Request` when:

* The start location is missing
* The finish location is missing
* A requested city cannot be found
* A valid route or fuel-stop sequence cannot be determined

## Testing

The following scenarios were tested:

1. New York → Washington, DC → 200 OK
2. Seattle → Miami → 200 OK
3. Missing finish location → 400 Bad Request
4. Invalid city → 400 Bad Request

A longer route such as Los Angeles → New York was also tested to verify multiple fuel stops.

## Notes

The provided fuel-price CSV is used as the source of fuel prices.

The Census Gazetteer place data is used to resolve US city/state names to geographic coordinates.

The routing service provides the driving route and route geometry.

The project is designed as an assessment implementation and uses the assumptions specified in the assessment.
