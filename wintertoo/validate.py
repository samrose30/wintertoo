import logging

import astropy.time
import numpy as np
import pandas as pd
import json
from astropy import units as u
from astropy.time import Time
from jsonschema import validate, ValidationError
from wintertoo.data import too_db_schedule_config, summer_filters, max_target_priority
from wintertoo.utils import get_program_details, get_tonight, up_tonight

logger = logging.getLogger(__name__)


class RequestValidationError(Exception):
    pass


def validate_schedule_json(
    data: dict
):
    try:
        validate(data, schema=too_db_schedule_config)
        logger.info("Successfully validated schema")
    except ValidationError as e:
        logger.error("Error with JSON schema validation, input data not formatted correctly.")
        logger.error(e)
        raise RequestValidationError(e)


def validate_schedule_df(
    df: pd.DataFrame
):
    for _, row in df.iterrows():
        json.loads(row.to_json())
        validate_schedule_json(json.loads(row.to_json()))

def validate_target_visibility(
        schedule: pd.DataFrame
):
    for _, row in schedule.iterrows():

        ra = row["fieldRA"] * u.radian
        dec = row["fieldDec"] * u.radian

        for time_mjd in [row["validStart"], row["validStop"]]:
            t = Time(time_mjd, format="mjd")

            is_up, _ = up_tonight(time=t, ra=ra, dec=dec)

            if not is_up:
                err = f"The following target is not visible on requested date {t}: \n" \
                      f" {row}"
                logger.error(err)
                raise RequestValidationError(err)


def calculate_overall_priority(
        target_priority: float,
        program_base_priority: float
):
    return target_priority + program_base_priority

def validate_target_priority(
        schedule: pd.DataFrame,
        program_base_priority: float
):
    max_priority = calculate_overall_priority(
        target_priority=max_target_priority,
        program_base_priority=program_base_priority
    )

    for _, row in schedule.iterrows():
        target_priority = row["priority"]

        if target_priority > max_priority:
            err = f"Target priority ({target_priority} exceeds maximum allowed value of {target_priority}." \
                  f"The maximum is the sum of the overall max target priority ({max_target_priority}) " \
                  f"and the program priority ({program_base_priority})."
            logger.error(err)
            raise RequestValidationError(err)


def validate_filter(
        filter_name: str
):
    assert filter_name in summer_filters


def validate_target_pi(
        schedule: pd.DataFrame,
        prog_pi: str
):
    for _, row in schedule.iterrows():
        pi = row["pi"]
        if pi != prog_pi:
            err = f"Pi '{pi}' does not match PI for program {program_name}"
            logger.error(err)
            raise RequestValidationError(err)


def validate_target_dates(
        schedule: pd.DataFrame,
        program_start_date: astropy.time.Time,
        program_end_date: astropy.time.Time
):

    for _, row in schedule.iterrows():

        start_time = row["validStart"]
        stop_time = row["validStop"]

        err = None

        if start_time > stop_time:
            err = f"Start time '{start_time}' is after stop time '{stop_time}'."

        elif start_time < program_start_date:
            err = f"Start time '{start_time}' is before program start date '{stop_time}'"

        elif stop_time > program_end_date:
            err = f"Stop time '{start_time}' is after program end date '{stop_time}'"

        if err is not None:
            logger.error(err)
            RequestValidationError(err)


def validate_schedule_request(
        schedule_request: pd.DataFrame,
        program_name: str,
):
    validate_schedule_df(schedule_request)

    validate_target_visibility(schedule_request)

    # Check request using program info

    programs_query_results = get_program_details(program_name)
    program_details = programs_query_results[0]

    program_pi = programs_query_results[0][2]
    program_start_date = programs_query_results[0][3]
    program_end_date = programs_query_results[0][4]
    program_base_priority = programs_query_results[0][6]


    validate_target_pi(
        schedule_request,
        program_pi=program_pi
    )
    validate_target_dates(
        schedule_request,
        program_start_date=program_start_date,
        program_end_date=program_end_date
    )
    validate_target_priority(
        schedule_request,
        program_base_priority=program_base_priority
    )

