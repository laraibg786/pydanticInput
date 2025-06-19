from pydantic import BaseModel

from pydanticInput import Input


class Person(BaseModel):
    name: str
    age: int


Input(Person)
