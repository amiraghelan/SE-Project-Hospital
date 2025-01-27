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
        # we should move this to config
        self.death_rate = 0.2
        self.is_dead, self.death_time = self.__death_during_treatment()
        if self.death_time:
            self.end_date = self.death_time
        else:
            self.end_date = self.start_date + self.duration

    def __estimate_duration(self, time_rate: int) -> timedelta:
        treatment_durations = {
            TreatmentType.FRACTURE_TREATMENT: timedelta(seconds=random.randint(6, 8) * time_rate),
            TreatmentType.WOUND_CARE: timedelta(seconds=random.randint(1, 3) * time_rate),
            TreatmentType.PHYSIOTHERAPY: timedelta(seconds=random.randint(2, 4) * time_rate),
            TreatmentType.BURN_TREATMENT: timedelta(seconds=random.randint(1, 4) * time_rate),
            TreatmentType.DISLOCATION_TREATMENT: timedelta(seconds=random.randint(3, 5) * time_rate),
        }
        return treatment_durations.get(self.treatment_type, timedelta(seconds=1))

    def __death_during_treatment(self) -> (bool, datetime):  # type: ignore
        if random.random() < self.death_rate:
            death_offset_seconds = random.randint(0, self.duration.total_seconds())
            death_time = self.start_date + timedelta(seconds=death_offset_seconds)
            return True, death_time
        return False, None

    def __str__(self) -> str:
        death_info = (
            "Patient Status: Deceased\n"
            if self.is_dead
            else "Patient Status: Alive\n"
        )
        return (
            f"Treatment ID: {self.id}\n"
            f"Patient ID: {self.patient_id}\n"
            f"Doctor ID: {self.doctor_id}\n"
            f"Treatment Type: {self.treatment_type.value}\n"
            f"{death_info}"
            f"Start Date: {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Date: {self.end_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration: {self.duration.seconds} seconds\n"
        )
