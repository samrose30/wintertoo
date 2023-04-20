from typing import List, Literal

from astropy import units as u
from astropy.time import Time
from pydantic import BaseModel, Field, validator
from winterdrp.pipelines.summer.config.models.program import ProgramCredentials

from wintertoo.errors import WinterValidationError
from wintertoo.utils import get_date


class BaseImageQuery(BaseModel):
    program_list: list[ProgramCredentials] = Field(
        title="List of programs to search for", min_items=1
    )
    start_date: int = Field(
        title="Start date for images",
        le=get_date(Time.now()),
        default=get_date(Time.now() - 30.0 * u.day),
    )
    end_date: int = Field(
        title="End date for images",
        le=get_date(Time.now()),
        default=get_date(Time.now()),
    )
    kind: Literal["raw", "science", "diff"] = Field(
        default="science", title="raw/science/diff"
    )


class RectangleImageQuery(BaseImageQuery):
    ra_min: float = Field(title="Minimum RA (degrees)", ge=0.0, le=360.0, default=0.0)
    ra_max: float = Field(title="Minimum RA (degrees)", ge=0.0, le=360.0, default=360.0)

    dec_min: float = Field(
        title="Minimum dec (degrees)", ge=-90.0, le=90.0, default=-90.0
    )
    dec_max: float = Field(
        title="Minimum dec (degrees)", ge=-90.0, le=90.0, default=90.0
    )

    @validator("ra_max", "dec_max")
    @classmethod
    def validate_field_pairs(cls, field_value, values, field):
        min_key = field.name.replace("max", "min")
        min_val = values[min_key]
        if not field_value > min_val:
            raise WinterValidationError(
                f"{field.name} ({field_value}) not greater than {min_key} ({min_val})"
            )
        return field_value


class ConeImageQuery(BaseImageQuery):
    ra: float = Field(title="Center RA (degrees)", ge=0.0, le=360.0, default=0.0)
    dec: float = Field(title="Center dec (degrees)", ge=-90.0, le=90.0, default=-90.0)
    radius_deg: float = Field(
        title="Search radius in degrees", ge=0.0, le=90.0, default=1.0
    )
