from src.utils.random_id_generator import UniqueIDGenerator
from datetime import datetime


class Snapshot:
    def __init__(self, entity_id: int, persons: list, earthquake_status: bool) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.entity_id = entity_id
        self.persons = persons
        self.earthquake_status = earthquake_status
        self.creation_date = datetime.now()

    @classmethod
    def from_dict(cls, data):
        return cls(data['entity_id'], data['persons'], data['earthquake_status'])

    def __str__(self):
        return (
            f"Snapshot ID: {self.id}\n"
            f"Entity ID: {self.entity_id}\n"
            f"Persons: {', '.join(map(lambda person: str(person.id), self.persons))}\n"
            f"Earthquake Status: {'Active' if self.earthquake_status else 'Inactive'}\n"
            f"Creation Date: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
