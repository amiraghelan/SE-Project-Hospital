import random
from datetime import datetime, timedelta
from src.utils.random_id_generator import UniqueIDGenerator
from src.models.enums import TreatmentType


class RandomTreatmentType:
    _available_treatment_types = [TreatmentType.FRACTURE_TREATMENT, TreatmentType.WOUND_CARE,
                                  TreatmentType.PHYSIOTHERAPY, TreatmentType.BURN_TREATMENT,
                                  TreatmentType.DISLOCATION_TREATMENT]

    @staticmethod
    def generate():
        return random.choice(tuple(RandomTreatmentType._available_treatment_types))


class Treatment:
    def __init__(self, patient_id: int, doctor_id: int, type: TreatmentType) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.treatment_type = type
        self.start_date = datetime.now()
        self.duration = self.estimate_duration()
        self.end_date = self.start_date + self.duration

    def estimate_duration(self) -> timedelta:
        treatment_durations = {
            TreatmentType.FRACTURE_TREATMENT: timedelta(days=random.randint(6, 8)),
            TreatmentType.WOUND_CARE: timedelta(days=random.randint(1, 3)),
            TreatmentType.PHYSIOTHERAPY: timedelta(days=random.randint(2, 4)),
            TreatmentType.BURN_TREATMENT: timedelta(days=random.randint(1, 4)),
            TreatmentType.DISLOCATION_TREATMENT: timedelta(days=random.randint(3, 5)),
        }

        return treatment_durations.get(self.treatment_type, timedelta(days=1))

    def __str__(self) -> str:
        return (
            f"Treatment ID: {self.id}\n"
            f"Patient ID: {self.patient_id}\n"
            f"Doctor ID: {self.doctor_id}\n"
            f"Treatment Type: {self.treatment_type.value}\n"
            f"Start Date: {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Date: {self.end_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration: {self.duration.days} days, {self.duration.seconds // 3600} hours, "
            f"{(self.duration.seconds % 3600) // 60} minutes"
        )
