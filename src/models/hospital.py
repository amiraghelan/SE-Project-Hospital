import random
import requests
import threading
from datetime import datetime

from src.models.person import Doctor, Patient, Person
from src.models.snapshot import Snapshot
from src.models.discharge import Discharge
from src.models.base_model import BaseEntity
from src.models.treatment import Treatment, RandomTreatmentType
from src.models.enums import DischargeStatus, Gender, EntityStatus, PatientStatus,  Expertise, TreatmentType


class Hospital(BaseEntity):
    def __init__(self, name: str, max_capacity: int) -> None:
        super().__init__()
        self.name = name
        self.max_capacity = max_capacity
        self.doctors: list[Doctor] = self.__initialize_doctors()
        self.treatments: dict[int, Treatment] = dict()
        self.snapshots: dict[int, Snapshot] = self.__initialize_initial_snapshot(-1)
        self.discharges: dict[int, Discharge] = dict()
        self.patients_in_progress: dict[int, Patient] = dict()
        self.__entity_id = -1
        self.__time_rate = 100
        self.__used_capacity = 0
        self.__last_snapshot = self.snapshots[-1]
        self.__expertise_mapping = {
            TreatmentType.FRACTURE_TREATMENT: Expertise.ORTHOPEDICS,
            TreatmentType.WOUND_CARE: Expertise.TRAUMATOLOGY,
            TreatmentType.PHYSIOTHERAPY: Expertise.PHYSICAL_THERAPY,
            TreatmentType.BURN_TREATMENT: Expertise.PLASTIC_SURGERY,
            TreatmentType.DISLOCATION_TREATMENT: Expertise.ORTHOPEDICS,
        }

    def register(self, url) -> bool:
        response = requests.post(
            url,
            json={
                "entity_type": Hospital.__name__,
                "max_capacity": self.max_capacity,
                "eav": {
                    "name": self.name,
                    "doctor": [doctor.to_dict() for doctor in self.doctors],
                    "creation_date": self.creation_date.strftime('%Y-%m-%d')
                }
            }
        )

        body = response.json()
        self.__entity_id = body['entity_id']
        self.__time_rate = body['time_rate']

        print(f"In {__name__}.{self.register.__name__}: entity_id:{body['entity_id']}")
        print(100 * "-")

        return response.status_code == 200

    def take_snapshot(self, url) -> None:
        response = requests.get(url, params={"entity_id": self.__entity_id})
        body = response.json()

        snapshot = Snapshot.from_dict(body)

        print(f"In {__name__}.{self.take_snapshot.__name__}: ")
        print(f"snapshot id: {snapshot.id}\n"
              f"persons in snapshot:")
        if not snapshot.persons or len(snapshot.persons) == 0:
            print("empty!!")
        else:
            for person in snapshot.persons:
                print(person.id, end=" ")
        print()
        print(100 * "-")

        # what if there was no response?
        # so, we can give default snapshot or empty one or something like these
        self.snapshots[snapshot.id] = snapshot
        self.__last_snapshot = snapshot

    def admit_patient(self, admit_url, discharge_url) -> bool:
        persons = self.__admit_process(discharge_url)
        if persons and len(persons) != 0:
            print(f"In {__name__}.{self.admit_patient.__name__}:\n" +
                  f"persons admitted:")
            for person in persons:
                print(person, end=" ")
            print()
            print(100 * "-")

            return requests.post(admit_url, json={"entity_id": self.__entity_id, "persons_id": persons}).json()
        else:
            return False

    def discharge_patient(self, url: str, patient_id: int):
        return requests.post(url, json={"entity_id": self.__entity_id, "persons_id": [patient_id]}).json()

    def __initialize_initial_snapshot(self, id: int) -> dict[int, Snapshot]:
        snapshot = Snapshot(id, [], False)
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

        return [Doctor(name, gender, birth_date, expertise) for name, gender, birth_date, expertise in doctors_data]

    def __admit_process(self, discharge_url) -> list:
        # i think we should move the rate to config files.
        admission_rate = random.uniform(0.7, 1)
        patient_inline = []

        for person in self.__last_snapshot.persons:
            if self.__used_capacity >= self.max_capacity:
                break
            if random.random() < admission_rate and self.__start_treatment(person.id, discharge_url):
                self.__mark_patient_in_progress(person)
                patient_inline.append(person.id)
            else:
                self.__mark_patient_in_queue(person)

        return patient_inline

    def __mark_patient_in_queue(self, person: Person) -> None:
        print(f"In {__name__}.{self.__mark_patient_in_queue.__name__}:")
        print(f"Patient {person.id} status is in-queue.")
        print(100 * "-")

    def __mark_patient_in_progress(self, person: Person) -> None:
        self.patients_in_progress[person.id] = Patient(
            person.name, person.gender, person.birth_date,
            person.national_code, EntityStatus.INPROGRESS, PatientStatus.INJURED
        )
        print(f"In {__name__}.{self.__mark_patient_in_progress.__name__}:")
        print(f"Patient {person.id} status is in-progress.")
        print(100 * "-")

    def __assign_doctor(self, treatment_type: TreatmentType) -> Doctor | None:
        required_expertise = self.__expertise_mapping[treatment_type]

        available_doctors = [doctor for doctor in self.doctors if doctor.expertise == required_expertise]

        if not available_doctors:
            print(f"In {__name__}.{self.__assign_doctor.__name__}:")
            print(f"No available doctor with expertise in {required_expertise.value}")
            print(100 * "-")
            return

        return random.choice(available_doctors)

    def __start_treatment(self, patient_id: int, discharge_url: str) -> bool:
        treatment_type = RandomTreatmentType.generate()
        doctor = self.__assign_doctor(treatment_type)

        if not doctor:
            print(f"In {__name__}.{self.__start_treatment.__name__}:")
            print(f"Treatment failed for patient {patient_id} because no doctor with expertise in "
                  f"{self.__expertise_mapping[treatment_type].value} is available.")
            print(100 * "-")
            return False

        treatment = Treatment(patient_id, doctor.id, treatment_type)

        self.treatments[treatment.id] = treatment
        self.__used_capacity += 1

        print(f"In {__name__}.{self.__start_treatment.__name__}:")
        print(f"Started treatment: {treatment.id}, patient id: {treatment.patient_id} with duration {treatment.duration}")
        print(100 * "-")

        duration = treatment.duration.total_seconds()
        threading.Timer(duration, self.__discharge_patient, args=(treatment.id, discharge_url,)).start()

        return True

    def __discharge_patient(self, treatment_id: int, discharge_url: str) -> None:
        treatment = self.treatments.get(treatment_id)
        if not treatment:
            print(f"In {__name__}.{self.__discharge_patient.__name__}:")
            print(f"Treatment ID {treatment_id} not found.")
            print(100 * "-")
            return

        discharge = Discharge(treatment_id, DischargeStatus.HEALTHY)
        self.discharges[discharge.id] = discharge

        patient = self.patients_in_progress.pop(treatment.patient_id, None)
        if patient:
            print(f"In {__name__}.{self.__discharge_patient.__name__}:")
            print(f"Discharged patient {patient.id}:\n{discharge}")
            print(100 * "-")

            self.__used_capacity -= 1
            self.discharge_patient(discharge_url, patient.id)
        else:
            print(f"In {__name__}.{self.__discharge_patient.__name__}:")
            print(f"Patient with treatment id {treatment_id} not found.")
            print(100 * "-")

    def get_entity_id(self) -> int:
        return self.__entity_id
