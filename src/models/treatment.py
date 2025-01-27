import random
from datetime import datetime, timedelta

from src.models.base_model import BaseEntity
from src.models.enums import TreatmentType


class RandomTreatmentType:
    _available_treatment_types = [TreatmentType.FRACTURE_TREATMENT, TreatmentType.WOUND_CARE,
                                  TreatmentType.PHYSIOTHERAPY, TreatmentType.BURN_TREATMENT,
                                  TreatmentType.DISLOCATION_TREATMENT]

    @staticmethod
    def generate():
        return random.choice(tuple(RandomTreatmentType._available_treatment_types))


class Treatment(BaseEntity):
    def __init__(self, patient_id: int, doctor_id: int, type: TreatmentType) -> None:
        super().__init__()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.treatment_type = type
        self.start_date = datetime.now()
        self.duration = self.estimate_duration()
        self.end_date = self.start_date + self.duration

    def estimate_duration(self) -> timedelta:
        treatment_durations = {
            TreatmentType.FRACTURE_TREATMENT: timedelta(seconds=random.randint(6, 8)),
            TreatmentType.WOUND_CARE: timedelta(seconds=random.randint(1, 3)),
            TreatmentType.PHYSIOTHERAPY: timedelta(seconds=random.randint(2, 4)),
            TreatmentType.BURN_TREATMENT: timedelta(seconds=random.randint(1, 4)),
            TreatmentType.DISLOCATION_TREATMENT: timedelta(seconds=random.randint(3, 5)),
        }

        return treatment_durations.get(self.treatment_type, timedelta(seconds=1))

    def __str__(self) -> str:
        return (
            f"Treatment ID: {self.id}\n"
            f"Patient ID: {self.patient_id}\n"
            f"Doctor ID: {self.doctor_id}\n"
            f"Treatment Type: {self.treatment_type.value}\n"
            f"Start Date: {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Date: {self.end_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration: {self.duration.seconds} seconds, "
        )
