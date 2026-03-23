from __future__ import annotations
from src.models.grid import Grid
from src.models.puzzle import Puzzle


class PlaywrightReader:
    def __init__(self, headless: bool = False, profile: str | None = None):
        self.headless = headless
        self.profile = profile
        self.page = None
        self._browser = None
        self._context = None
        self._playwright = None

    def read(self) -> Puzzle:
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()

        if self.profile:
            self._context = self._playwright.chromium.launch_persistent_context(
                self.profile,
                headless=self.headless,
                channel="chrome",
            )
            self.page = self._context.pages[0] if self._context.pages else self._context.new_page()
        else:
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                channel="chrome",
            )
            self._context = self._browser.new_context()
            self.page = self._context.new_page()

        self.page.goto("https://www.linkedin.com/games/zip")

        # Wait for the game grid to appear (user may need to log in)
        print("Waiting for puzzle to load (log in to LinkedIn if needed)...")
        self.page.wait_for_selector(".trail-grid", timeout=120000)

        # Dismiss tutorial modal if present
        try:
            dismiss = self.page.query_selector(".trail-tutorial-modal button.artdeco-modal__dismiss")
            if dismiss:
                dismiss.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

        # Click start button if present
        try:
            start_btn = self.page.query_selector("#launch-footer-start-button")
            if start_btn:
                start_btn.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

        return self._extract_puzzle()

    def _extract_puzzle(self) -> Puzzle:
        grid_el = self.page.query_selector(".trail-grid")

        # Get grid dimensions from CSS custom property
        rows = self.page.evaluate(
            "el => parseInt(getComputedStyle(el).getPropertyValue('--rows')) || 0",
            grid_el,
        )
        cols = self.page.evaluate(
            "el => parseInt(getComputedStyle(el).getPropertyValue('--cols')) || 0",
            grid_el,
        )
        if rows == 0:
            rows = self.page.evaluate(
                "el => parseInt(getComputedStyle(el).getPropertyValue('--row-count')) || 0",
                grid_el,
            )
        if cols == 0:
            cols = self.page.evaluate(
                "el => parseInt(getComputedStyle(el).getPropertyValue('--col-count')) || 0",
                grid_el,
            )
        # Fallback: try to infer from number of cells
        cells = self.page.query_selector_all(".trail-grid .trail-cell")
        if rows == 0 or cols == 0:
            total = len(cells)
            # Assume square grid
            rows = cols = int(total ** 0.5)

        grid = Grid(rows, cols)

        for idx, cell_el in enumerate(cells):
            r = idx // cols
            c = idx % cols

            # Check for waypoint number
            content = self.page.evaluate(
                """el => {
                    const c = el.querySelector('.trail-cell-content');
                    return c ? c.textContent.trim() : '';
                }""",
                cell_el,
            )
            if content and content.isdigit():
                grid.set_cell(r, c, int(content))

            # Check for walls
            has_right_wall = self.page.evaluate(
                "el => !!el.querySelector('.trail-cell-wall--right')",
                cell_el,
            )
            has_down_wall = self.page.evaluate(
                "el => !!el.querySelector('.trail-cell-wall--down')",
                cell_el,
            )
            if has_right_wall and c + 1 < cols:
                grid.add_wall((r, c), (r, c + 1))
            if has_down_wall and r + 1 < rows:
                grid.add_wall((r, c), (r + 1, c))

        puzzle = Puzzle.from_grid(grid)
        if not puzzle.validate():
            raise ValueError("Failed to parse valid puzzle from LinkedIn page")

        print(f"Parsed {rows}x{cols} grid with {len(puzzle.waypoints)} waypoints")
        return puzzle

    def close(self):
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
