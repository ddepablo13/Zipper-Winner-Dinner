from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from src.models.puzzle import Puzzle


def play_solution(page: Page, puzzle: Puzzle, path: list[tuple[int, int]]):
    """Auto-play the solution by clicking cells in order on the LinkedIn Zip page."""
    cols = puzzle.grid.cols
    cells = page.query_selector_all(".trail-grid .trail-cell")

    if not cells:
        print("Error: could not find grid cells on page")
        return

    print(f"Auto-playing solution ({len(path)} moves)...")

    # Click each cell in the path order
    for i, (r, c) in enumerate(path):
        idx = r * cols + c
        if idx < len(cells):
            cells[idx].click()
            # Small delay for UI responsiveness
            if i < len(path) - 1:
                page.wait_for_timeout(30)

    page.wait_for_timeout(500)
    print("Auto-play complete!")
