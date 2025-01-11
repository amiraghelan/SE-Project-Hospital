from datetime import datetime

from src.utils.random_id_generator import UniqueIDGenerator


class BaseEntity:
    def __init__(self) -> None:
        self.id = UniqueIDGenerator.generate_id()
        self.creation_date = datetime.now()
        self.modified_date = self.creation_date
