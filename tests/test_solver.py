import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.puzzle import Puzzle
from src.models.grid import Grid
from src.solver.dfs_solver import solve


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _validate_solution(puzzle: Puzzle, path: list[tuple[int, int]]):
    """Verify a solution path is valid."""
    # Must visit every cell exactly once
    assert len(path) == puzzle.total_cells, f"Path length {len(path)} != {puzzle.total_cells}"
    assert len(set(path)) == len(path), "Path has duplicate cells"

    # Must start at waypoint 1
    assert path[0] == puzzle.waypoints[1], "Path doesn't start at waypoint 1"

    # Each step must be to an adjacent cell (no walls)
    for i in range(1, len(path)):
        r1, c1 = path[i - 1]
        r2, c2 = path[i]
        assert abs(r1 - r2) + abs(c1 - c2) == 1, f"Non-adjacent step: {path[i-1]} -> {path[i]}"
        assert not puzzle.grid.has_wall((r1, c1), (r2, c2)), f"Path crosses wall: {path[i-1]} -> {path[i]}"

    # Waypoints must appear in order
    wp_positions = {pos: num for num, pos in puzzle.waypoints.items()}
    visited_wps = [(wp_positions[p], p) for p in path if p in wp_positions]
    for i in range(1, len(visited_wps)):
        assert visited_wps[i][0] > visited_wps[i - 1][0], (
            f"Waypoints out of order: {visited_wps[i-1]} before {visited_wps[i]}"
        )


def test_small_3x3():
    """Tiny 3x3 grid with 2 waypoints."""
    grid = Grid(3, 3)
    grid.set_cell(0, 0, 1)
    grid.set_cell(2, 2, 2)
    puzzle = Puzzle.from_grid(grid)
    result = solve(puzzle)
    assert result.solved
    _validate_solution(puzzle, result.path)
    print(f"3x3: {result.elapsed_ms:.1f}ms, {result.states_explored} states")


def test_6x6_fixture():
    """6x6 puzzle from fixture file."""
    puzzle = Puzzle.from_json(os.path.join(FIXTURES, "puzzle_6x6.json"))
    assert puzzle.validate()
    result = solve(puzzle)
    assert result.solved
    _validate_solution(puzzle, result.path)
    print(f"6x6: {result.elapsed_ms:.1f}ms, {result.states_explored} states")


def test_5x5_with_walls():
    """5x5 puzzle with walls."""
    puzzle = Puzzle.from_json(os.path.join(FIXTURES, "puzzle_5x5_walls.json"))
    assert puzzle.validate()
    result = solve(puzzle)
    assert result.solved
    _validate_solution(puzzle, result.path)
    print(f"5x5 walls: {result.elapsed_ms:.1f}ms, {result.states_explored} states")


def test_4x4_simple():
    """4x4 with 3 waypoints."""
    grid = Grid(4, 4)
    grid.set_cell(0, 0, 1)
    grid.set_cell(0, 3, 2)
    grid.set_cell(3, 3, 3)
    puzzle = Puzzle.from_grid(grid)
    result = solve(puzzle)
    assert result.solved
    _validate_solution(puzzle, result.path)
    print(f"4x4: {result.elapsed_ms:.1f}ms, {result.states_explored} states")


if __name__ == "__main__":
    test_small_3x3()
    test_4x4_simple()
    test_5x5_with_walls()
    test_6x6_fixture()
    print("\nAll tests passed!")
