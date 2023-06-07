"""
Module for testing submission of a schedule
"""
import logging
import os
import unittest

import pandas as pd
from datetime import date
from astropy.time import Time

from wintertoo.schedule import schedule_ra_dec
from wintertoo.validate import validate_schedule_df
from wintertoo.models import SummerRaDecToO, Program

logger = logging.getLogger(__name__)

test_data_dir = os.path.join(os.path.dirname(__file__), "testdata")
test_json_path = os.path.join(test_data_dir, "test_schedule.json")
test_df = pd.read_json(test_json_path)


class TestSchedule(unittest.TestCase):
    """
    Class for schedule testing
    """

    def test_validate_json(self):
        """
        Test validation of json

        :return: None
        """
        logger.info("Testing the validation with a test json")
        validate_schedule_df(test_df)

    def test_generate_schedule(self):
        """
        Test generating a schedule

        :return: None
        """
        logger.info("Testing schedule generation")
        schedule = schedule_ra_dec(
            too=SummerRaDecToO(
                ra_deg=173.7056754,
                dec_deg=11.253441,
                start_time_mjd=69721.1894969287,
                end_time_mjd=69722.1894969452,
            ),
            program=Program(
                pi_name="Stein",
                progname="2021A000",
                prog_key="763244309190298696786072636901190268976229595667748695826878",
                maxpriority=100,
                startdate=date(2021, 1, 1),
                enddate=date(2023, 12, 31),
            )
        )
        comp = pd.read_json(schedule.to_json())  # pylint: disable=no-member
        comp.to_json(test_json_path)
        self.assertEqual(test_df.to_json(), comp.to_json())  # pylint: disable=no-member
