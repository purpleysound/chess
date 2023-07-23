
def tuple_add(t1: tuple, t2: tuple) -> tuple:
    """add two tuples together"""
    return tuple(sum(i) for i in zip(t1, t2))

def indices_to_coords(index: int, jndex: int) -> tuple[int, int]:
    """converts indices to coordinates"""
    return (jndex + 1, index + 1)