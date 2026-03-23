from src.models.puzzle import Puzzle
from src.solver.dfs_solver import SolveResult


# ANSI color codes
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def display_solution(puzzle: Puzzle, result: SolveResult):
    if not result.solved:
        print(f"\n{BOLD}No solution found.{RESET}")
        print(f"  States explored: {result.states_explored}")
        print(f"  Time: {result.elapsed_ms:.1f}ms")
        return

    path = result.path
    grid = puzzle.grid

    # Build step map: (row, col) -> step number (1-indexed)
    step_map: dict[tuple[int, int], int] = {}
    for i, pos in enumerate(path):
        step_map[pos] = i + 1

    # Waypoint positions for highlighting
    wp_positions = set(puzzle.waypoints.values())

    print(f"\n{BOLD}{GREEN}Solution found!{RESET}")
    print(f"  Time: {result.elapsed_ms:.1f}ms | States explored: {result.states_explored}")
    print()

    # Determine cell width
    max_num = puzzle.total_cells
    cell_width = len(str(max_num)) + 2

    # Print grid
    h_sep = "+" + (("-" * cell_width + "+") * grid.cols)
    for r in range(grid.rows):
        # Top border with wall-aware separators
        border = "+"
        for c in range(grid.cols):
            if r > 0 and grid.has_wall((r - 1, c), (r, c)):
                border += "=" * cell_width + "+"
            else:
                border += "-" * cell_width + "+"
        print(border)

        # Cell values
        row_str = "|"
        for c in range(grid.cols):
            step = step_map.get((r, c), 0)
            num_str = str(step).center(cell_width)
            if (r, c) in wp_positions:
                num_str = f"{BOLD}{CYAN}{num_str}{RESET}"
            wall_right = c < grid.cols - 1 and grid.has_wall((r, c), (r, c + 1))
            row_str += num_str + ("‖" if wall_right else "|")
        print(row_str)

    # Bottom border
    border = "+"
    for c in range(grid.cols):
        border += "-" * cell_width + "+"
    print(border)

    # Legend
    print(f"\n  {BOLD}{CYAN}Highlighted{RESET} = waypoint cells")
