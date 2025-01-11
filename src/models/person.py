from datetime import datetime

from src.models.enums import Gender, Expertise, EntityStatus, PatientStatus
from src.models.base_model import BaseEntity


class Person:
    def __init__(self, id: int, name: str, gender: Gender, birth_date: datetime,
                 national_code: str, death_date=None) -> None:
        self.id = id
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
        self.national_code = national_code
        self.death_date: datetime = death_date

    @classmethod
    def from_dict(cls, data):
        gender = Gender.MALE if data['gender'] == 'male' else Gender.FEMALE
        return cls(data['id'], data['name'], gender, data['birth_date'], data['national_code'])

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
    def __init__(self, name: str, gender: Gender, birth_date: datetime, expertise: Expertise) -> None:
        super().__init__()
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
        self.expertise = expertise

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender.value,
            'birth_date': self.birth_date.strftime('%Y-%m-%d'),
            'expertise': self.expertise.value
        }

    def __str__(self):
        return (
            f"Doctor ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Gender: {self.gender.name}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d')}\n"
            f"Expertise: {self.expertise.value}"
        )


class Patient(BaseEntity):
    def __init__(self, name: str, gender: Gender, birth_date: datetime, national_code: str,
                 entity_status: EntityStatus, patient_status: PatientStatus) -> None:
        super().__init__()
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
        self.national_code = national_code
        self.entity_status = entity_status
        self.patient_status = patient_status

    def __str__(self) -> str:
        return (
            f"Patient ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Gender: {self.gender.value}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d') if isinstance(self.birth_date, datetime) else self.birth_date}\n"
            f"National Code: {self.national_code}\n"
            f"Entity Status: {self.entity_status.value}\n"
            f"Patient Status: {self.patient_status.value}"
        )
