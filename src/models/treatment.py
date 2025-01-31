import random
from datetime import datetime, timedelta

from src.models.base_model import BaseEntity
from src.models.enums import TreatmentType
import src.config as config
from src.utils.logger import get_logger

logger = get_logger(__name__)



class RandomTreatmentType:
    _available_treatment_types = [TreatmentType.FRACTURE_TREATMENT, TreatmentType.WOUND_CARE,
                                  TreatmentType.PHYSIOTHERAPY, TreatmentType.BURN_TREATMENT,
                                  TreatmentType.DISLOCATION_TREATMENT]

    @staticmethod
    def generate():
        return random.choice(tuple(RandomTreatmentType._available_treatment_types))


class Treatment(BaseEntity):
    def __init__(self, patient_id: int, doctor_id: int, treatment_type: TreatmentType, time_rate: int) -> None:
        super().__init__()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.treatment_type = treatment_type
        self.start_date = datetime.now()
        self.duration = self.__estimate_duration(time_rate)
        self.is_dead, self.death_offset_seconds = self.__death_during_treatment()
        if self.is_dead and self.death_offset_seconds:
            self.duration = self.death_offset_seconds
        self.end_date = self.start_date + timedelta(seconds=self.duration)
        
        logger.info(f"treatmeant created: patient_id={self.patient_id} - duration = {self.duration} - healthy = {not self.is_dead}")

    def __estimate_duration(self, time_rate: int) -> int:
        match self.treatment_type:
            case TreatmentType.FRACTURE_TREATMENT:
                return round(random.randint(6, 8) / time_rate)
            case TreatmentType.PHYSIOTHERAPY:
                return round(random.randint(2, 4) / time_rate)
            case TreatmentType.BURN_TREATMENT:
                return round(random.randint(1, 4) / time_rate)
            case TreatmentType.DISLOCATION_TREATMENT:
                return round(random.randint(3, 5) / time_rate)
            case _:    
                # added to prevent linter warning 
                return 1

    def __death_during_treatment(self) -> (bool, int):  # type: ignore
        if random.random() < config.DEATH_RATE:
            death_offset_seconds : int = random.randint(0, self.duration)
            return True, death_offset_seconds
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
            f"Duration: {self.duration} seconds\n"
        )
