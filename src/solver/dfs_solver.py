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
    rows = grid.rows
    cols = grid.cols
    total = puzzle.total_cells
    waypoints = puzzle.waypoints

    # Sorted waypoint list: [(number, (row, col)), ...]
    wp_sorted = sorted(waypoints.items())
    # Map from (row, col) -> waypoint number for quick lookup
    wp_at: dict[tuple[int, int], int] = {pos: num for num, pos in wp_sorted}

    # Precompute adjacency as flat index lists for speed
    neighbors: list[list[int]] = [[] for _ in range(total)]
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            for nr, nc in grid.get_neighbors(r, c):
                neighbors[idx].append(nr * cols + nc)

    # Flat index helpers
    def to_idx(r: int, c: int) -> int:
        return r * cols + c

    def from_idx(idx: int) -> tuple[int, int]:
        return divmod(idx, cols)

    # Convert waypoint data to flat indices
    wp_sorted_idx = [(num, to_idx(r, c)) for num, (r, c) in wp_sorted]
    wp_at_idx: dict[int, int] = {to_idx(r, c): num for (r, c), num in wp_at.items()}
    wp_positions_idx = [idx for _, idx in wp_sorted_idx]

    start_idx = wp_sorted_idx[0][1]
    path: list[int] = [start_idx]
    visited = [False] * total
    visited[start_idx] = True
    states_explored = 0
    unvisited_count = total - 1
    t0 = time.perf_counter()

    # Reusable BFS queue and seen array for connectivity check
    _bfs_queue = deque()
    _bfs_seen = [False] * total

    def is_connected(exclude: int) -> bool:
        """Check if all unvisited cells (after marking exclude) remain connected."""
        seed = -1
        target_count = unvisited_count - 1  # exclude one more cell
        if target_count <= 0:
            return True

        # Find seed: first unvisited cell that isn't excluded
        for i in range(total):
            if not visited[i] and i != exclude:
                seed = i
                break

        # BFS from seed
        queue = _bfs_queue
        seen = _bfs_seen
        queue.clear()
        queue.append(seed)
        seen[seed] = True
        reached = 1

        while queue:
            cur = queue.popleft()
            for nb in neighbors[cur]:
                if not seen[nb] and not visited[nb] and nb != exclude:
                    seen[nb] = True
                    reached += 1
                    if reached == target_count:
                        # Early exit: all reachable
                        # Clean up seen
                        for i in range(total):
                            seen[i] = False
                        return True
                    queue.append(nb)

        # Clean up seen
        for i in range(total):
            seen[i] = False
        return reached == target_count

    def dfs(pos: int, next_wp_idx: int) -> bool:
        nonlocal states_explored, unvisited_count
        states_explored += 1

        if unvisited_count == 0:
            return True

        remaining = unvisited_count

        # Manhattan feasibility: check we can reach remaining waypoints in order
        if next_wp_idx < len(wp_sorted_idx):
            dist_sum = 0
            pr, pc = from_idx(pos)
            for i in range(next_wp_idx, len(wp_sorted_idx)):
                wr, wc = from_idx(wp_sorted_idx[i][1])
                dist_sum += abs(pr - wr) + abs(pc - wc)
                pr, pc = wr, wc
            if dist_sum > remaining:
                return False

        # Sort neighbors: prefer those closer to next waypoint target
        nbrs = neighbors[pos]
        if next_wp_idx < len(wp_sorted_idx):
            target = wp_sorted_idx[next_wp_idx][1]
            tr, tc = from_idx(target)
            nbrs = sorted(nbrs, key=lambda n: abs(n // cols - tr) + abs(n % cols - tc))

        for nb in nbrs:
            if visited[nb]:
                continue

            # Waypoint ordering: if this cell has a waypoint, it must be the next one
            cell_wp = wp_at_idx.get(nb)
            if cell_wp is not None:
                if next_wp_idx >= len(wp_sorted_idx) or wp_sorted_idx[next_wp_idx][0] != cell_wp:
                    continue

            # Connectivity check (skip when only 1-2 cells remain)
            if remaining > 2 and not is_connected(nb):
                continue

            # Make move
            visited[nb] = True
            unvisited_count -= 1
            path.append(nb)
            new_wp_idx = next_wp_idx + 1 if cell_wp is not None else next_wp_idx

            if dfs(nb, new_wp_idx):
                return True

            # Undo move
            path.pop()
            visited[nb] = False
            unvisited_count += 1

        return False

    # Start DFS from waypoint 1, next waypoint to find is index 1 (waypoint 2)
    found = dfs(start_idx, 1)
    elapsed = (time.perf_counter() - t0) * 1000

    return SolveResult(
        path=[from_idx(i) for i in path] if found else None,
        elapsed_ms=elapsed,
        states_explored=states_explored,
    )
