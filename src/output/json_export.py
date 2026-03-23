import json
from src.models.puzzle import Puzzle
from src.solver.dfs_solver import SolveResult


def export_json(puzzle: Puzzle, result: SolveResult, path: str):
    data = puzzle.to_dict()
    data["solution"] = {
        "path": result.path,
        "elapsed_ms": result.elapsed_ms,
        "states_explored": result.states_explored,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {path}")
