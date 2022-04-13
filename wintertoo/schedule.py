import pandas as pd
import os
from astropy.time import Time
from astropy import units as u
import logging
from wintertoo.data import summer_filters, too_schedule_config
from wintertoo.make_request import make_too_request_from_df
from wintertoo.fields import get_best_summer_field

logger = logging.getLogger(__name__)


def to_date_string(
        time: Time
):
    return time.isot.split("T")[0]


def build_schedule(
        ra_degs: list,
        dec_degs: list,
        prog_id: str,
        pi: str,
        filters: list = None,
        texp: float = 300,
        nexp: int = 1,
        dither_bool: bool = True,
        dither_distance="",
        maximum_airmass: float = 1.5,
        maximum_seeing: float = 3.0,
        nights: list = None,
        t_0: Time = None,
        csv_save_file: str = None,
):

    if nights is None:
        nights = list([1, 2, 3])
    if filters is None:
        filters = summer_filters
    if t_0 is None:
        t_0 = Time.now()

    schedule = pd.DataFrame()

    for night in nights:
        start_date = to_date_string(t_0 + (night-1)*u.day)
        end_date = to_date_string(t_0 + (night*u.day))

        for i, ra_deg in enumerate(ra_degs):
            dec_deg = dec_degs[i]

            for f in filters:
                schedule = schedule.append({
                    "RA_deg": ra_deg,
                    "Dec_deg": dec_deg,
                    "Filter": f,
                    "Texp": texp,
                    "Nexp": nexp,
                    "Dither?": ["n", "y"][dither_bool],
                    "Dither distance": dither_distance,
                    "PI": pi,
                    "propID": prog_id,
                    "Earliest UT Date": start_date,
                    "UT Start Time": "00:00:00.02",
                    "Latest UT Date": end_date,
                    "UT Finish Time": "00:00:00.01",
                    "Maximum Airmass": maximum_airmass,
                    "Maximum Seeing": maximum_seeing
                }, ignore_index=True)

    schedule = schedule.astype({"Nexp": int})

    if csv_save_file is not None:
        logger.info(f"Saving schedule to {csv_save_file}")
        schedule.to_csv(csv_save_file, index=False)
    return schedule


def make_schedule(
        schedule_name,
        ra_degs: list,
        dec_degs: list,
        prog_id: str,
        pi: str,
        filters: list = None,
        texp: float = 300,
        nexp: int = 1,
        dither_bool: bool = True,
        dither_distance="",
        maximum_airmass: float = 1.5,
        maximum_seeing: float = 3.0,
        nights: list = None,
        t_0: Time = None,
        csv_save_file: str = None,
        submit: bool = False
):
    schedule = build_schedule(
        ra_degs=ra_degs,
        dec_degs=dec_degs,
        prog_id=prog_id,
        pi=pi,
        filters=filters,
        texp=texp,
        nexp=nexp,
        dither_bool=dither_bool,
        dither_distance=dither_distance,
        maximum_seeing=maximum_seeing,
        maximum_airmass=maximum_airmass,
        nights=nights,
        t_0=t_0,
        csv_save_file=csv_save_file
    )

    if submit:

        make_too_request_from_df(
            schedule,
            save_path=f"{schedule_name}.df"
        )

        # make_too_request_from_file(
        #     too_file_path=csv_path,
        #     save_path=csv_path.replace(".csv", ".db"),
        #     config_path=too_schedule_config
        # )

    return schedule


def schedule_ra_dec(
        schedule_name: str,
        ra_deg: float,
        dec_deg: float,
        pi: str,
        prog_id: str,
        filters: list = summer_filters,
        t_exp: float = 300.,
        n_exp: int = 1,
        dither_bool: bool = True,
        dither_distance="",
        nights=[1],
        t_0=None,
        maximum_airmass=2.0,
        summer: bool = True,
        use_field: bool = True,
        submit: bool = False,
        csv_save_file: str = None,
):
    if summer:
        get_best_field = get_best_summer_field
    else:
        raise NotImplementedError

    # Take RA/Dec and select nearest-centered field

    if use_field:
        best_field = get_best_field(ra_deg, dec_deg)
        ra_deg = best_field["RA"]
        dec_deg = best_field["Dec"]

    schedule = make_schedule(
        schedule_name=schedule_name,
        ra_degs=[ra_deg],
        dec_degs=[dec_deg],
        filters=filters,
        texp=t_exp,
        nexp=n_exp,
        dither_bool=dither_bool,
        dither_distance=dither_distance,
        nights=nights,
        t_0=t_0,
        pi=pi,
        prog_id=prog_id,
        submit=submit,
        csv_save_file=csv_save_file
    )

    return schedule

