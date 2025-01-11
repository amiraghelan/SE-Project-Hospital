from datetime import datetime

from src.models.person import Person


class Snapshot:
    def __init__(self, id: int, persons: list[Person], earthquake_status: bool) -> None:
        self.id = id
        self.persons = persons
        self.earthquake_status = earthquake_status
        self.creation_date = datetime.now()

    @classmethod
    def from_dict(cls, data):
        persons = [Person.from_dict(person) for person in data['persons']]
        return cls(data['id'], persons, data['earthquake_status'])

    def __str__(self):
        return (
            f"Snapshot ID: {self.id}\n"
            f"Persons: {', '.join(map(lambda person: str(person.id), self.persons))}\n"
            f"Earthquake Status: {'Active' if self.earthquake_status else 'Inactive'}\n"
            f"Creation Date: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
