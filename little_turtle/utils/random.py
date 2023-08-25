import random
from typing import List, TypedDict, Any


def random_pick_n(items: List[Any], n: int) -> List[TypedDict]:
    return random.sample(items, n)
