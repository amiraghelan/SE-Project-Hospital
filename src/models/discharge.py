from src.models.base_model import BaseEntity
from src.models.enums import DischargeStatus


class Discharge(BaseEntity):
    def __init__(self, treatment_id: int, discharge_status: DischargeStatus) -> None:
        super().__init__()
        self.treatment_id = treatment_id
        self.discharge_status = discharge_status
        self.discharge_date = self.creation_date

    def __str__(self):
        return (
            f"Discharge ID: {self.id}\n"
            f"Treatment ID: {self.treatment_id}\n"
            f"Discharge Status: {self.discharge_status.value}\n"
            f"Discharge Date: {self.discharge_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
