from enum import Enum
from pydantic import BaseModel

from pydanticInput import Input


class city(str, Enum):
    new_york = "New York"
    los_angeles = "Los Angeles"
    chicago = "Chicago"
class Person(BaseModel):
    name: str
    age: int
    # city: city


Input(Person)
