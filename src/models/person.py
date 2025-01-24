from datetime import datetime

from src.models.enums import (
    Gender,
    Expertise,
    PersonStatus,
)
from src.models.base_model import BaseEntity


class Person:
    def __init__(
        self,
        id: int,
        name: str,
        gender: str,
        birth_date: str,
        national_code: str,
        status:str,
        death_date=None,
    ) -> None:
        self.id = id
        self.name = name
        self.gender = Gender.MALE if gender == "male" else Gender.FEMALE
        self.birth_date = datetime.fromisoformat(birth_date)
        self.national_code = national_code
        self.death_date: datetime | None = datetime.fromisoformat(death_date) if  death_date else None
        match status:
            case 'alive':
                self.status = PersonStatus.ALIVE
            case 'injured':
                self.status = PersonStatus.ALIVE
            case 'dead':
                self.status = PersonStatus.DEAD

    def __str__(self) -> str:
        return (
            f"Person ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Gender: {self.gender.value}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d')}\n"
            f"National Code: {self.national_code}\n"
            f"Death Date: {self.death_date.strftime('%Y-%m-%d %H:%M:%S') if self.death_date else 'N/A'}"
        )

class Doctor(BaseEntity):
    def __init__(
        self, name: str, gender: Gender, birth_date: datetime, expertise: Expertise
    ) -> None:
        super().__init__()
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
        self.expertise = expertise

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender.value,
            "birth_date": self.birth_date.strftime("%Y-%m-%d"),
            "expertise": self.expertise.value,
        }

    def __str__(self):
        return (
            f"Doctor ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Gender: {self.gender.name}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d')}\n"
            f"Expertise: {self.expertise.value}"
        )
