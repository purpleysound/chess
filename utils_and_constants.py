
def vector_add(t1: tuple, t2: tuple) -> tuple:
    """add two tuples together"""
    return tuple(sum(i) for i in zip(t1, t2))

def indices_to_pos(index: int, jndex: int) -> tuple[int, int]:
    """converts indices to coordinates"""
    return (jndex + 1, index + 1)

def pos_to_indices(coords: tuple[int, int]) -> tuple[int, int]:
    """converts coordinates to indices"""
    return (coords[1] - 1, coords[0] - 1)
