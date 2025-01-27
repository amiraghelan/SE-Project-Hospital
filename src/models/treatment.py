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
    def __init__(self, patient_id: int, doctor_id: int, type: TreatmentType, time_rate: int) -> None:
        super().__init__()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.treatment_type = type
        self.start_date = datetime.now()
        self.duration = self.__estimate_duration(time_rate)
        self.end_date = self.start_date + self.duration

    def __estimate_duration(self, time_rate) -> timedelta:
        # 1 day : time_rate * seconds
        # So, for example 8 days equal to (8 * time_rate) seconds
        treatment_durations = {
            TreatmentType.FRACTURE_TREATMENT: timedelta(seconds=random.randint(6, 8) * time_rate),
            TreatmentType.WOUND_CARE: timedelta(seconds=random.randint(1, 3) * time_rate),
            TreatmentType.PHYSIOTHERAPY: timedelta(seconds=random.randint(2, 4) * time_rate),
            TreatmentType.BURN_TREATMENT: timedelta(seconds=random.randint(1, 4) * time_rate),
            TreatmentType.DISLOCATION_TREATMENT: timedelta(seconds=random.randint(3, 5) * time_rate),
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
