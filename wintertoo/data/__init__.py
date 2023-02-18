"""
Central module for general data and telescope constants
"""
import json
from pathlib import Path

import astroplan
import astropy.coordinates as coords
import pandas as pd

data_dir = Path(__file__).parent.resolve()

summer_fields_path = data_dir.joinpath("summer_fields.txt")
summer_fields = pd.read_csv(summer_fields_path, sep=r"\s+")

SUMMER_FILTERS = ["u", "g", "r", "i"]
WINTER_FILTERS = ["Y", "J", "Hs"]

SUMMER_BASE_WIDTH = 0.26112
WINTER_BASE_WIDTH = 1.0

MAX_TARGET_PRIORITY = 100.0

PROGRAM_DB_HOST = "jagati.caltech.edu"

too_schedule_config_path = data_dir.joinpath("observing_request_schema.json")

with open(too_schedule_config_path, "rb") as f:
    too_db_schedule_config = json.load(f)


def get_default_value(key: str):
    """
    Get default value for a parameter.

    :param key: Key to check
    :return: default value
    """
    return too_db_schedule_config["properties"][key]["default"]


# define location of Palomar Observatory
PALOMAR_LOC = coords.EarthLocation(
    lat=coords.Latitude("33d21m25.5s"),
    lon=coords.Longitude("-116d51m58.4s"),
    height=1696.0,
)

palomar_observer = astroplan.Observer(location=PALOMAR_LOC)
