from src.models.grid import Grid
from src.models.puzzle import Puzzle


def read_manual() -> Puzzle:
    print("=== Manual Puzzle Input ===")
    rows = int(input("Grid rows: "))
    cols = int(input("Grid cols: "))

    print(f"\nEnter {rows} rows of space-separated values (0 = empty, positive = waypoint number):")
    grid = Grid(rows, cols)
    for r in range(rows):
        line = input(f"  Row {r}: ").strip().split()
        for c, val in enumerate(line):
            v = int(val)
            if v > 0:
                grid.set_cell(r, c, v)

    print("\nEnter walls as 'r1,c1 r2,c2' (one per line, empty line to finish):")
    while True:
        line = input("  Wall: ").strip()
        if not line:
            break
        parts = line.split()
        a = tuple(int(x) for x in parts[0].split(","))
        b = tuple(int(x) for x in parts[1].split(","))
        grid.add_wall(a, b)

    puzzle = Puzzle.from_grid(grid)
    if not puzzle.validate():
        raise ValueError("Invalid puzzle: waypoints must be sequential starting from 1")
    return puzzle
