from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

PLACES_DATA_PATH = (
    BASE_DIR
    / "routing"
    / "data"
    / "us_places"
    / "2025_Gaz_place_national.txt"
)


def load_places():
    """
    Load US city/place coordinates from the Census dataset.
    """

    return pd.read_csv(
        PLACES_DATA_PATH,
        sep="|",
        usecols=[
            "USPS",
            "NAME",
            "INTPTLAT",
            "INTPTLONG",
        ],
    )


def normalize_city_name(city):
    """
    Normalize city names so matching is more reliable.
    """

    return (
        city.strip()
        .lower()
    )


def get_location_coordinates(city, state):
    """
    Find latitude and longitude for a US city and state.
    """

    places = load_places()

    city_normalized = normalize_city_name(city)
    state_normalized = state.strip().upper()

    places["NAME_NORMALIZED"] = (
        places["NAME"]
        .str.replace(
            r"\s+(city|town|village|borough|CDP)$",
            "",
            regex=True,
            case=False,
        )
        .str.strip()
        .str.lower()
    )

    match = places[
        (places["USPS"].str.upper() == state_normalized)
        & (
            places["NAME_NORMALIZED"]
            == city_normalized
        )
    ]

    if match.empty:
        raise ValueError(
            f"Location not found: {city}, {state}"
        )

    location = match.iloc[0]

    return {
        "city": city,
        "state": state_normalized,
        "latitude": float(location["INTPTLAT"]),
        "longitude": float(location["INTPTLONG"]),
    }