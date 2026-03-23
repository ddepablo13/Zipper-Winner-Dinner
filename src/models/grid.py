from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    row: int
    col: int
    value: int = 0  # 0 = empty, positive = waypoint number


class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.cells: list[list[Cell]] = [
            [Cell(r, c) for c in range(cols)] for r in range(rows)
        ]
        # Walls stored as normalized pairs: frozenset of two (row, col) tuples
        self.walls: set[frozenset[tuple[int, int]]] = set()

    def set_cell(self, row: int, col: int, value: int):
        self.cells[row][col] = Cell(row, col, value)

    def add_wall(self, a: tuple[int, int], b: tuple[int, int]):
        self.walls.add(frozenset((a, b)))

    def has_wall(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        return frozenset((a, b)) in self.walls

    def is_in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_in_bounds(nr, nc) and not self.has_wall((row, col), (nr, nc)):
                neighbors.append((nr, nc))
        return neighbors
