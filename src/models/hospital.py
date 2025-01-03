import random
import requests
import threading
from datetime import datetime

from src.models.person import Doctor, Patient
from src.models.snapshot import Snapshot
from src.models.discharge import Discharge
from src.models.treatment import Treatment, RandomTreatmentType
from src.models.enums import DischargeStatus, Gender, EntityStatus, Expertise, TreatmentType


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
        self.doctors: list[Doctor] = self.__initialize_doctors()
        self.creation_date = datetime.now()
        self.patients_in_queue: dict[int, Patient] = dict()
        self.patients_in_progress: dict[int, Patient] = dict()
        self.treatments: dict[int, Treatment] = dict()
        self.snapshots: dict[int, Snapshot] = self.__initialize_initial_snapshot()
        self.discharges: dict[int, Discharge] = dict()
        self.__used_capacity = 0

    def register(self, url) -> None:
        response = requests.post(
            url,
            json={
                "entity_type": Hospital.__name__,
                "max_capacity": self.max_capacity,
                "eav": {
                    "name": self.name,
                    "doctor": self.doctors,
                    "creation_date": self.creation_date
                }
            }
        )

        body = response.json()
        self.entity_id = body['entity_id']
        self.time_rate = body['time_rate']

    def take_snapshot(self, url) -> None:
        response = requests.get(url, params={"entity_id": self.entity_id})
        body = response.json()

        snapshot = Snapshot.from_dict(body)
        # what if there was no response?
        # so, we can give default snapshot or empty one or something like these
        self.snapshots[snapshot.id] = snapshot
        self.__last_snapshot = snapshot

    def admit_patient(self, url) -> bool:
        return requests.post(url, json={"entity_id": self.entity_id, "persons_id": self.__admit_process()}).json()

    def discharge_patient(self, url: str, patient_id: int):
        return requests.post(url, json={"entity_id": self.entity_id, "persons_id": [patient_id]}).json()

    def __initialize_initial_snapshot(self, entity_id: int) -> dict[int, Snapshot]:
        snapshot = Snapshot(entity_id, [], False)
        return {snapshot.id: snapshot}

    def __initialize_doctors(self) -> list[Doctor]:
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

    def __admit_process(self) -> list:
        # i think we should move the rate to config files.
        admission_rate = random.uniform(0.6, 1)
        accepted_persons = []

        all_patients = self.__last_snapshot.persons + list(self.patients_in_queue.values())

        for person in all_patients:
            if self.__used_capacity >= self.max_capacity:
                break
            if random.random() < admission_rate:
                is_started = self.__start_treatment(person.id)
                if is_started:
                    self.patients_in_progress[person.id] = Patient(
                        person.name, person.gender, person.birth_date,
                        person.national_code, EntityStatus.INPROGRESS, person.status
                    )
                    accepted_persons.append(person.id)
                    print(f"Patient {person.id} status is in-progress.")
                else:
                    self.patients_in_queue[person.id] = Patient(
                        person.name, person.gender, person.birth_date,
                        person.national_code, EntityStatus.INQUEUE, person.status
                    )
                    print(f"Patient {person.id} status is in-queue.")
            else:
                self.patients_in_queue[person.id] = Patient(
                    person.name, person.gender, person.birth_date,
                    person.national_code, EntityStatus.INQUEUE, person.status
                )
                print(f"Patient {person.id} status is in-queue.")

        return accepted_persons

    def __assign_doctor(self, treatment_type: TreatmentType) -> Doctor | None:
        required_expertise = self.__expertise_mapping[treatment_type]

        available_doctors = [doctor for doctor in self.doctors if doctor.expertise == required_expertise]

        if not available_doctors:
            print(f"No available doctor with expertise in {required_expertise.value}")
            return

        return random.choice(available_doctors)

    def __start_treatment(self, patient_id: int) -> bool:
        treatment_type = RandomTreatmentType.generate()
        doctor = self.__assign_doctor(treatment_type)

        if not doctor:
            print(f"Treatment failed for patient {patient_id} because no doctor with expertise in "
                  f"{self.__expertise_mapping[treatment_type].value} is available.")
            return False

        treatment = Treatment(patient_id, doctor.id, treatment_type)

        self.treatments[treatment.id] = treatment
        self.__used_capacity += 1
        print(f"Started treatment: {treatment}")

        duration_seconds = treatment.duration.total_seconds()
        threading.Timer(duration_seconds, self.__discharge_patient, args=(treatment.id,)).start()

        return True

    def __discharge_patient(self, treatment_id: int) -> None:
        treatment = self.treatments.get(treatment_id)
        if not treatment:
            print(f"Treatment ID {treatment_id} not found.")
            return

        discharge = Discharge(treatment_id, DischargeStatus.HEALTHY)
        self.discharges[discharge.id] = discharge

        patient = self.patients_in_progress.pop(treatment.patient_id, None)
        if patient:
            print(f"Discharged patient {patient.id}: {discharge}")
            # TODO
            self.__used_capacity -= 1
            self.discharge_patient("", patient.id)
        else:
            print(f"Patient for treatment {treatment_id} not found.")
