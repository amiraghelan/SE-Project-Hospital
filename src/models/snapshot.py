from datetime import datetime

from src.models.person import Person
from src.utils.logger import get_logger


logger = get_logger(__name__)


class Snapshot:
    def __init__(self, id: int, persons: list[Person], earthquake_status: bool) -> None:
        self.id = id
        self.persons = persons
        self.earthquake_status = earthquake_status
        self.creation_date = datetime.now()
        persons_id = list(map(lambda x: x.id, persons))
        logger.info("new snap shot was created")
        logger.info(
            f"snapshpt_id: {id} - persons_id: {persons_id} - earthquake: {earthquake_status}"
        )

    @classmethod
    def from_dict(cls, data):
        persons = [Person(person["id"], person["name"], person["gender"], person["birth_date"], person["national_code"], person["status"]) for person in data["persons"]]
        return cls(data["id"], persons, data["earthquake_status"])

    def __str__(self):
        return (
            f"Snapshot ID: {self.id}\n"
            f"Persons: {', '.join(map(lambda person: str(person.id), self.persons))}\n"
            f"Earthquake Status: {'Active' if self.earthquake_status else 'Inactive'}\n"
            f"Creation Date: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
