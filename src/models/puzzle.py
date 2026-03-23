from __future__ import annotations
import json
from src.models.grid import Grid


class Puzzle:
    def __init__(self, grid: Grid, waypoints: dict[int, tuple[int, int]]):
        self.grid = grid
        self.waypoints = waypoints  # {waypoint_number: (row, col)}
        self.total_cells = grid.rows * grid.cols

    @classmethod
    def from_grid(cls, grid: Grid) -> Puzzle:
        waypoints = {}
        for r in range(grid.rows):
            for c in range(grid.cols):
                val = grid.cells[r][c].value
                if val > 0:
                    waypoints[val] = (r, c)
        return cls(grid, waypoints)

    def validate(self) -> bool:
        if not self.waypoints:
            return False
        expected = list(range(1, max(self.waypoints.keys()) + 1))
        return sorted(self.waypoints.keys()) == expected

    def to_dict(self) -> dict:
        grid_values = [
            [self.grid.cells[r][c].value for c in range(self.grid.cols)]
            for r in range(self.grid.rows)
        ]
        walls = [
            sorted(list(w)) for w in self.grid.walls
        ]
        return {
            "rows": self.grid.rows,
            "cols": self.grid.cols,
            "grid": grid_values,
            "walls": walls,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Puzzle:
        rows = data["rows"]
        cols = data["cols"]
        grid = Grid(rows, cols)
        for r in range(rows):
            for c in range(cols):
                val = data["grid"][r][c]
                if val > 0:
                    grid.set_cell(r, c, val)
        for wall in data.get("walls", []):
            a, b = tuple(wall[0]), tuple(wall[1])
            grid.add_wall(a, b)
        return cls.from_grid(grid)

    @classmethod
    def from_json(cls, path: str) -> Puzzle:
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def save_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
