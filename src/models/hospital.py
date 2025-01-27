import random
from time import sleep
import requests
import threading
from datetime import datetime

from src.models.person import Doctor, Person
from src.models.snapshot import Snapshot
from src.models.discharge import Discharge
from src.models.base_model import BaseEntity
from src.models.treatment import Treatment, RandomTreatmentType
from src.models.enums import (
    DischargeStatus,
    Gender,
    Expertise,
    TreatmentType,
)
from src.utils.logger import get_logger
logger = get_logger(__name__)


class Hospital(BaseEntity):
    def __init__(
        self, name: str, max_capacity: int, worldmodel_baseUrl: str = ""
    ) -> None:
        super().__init__()
        self.url = worldmodel_baseUrl

        self.id = -1
        self.name = name
        self.max_capacity = max_capacity
        self.used_capacity = 0
        self.time_rate = 1

        self.doctors: list[Doctor] = self.__initialize_doctors()
        self.__expertise_mapping = {
            TreatmentType.FRACTURE_TREATMENT: Expertise.ORTHOPEDICS,
            TreatmentType.WOUND_CARE: Expertise.TRAUMATOLOGY,
            TreatmentType.PHYSIOTHERAPY: Expertise.PHYSICAL_THERAPY,
            TreatmentType.BURN_TREATMENT: Expertise.PLASTIC_SURGERY,
            TreatmentType.DISLOCATION_TREATMENT: Expertise.ORTHOPEDICS,
        }

        self.treatments: dict[int, Treatment] = dict()
        self.discharges: dict[int, Discharge] = dict()
        self.patients_in_progress: dict[int, Person] = dict()
        self.servicing_patients_id: list[int] = []

        self.snapshots: dict[int, Snapshot] = self.__initialize_initial_snapshot(-1)
        self.last_snapshot = self.snapshots[-1]

    # ==registration========================================================
    def _register_request(self):
        while True:
            try:
                url = self.url + "/register"
                logger.info(f"trying to register on {url}")
                response = requests.post(
                    url,
                    json={
                        "entity_type": Hospital.__name__,
                        "max_capacity": self.max_capacity,
                        "eav": {
                            "name": self.name,
                            "doctor": [doctor.to_dict() for doctor in self.doctors],
                            "creation_date": self.creation_date.strftime("%Y-%m-%d"),
                        },
                    },
                )
                body = response.json()
                self.id = body["entity_id"]
                self.time_rate = body["time_rate"]
                logger.info(
                    f"registered with success - entity_id: {self.id} - time_rate: {self.time_rate}"
                )
                break
            except Exception as error:
                logger.error(error)
            sleep(5)

    def register(self):
        register_thread = threading.Thread(target=self._register_request)
        register_thread.setDaemon()
        register_thread.start()

    # =======================================================================

    # ==snapshot=============================================================
    def __initialize_initial_snapshot(self, id: int) -> dict[int, Snapshot]:
        snapshot = Snapshot(id, [], False)
        return {snapshot.id: snapshot}

    def take_snapshot(self) -> None:
        try:
            response = requests.get(self.url + f"/snapshot/{self.id}")
            body = response.json()
            if response.status_code != 200:
                logger.error(f"faild to load snapshot - statuscode: {response.status_code} - message: {body["message"]}")
            else:
                snapshot = Snapshot.from_dict(body)            
                self.snapshots[snapshot.id] = snapshot
                self.last_snapshot = snapshot    
                logger.info("snapshot was updated")
        except Exception as error:
            logger.error("faile to get last snapshot from worldmodel")
            logger.error(f"yoho: {error}")

    # =======================================================================

    #==handling patients=====================================================
    def admit_patient(self):
        persons = self.last_snapshot.persons
        temp_accepted_persons = []
        for person in persons:
            if person.id in self.servicing_patients_id:
                continue
            temp = self.max_capacity - (self.used_capacity + len(temp_accepted_persons))
            if temp <= 0:
                break
            
            if random.random() <= 0.7:
                temp_accepted_persons.append(person.id)
        try:
            if len(temp_accepted_persons) == 0:
                logger.info("no patiens in snapshot to admit")
                return
            
            logger.info(f"sending accept request for: {temp_accepted_persons}")
            
            response = requests.post(
                self.url + "/accept-person",
                json={"entity_id": self.id, "persons_id": temp_accepted_persons},
            )
            body = response.json()
            accepted_persons_id = body["accepted"]
            rejected_persons_id = body["rejected"]
            logger.info(f"accepted persons: {accepted_persons_id} - rejected persons: {rejected_persons_id}")
            self.servicing_patients_id.extend(accepted_persons_id)
            accepted_persons = list(
                filter(lambda p: p.id in accepted_persons_id, persons)
            )
            self._addmit_procces(accepted_persons)
        except Exception as error:
            logger.error(f"error while addmiting - {error}")

    def _addmit_procces(self, persons: list[Person]):
        for person in persons:
            if self.used_capacity >= self.max_capacity:
                break
            treatment_type = RandomTreatmentType.generate()
            doctor = self.__assign_doctor(treatment_type)
            if doctor:
                treatment = Treatment(person.id, doctor.id, treatment_type)
                self.treatments[treatment.id] = treatment
                self.servicing_patients_id.append(person.id)
                self.patients_in_progress[person.id] = person
                self.used_capacity = len(self.servicing_patients_id)

                duration = treatment.duration.total_seconds()

                timer = threading.Timer(
                    duration, self.discharge, args=(treatment.id, DischargeStatus.DEAD if treatment.is_dead else DischargeStatus.HEALTHY)
                )
                timer.setDaemon(True)
                timer.start()

    def discharge(self, treatment_id: int, discharge_status:DischargeStatus = DischargeStatus.HEALTHY, count:int=1):
        # TODO implement the maximum try with count parameter
        treatment = self.treatments.get(treatment_id)
        if not treatment:
            return
        
        try:
            person_id = treatment.patient_id
            if discharge_status == DischargeStatus.HEALTHY:
                response = requests.post(
                    self.url + "/service-done",
                    json={"entity_id": self.id, "persons_id": [person_id]},
                )
                body = response.json()
                accepted = body["accepted"]
                if accepted:
                    logger.info(f"service done for {accepted} was accepted")
                else:
                    logger.info(f"service done for {body["accepted"]} was accepted")

                if person_id in accepted:
                    discharge = Discharge(treatment.id, DischargeStatus.HEALTHY)
                    self.discharges[discharge.id] = discharge
        
            else:
                response = requests.post(
                    self.url + "/person-death",
                    json={"entity_id": self.id, "persons_id": [person_id]},
                )
                body = response.json()
                accepted = body["accepted"]
                if accepted:
                    logger.info(f"person death for {accepted} was accepted")
                else:
                    logger.info(f"person death for {body["accepted"]} was accepted")

                if person_id in accepted:
                    discharge = Discharge(treatment.id, DischargeStatus.DEAD)
                    self.discharges[discharge.id] = discharge
                    
        except Exception as error:
                logger.error("error in discharge")
                logger.error(error)

    #=========================================================================
    
    #==utils==================================================================
    def __initialize_doctors(self) -> list[Doctor]:
        doctors_data = [
            (
                "Sophia Williams",
                Gender.FEMALE,
                datetime(1985, 6, 15),
                Expertise.ORTHOPEDICS,
            ),
            ("John Smith", Gender.MALE, datetime(1990, 4, 22), Expertise.TRAUMATOLOGY),
            (
                "Emily Brown",
                Gender.FEMALE,
                datetime(1987, 3, 8),
                Expertise.PHYSICAL_THERAPY,
            ),
            (
                "Michael Johnson",
                Gender.MALE,
                datetime(1982, 12, 19),
                Expertise.EMERGENCY_MEDICINE,
            ),
            (
                "Emma Garcia",
                Gender.FEMALE,
                datetime(1995, 9, 14),
                Expertise.PLASTIC_SURGERY,
            ),
            (
                "David Hernandez",
                Gender.MALE,
                datetime(1980, 7, 1),
                Expertise.ORTHOPEDICS,
            ),
            (
                "Jane Martinez",
                Gender.FEMALE,
                datetime(1993, 11, 2),
                Expertise.PHYSICAL_THERAPY,
            ),
            (
                "Chris Davis",
                Gender.MALE,
                datetime(1992, 5, 30),
                Expertise.EMERGENCY_MEDICINE,
            ),
            (
                "Sarah Miller",
                Gender.FEMALE,
                datetime(1988, 10, 10),
                Expertise.PLASTIC_SURGERY,
            ),
            ("Alex Jones", Gender.MALE, datetime(1984, 8, 25), Expertise.TRAUMATOLOGY),
        ]

        return [
            Doctor(name, gender, birth_date, expertise)
            for name, gender, birth_date, expertise in doctors_data
        ]

    def __assign_doctor(self, treatment_type: TreatmentType) -> Doctor | None:
        required_expertise = self.__expertise_mapping[treatment_type]

        available_doctors = [
            doctor for doctor in self.doctors if doctor.expertise == required_expertise
        ]

        if not available_doctors:
            logger.info(f"No available doctor with expertise in {required_expertise.value}")
            return

        return random.choice(available_doctors)

    #=========================================================================