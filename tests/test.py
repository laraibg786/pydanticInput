import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from pydanticInput import Input


class CityEnum(str, Enum):
    new_york = "New York"
    los_angeles = "Los Angeles"
    chicago = "Chicago"


class Address(BaseModel):
    street: str
    zip_code: str
    country: str


class Person(BaseModel):
    # Basic Types
    name: str
    age: int
    height: float
    active: bool

    # Enum
    city: CityEnum

    # Date/Time Types
    date_of_birth: datetime.date
    time_of_birth: datetime.time
    current_moment: datetime.datetime
    # duration_alive: datetime.timedelta  # ❌ Not handled

    # Optional and Union
    nickname: Optional[str] = None
    contact_info: Union[str, float, datetime.datetime]

    # Collections
    tags: List[Union[str, int]]
    # scores: Tuple[int, int, int]  # ❌ Tuple not handled
    preferences: Dict[str, str]  # ❌ Dict not handled
    # unique_ids: Set[int]  # ❌ Set not handled

    # Special Types
    # website: HttpUrl
    # ip_address: IPvAnyAddress
    account_balance: Decimal
    # user_id: UUID

    # Nested Model
    # address: Address  # ❌ Nested BaseModel not handled


Input(Person)
