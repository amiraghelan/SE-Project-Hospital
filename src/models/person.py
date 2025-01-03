from datetime import datetime

from src.utils.random_id_generator import UniqueIDGenerator
from src.models.enums import Gender, Expertise, EntityStatus, PatientStatus


class Doctor:
    def __init__(self, full_name: str, gender: Gender, birth_date: datetime, expertise: Expertise) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.full_name = full_name
        self.gender = gender
        self.birth_date = birth_date
        self.expertise = expertise

    def __str__(self):
        return (
            f"Doctor ID: {self.id}\n"
            f"Full Name: {self.full_name}\n"
            f"Gender: {self.gender.name}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d')}\n"
            f"Expertise: {self.expertise.value}"
        )
    def to_json(self):
        return {
            'id':self.id,
            'full_name':self.full_name,
            'gender':self.gender.value,
            'birth_date':self.birth_date.strftime('%Y-%m-%d'),
            'experties':self.expertise.value 
        }


class Patient:
    def __init__(self, full_name: str, gender: Gender, birth_date: datetime, national_code: str, entity_status: EntityStatus, patient_status: PatientStatus) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.full_name = full_name
        self.gender = gender
        self.birth_date = birth_date
        self.national_code = national_code
        self.entity_status = entity_status
        self.patient_status = patient_status

    def __str__(self) -> str:
        return (
            f"Patient ID: {self.id}\n"
            f"Full Name: {self.full_name}\n"
            f"Gender: {self.gender}\n"
            f"Birth Date: {self.birth_date.strftime('%Y-%m-%d') if isinstance(self.birth_date, datetime) else self.birth_date}\n"
            f"National Code: {self.national_code}\n"
            f"Entity Status: {self.entity_status.value}\n"
            f"Patient Status: {self.patient_status.value}"
        )
