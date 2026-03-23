from src.models.puzzle import Puzzle


def read_json(path: str) -> Puzzle:
    puzzle = Puzzle.from_json(path)
    if not puzzle.validate():
        raise ValueError("Invalid puzzle: waypoints must be sequential starting from 1")
    return puzzle
