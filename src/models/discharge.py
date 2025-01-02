from enum import Enum
from datetime import datetime
from src.utils.random_id_generator import UniqueIDGenerator

class DischargeStatus(Enum):
    HEALTHY = 'healthy',
    DEAD = 'dead'

class Discharge:
    def __init__(self, treatment_id: int, discharge_status: DischargeStatus) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.treatment_id = treatment_id
        self.discharge_status = discharge_status
        self.discharge_date = datetime.now()

    def __str__(self):
        return f"Treatment with id {self.treatment_id} occur at {self.discharge_date} with status {self.discharge_status}!"