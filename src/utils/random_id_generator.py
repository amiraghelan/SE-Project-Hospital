import random

class UniqueIDGenerator:
    _available_ids = set(range(1, 1_000))
    _id_start = 1_001
    _id_increment = 1_000
    
    @staticmethod
    def generate_id():
        if not UniqueIDGenerator._available_ids:
            UniqueIDGenerator._extend_id_pool()
        new_id = random.choice(tuple(UniqueIDGenerator._available_ids))
        UniqueIDGenerator._available_ids.remove(new_id)
        return new_id
    
    @staticmethod
    def _extend_id_pool():
        new_ids = set(range(UniqueIDGenerator._id_start, UniqueIDGenerator._id_start + UniqueIDGenerator._id_increment))
        UniqueIDGenerator._available_ids.update(new_ids)
        UniqueIDGenerator._id_start += UniqueIDGenerator._id_increment
