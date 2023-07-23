
def vector_add(t1: tuple, t2: tuple) -> tuple:
    """add two tuples together"""
    return tuple(sum(i) for i in zip(t1, t2))

def indices_to_pos(index: int, jndex: int) -> tuple[int, int]:
    """converts indices to coordinates"""
    return (jndex + 1, index + 1)

def pos_to_indices(coords: tuple[int, int]) -> tuple[int, int]:
    """converts coordinates to indices"""
    return (coords[1] - 1, coords[0] - 1)

def pos_to_notation(coords: tuple[int, int]) -> str:
    """converts coordinates to algebraic notation"""
    return f"{chr(coords[0] + 96)}{coords[1]}"

def notation_to_pos(notation: str) -> tuple[int, int]:
    """converts algebraic notation to coordinates"""
    return (ord(notation[0]) - 96, int(notation[1]))
