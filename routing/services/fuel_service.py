from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

FUEL_DATA_PATH = BASE_DIR / "routing" / "data" / "fuel-prices-for-be-assessment.csv"
PLACES_DATA_PATH = BASE_DIR / "routing" / "data" / "us_places" / "2025_Gaz_place_national.txt"


def load_fuel_data():
    fuel_df = pd.read_csv(FUEL_DATA_PATH)

    places_df = pd.read_csv(
        PLACES_DATA_PATH,
        sep="|",
        usecols=["USPS", "NAME", "INTPTLAT", "INTPTLONG"],
    )

    return fuel_df, places_df

def prepare_fuel_stations():
    fuel_df, places_df = load_fuel_data()

    # Clean the city and state values so they can be matched reliably.
    fuel_df["City"] = fuel_df["City"].str.strip()
    fuel_df["State"] = fuel_df["State"].str.strip()

    places_df["NAME"] = (
        places_df["NAME"]
        .str.replace(
            r"\s+(city|town|village|borough|CDP)$",
            "",
            regex=True,
            case=False,
        )
        .str.strip()
    )

    places_df["USPS"] = places_df["USPS"].str.strip()

    # Keep only the information needed to locate a fuel station.
    places_df = places_df[
        ["USPS", "NAME", "INTPTLAT", "INTPTLONG"]
    ].drop_duplicates(
        subset=["USPS", "NAME"]
    )

    # Match fuel stations with their city/state coordinates.
    stations = fuel_df.merge(
        places_df,
        left_on=["State", "City"],
        right_on=["USPS", "NAME"],
        how="left",
    )

    stations = stations.rename(
        columns={
            "INTPTLAT": "latitude",
            "INTPTLONG": "longitude",
            "Retail Price": "price",
        }
    )
    # We can only use stations that have valid coordinates.
    stations = stations.dropna(
        subset=["latitude", "longitude"]
    ).copy()
    return stations