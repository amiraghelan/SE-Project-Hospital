from enum import Enum


class DischargeStatus(Enum):
    HEALTHY = 'healthy',
    DEAD = 'dead'


class Gender(Enum):
    MALE = 'male',
    FEMALE = 'female'


class ServiceStatus(Enum):
    INQUEUE = 'in-queue'
    INPROGRESS = 'in-progress'
    SERVICEDONE = 'service-done'


class PersonStatus(Enum):
    ALIVE = 'alive',
    INJURED = 'injured'
    DEAD = 'dead'


class Expertise(Enum):
    ORTHOPEDICS = "Orthopedics"
    TRAUMATOLOGY = "Traumatology"
    PHYSICAL_THERAPY = "Physical Therapy"
    EMERGENCY_MEDICINE = "Emergency Medicine"
    PLASTIC_SURGERY = "Plastic Surgery"


class TreatmentType(Enum):
    FRACTURE_TREATMENT = "Fracture Treatment"
    WOUND_CARE = "Wound Care"
    PHYSIOTHERAPY = "Physiotherapy"
    BURN_TREATMENT = "Burn Treatment"
    DISLOCATION_TREATMENT = "Dislocation Treatment"
