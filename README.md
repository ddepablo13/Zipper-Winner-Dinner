# Zip Solver

LinkedIn Zip Puzzle solver that reads, solves, and auto-plays daily puzzles.

## How the Zip Puzzle Works

- You're given an N x N grid with numbered waypoints (1, 2, 3...)
- Visit **every cell exactly once** in a continuous path (up/down/left/right)
- Waypoints must be visited in **numerical order** (1 before 2 before 3...)
- Some cell borders have **walls** that block movement
- The path must start at waypoint 1

## Install

```bash
pip install -e .

# For browser automation (reading from LinkedIn + auto-play):
pip install -e ".[browser]"
playwright install chromium
```

Requires Python 3.11+.

## Usage

### Solve from LinkedIn (default)

```bash
zip-solver
```

Opens a browser, navigates to the Zip puzzle page, reads the grid, solves it, and displays the solution. Log in to LinkedIn when prompted.

### Auto-play the solution

```bash
zip-solver --auto-play
```

Solves the puzzle and then clicks through the solution in the browser.

### Use a saved Chrome profile (skip login)

```bash
zip-solver --profile ~/Library/Application\ Support/Google/Chrome/Default
```

### Solve from a JSON file

```bash
zip-solver --file puzzle.json
```

### Enter a puzzle manually

```bash
zip-solver --manual
```

### Save solution to JSON

```bash
zip-solver --file puzzle.json --save solution.json
```

## JSON Puzzle Format

```json
{
  "rows": 5,
  "cols": 5,
  "grid": [
    [1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 3]
  ],
  "walls": [
    [[0, 2], [0, 3]]
  ]
}
```

- `0` = empty cell, positive numbers = waypoints
- Walls are pairs of adjacent cell coordinates `[[r1, c1], [r2, c2]]`

## Solver

Uses depth-first search with:
- **Waypoint ordering** - only visit waypoints in sequence
- **Manhattan distance pruning** - skip paths that can't reach remaining waypoints in time
- **Connectivity check** - ensure unvisited cells remain reachable (no islands)
- **Neighbor sorting** - explore cells closer to the next waypoint first

Solves typical 6x6 puzzles in under 1ms.

## Tests

```bash
python3 tests/test_solver.py
```
