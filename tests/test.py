import datetime
import decimal
import enum
import typing

import pydantic

from pydanticInput import Input


class CityEnum(str, enum.Enum):
    new_york = "New York"
    los_angeles = "Los Angeles"
    chicago = "Chicago"


class Address(pydantic.BaseModel):
    street: str
    zip_code: str
    country: str


class Person(pydantic.BaseModel):
    # primitives
    name: str
    age: int
    height: float
    account_balance: decimal.Decimal
    active: bool
    address: Address

    # Enum
    city: CityEnum

    # datetime Types
    date_of_birth: datetime.date
    time_of_birth: datetime.time
    current_moment: datetime.datetime

    # special forms
    nickname: typing.Optional[str] = None
    contact_info: typing.Union[str, float, datetime.datetime]

    # Collections
    tags: typing.List[typing.Union[str, int]]
    preferences: typing.Dict[str, str]


print(Person(**Input(Person)))
