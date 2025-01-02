from datetime import *
from snapshot import *
from discharge import *
from person import *
from treatment import *
import random
import requests  # type: ignore


class Hospital:
    __expertise_mapping = {
        TreatmentType.FRACTURE_TREATMENT: Expertise.ORTHOPEDICS,
        TreatmentType.WOUND_CARE: Expertise.TRAUMATOLOGY,
        TreatmentType.PHYSIOTHERAPY: Expertise.PHYSICAL_THERAPY,
        TreatmentType.BURN_TREATMENT: Expertise.PLASTIC_SURGERY,
        TreatmentType.DISLOCATION_TREATMENT: Expertise.ORTHOPEDICS,
    }

    def __init__(self, name: str, max_capacity: int) -> None:
        self.name = name
        self.max_capacity = max_capacity
        self.doctors = self.__initialize_doctors()
        self.creation_date = datetime.now()
        self.patients_in_queue = dict()
        self.patients_in_progress = dict()
        self.treatments = dict()
        self.snapshots = dict()
        self.discharges = dict()

    def register(self, url) -> None:
        response = requests.post(url, json={"type": Hospital.__name__, "max_capacity": self.max_capacity, "eav": dict()})

        body = response.json()
        self.entity_id = body.entity_id
        self.time_rate = body.time_rate

    def take_snapshot(self, url) -> None:
        response = requests.get(url, params={"entity_id": self.entity_id})
        body = response.json()

        snapshot = Snapshot.from_dict(body)

        self.snapshots[snapshot.id] = snapshot
        self.__last_snapshot = snapshot

    def admit_patient(self, url) -> bool:
        admission_rate = random.uniform(0.6, 1)
        accepted_persons_id = []

        for person in self.__last_snapshot.persons:
            if random.random() < admission_rate:

                # TODO add logic for fail
                self.__start_treatment(person.id)

                accepted_persons_id.append(person.id)
                self.patients_in_progress[person.id] = Patient(
                    person.name, person.gender, person.birth_date,
                    person.national_code, EntityStatus.INPROGRESS, person.status
                )

            else:
                self.patients_in_queue[person.id] = Patient(
                    person.name, person.gender, person.birth_date,
                    person.national_code, EntityStatus.INQUEUE, person.status
                )
                print(f"Patient {person.id} status is in-queue.")

        response = requests.post(url, json={"entity_id": self.entity_id, "persons_id": accepted_persons_id})
        return response.json()

    def discharge_patient(self, url):
        patients_discharge = []
        for treatment in self.treatments.values():
            if datetime.now() > treatment.end_date:
                discharge = Discharge(treatment.id, DischargeStatus.HEALTHY)
                self.discharges[discharge.id] = discharge
                patients_discharge.append(self.patients_in_progress.pop(treatment.patient_id))

        requests.post(url, json={"entity_id": self.entity_id, "persons_id": patients_discharge})

    def __initialize_doctors(self) -> None:
        doctors_data = [
            ("Sophia Williams", Gender.FEMALE, datetime(1985, 6, 15), Expertise.ORTHOPEDICS),
            ("John Smith", Gender.MALE, datetime(1990, 4, 22), Expertise.TRAUMATOLOGY),
            ("Emily Brown", Gender.FEMALE, datetime(1987, 3, 8), Expertise.PHYSICAL_THERAPY),
            ("Michael Johnson", Gender.MALE, datetime(1982, 12, 19), Expertise.EMERGENCY_MEDICINE),
            ("Emma Garcia", Gender.FEMALE, datetime(1995, 9, 14), Expertise.PLASTIC_SURGERY),
            ("David Hernandez", Gender.MALE, datetime(1980, 7, 1), Expertise.ORTHOPEDICS),
            ("Jane Martinez", Gender.FEMALE, datetime(1993, 11, 2), Expertise.PHYSICAL_THERAPY),
            ("Chris Davis", Gender.MALE, datetime(1992, 5, 30), Expertise.EMERGENCY_MEDICINE),
            ("Sarah Miller", Gender.FEMALE, datetime(1988, 10, 10), Expertise.PLASTIC_SURGERY),
            ("Alex Jones", Gender.MALE, datetime(1984, 8, 25), Expertise.TRAUMATOLOGY),
        ]

        return [Doctor(full_name, gender, birth_date, expertise) for full_name, gender, birth_date, expertise in doctors_data]

    def __assign_doctor(self, treatment_type: TreatmentType) -> Doctor:
        required_expertise = self.__expertise_mapping[treatment_type]

        available_doctors = [doctor for doctor in self.doctors if doctor.expertise == required_expertise]

        if not available_doctors:
            # TODO logic for not available docotor
            raise Exception(f"No available doctor with expertise in {required_expertise.value}")

        return random.choice(available_doctors)

    def __start_treatment(self, patient_id: int) -> None:
        treatment_type = RandomTreatmentType.generate()

        doctor = self.__assign_doctor(treatment_type)

        treatment = Treatment(patient_id, doctor.id, treatment_type)

        self.treatments[treatment.id] = treatment
