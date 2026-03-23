from __future__ import annotations
import time
from collections import deque
from src.models.puzzle import Puzzle


class SolveResult:
    def __init__(self, path: list[tuple[int, int]] | None, elapsed_ms: float, states_explored: int):
        self.path = path
        self.elapsed_ms = elapsed_ms
        self.states_explored = states_explored

    @property
    def solved(self) -> bool:
        return self.path is not None


def solve(puzzle: Puzzle) -> SolveResult:
    grid = puzzle.grid
    total = puzzle.total_cells
    waypoints = puzzle.waypoints

    # Sorted waypoint list: [(number, (row, col)), ...]
    wp_sorted = sorted(waypoints.items())
    # Map from (row, col) -> waypoint number for quick lookup
    wp_at: dict[tuple[int, int], int] = {pos: num for num, pos in wp_sorted}
    # Next waypoint index lookup: after reaching waypoint N, next is wp_sorted[index]
    wp_index_of: dict[int, int] = {num: i for i, (num, _) in enumerate(wp_sorted)}

    # Precompute adjacency
    neighbors: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(grid.rows):
        for c in range(grid.cols):
            neighbors[(r, c)] = grid.get_neighbors(r, c)

    start = wp_sorted[0][1]  # position of waypoint 1
    path: list[tuple[int, int]] = [start]
    visited = [[False] * grid.cols for _ in range(grid.rows)]
    visited[start[0]][start[1]] = True
    states_explored = 0
    t0 = time.perf_counter()

    def is_connected(exclude_r: int, exclude_c: int) -> bool:
        """Check if all unvisited cells (after marking exclude) remain connected."""
        # Find first unvisited cell that isn't the excluded one
        seed = None
        unvisited_count = 0
        for r in range(grid.rows):
            for c in range(grid.cols):
                if not visited[r][c] and not (r == exclude_r and c == exclude_c):
                    unvisited_count += 1
                    if seed is None:
                        seed = (r, c)
        if unvisited_count == 0:
            return True
        # BFS from seed
        queue = deque([seed])
        reached = 1
        seen = [[False] * grid.cols for _ in range(grid.rows)]
        seen[seed[0]][seed[1]] = True
        while queue:
            cr, cc = queue.popleft()
            for nr, nc in neighbors[(cr, cc)]:
                if not seen[nr][nc] and not visited[nr][nc] and not (nr == exclude_r and nc == exclude_c):
                    seen[nr][nc] = True
                    reached += 1
                    queue.append((nr, nc))
        return reached == unvisited_count

    def dfs(pos: tuple[int, int], next_wp_idx: int) -> bool:
        nonlocal states_explored
        states_explored += 1

        if len(path) == total:
            return True

        remaining = total - len(path)
        # Manhattan feasibility: check we can reach remaining waypoints in order
        if next_wp_idx < len(wp_sorted):
            dist_sum = 0
            prev = pos
            for i in range(next_wp_idx, len(wp_sorted)):
                wp_pos = wp_sorted[i][1]
                dist_sum += abs(prev[0] - wp_pos[0]) + abs(prev[1] - wp_pos[1])
                prev = wp_pos
            if dist_sum > remaining:
                return False

        # Sort neighbors: prefer those closer to next waypoint
        nbrs = neighbors[pos]
        if next_wp_idx < len(wp_sorted):
            target = wp_sorted[next_wp_idx][1]
            nbrs = sorted(nbrs, key=lambda n: abs(n[0] - target[0]) + abs(n[1] - target[1]))

        for nr, nc in nbrs:
            if visited[nr][nc]:
                continue

            # Waypoint ordering: if this cell has a waypoint, it must be the next one
            cell_wp = wp_at.get((nr, nc))
            if cell_wp is not None:
                if next_wp_idx >= len(wp_sorted) or wp_sorted[next_wp_idx][0] != cell_wp:
                    continue

            # Connectivity check
            if remaining > 2 and not is_connected(nr, nc):
                continue

            # Make move
            visited[nr][nc] = True
            path.append((nr, nc))
            new_wp_idx = next_wp_idx + 1 if cell_wp is not None else next_wp_idx

            if dfs((nr, nc), new_wp_idx):
                return True

            # Undo move
            path.pop()
            visited[nr][nc] = False

        return False

    # Start DFS from waypoint 1, next waypoint to find is index 1 (waypoint 2)
    found = dfs(start, 1)
    elapsed = (time.perf_counter() - t0) * 1000

    return SolveResult(
        path=list(path) if found else None,
        elapsed_ms=elapsed,
        states_explored=states_explored,
    )
