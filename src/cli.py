import argparse
import sys

from src.models.puzzle import Puzzle
from src.solver.dfs_solver import solve
from src.output.console_display import display_solution
from src.output.json_export import export_json


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Zip Puzzle Solver")

    # Input mode (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--browser", action="store_true", default=True,
                             help="Read puzzle from LinkedIn via Playwright (default)")
    input_group.add_argument("--manual", action="store_true",
                             help="Enter puzzle manually via CLI")
    input_group.add_argument("--file", type=str, metavar="FILE",
                             help="Load puzzle from JSON file")

    # Browser options
    parser.add_argument("--headless", action="store_true",
                        help="Run browser in headless mode")
    parser.add_argument("--profile", type=str,
                        help="Path to Chrome user data directory for auto-login")

    # Output options
    parser.add_argument("--auto-play", action="store_true",
                        help="Automatically play solution in browser (requires --browser)")
    parser.add_argument("--save", type=str, metavar="FILE",
                        help="Save puzzle and solution to JSON file")
    parser.add_argument("--no-display", action="store_true",
                        help="Skip console output")

    args = parser.parse_args()

    # Read puzzle
    page = None
    if args.file:
        from src.readers.json_reader import read_json
        puzzle = read_json(args.file)
    elif args.manual:
        from src.readers.manual_reader import read_manual
        puzzle = read_manual()
    else:
        from src.readers.playwright_reader import PlaywrightReader
        reader = PlaywrightReader(headless=args.headless, profile=args.profile)
        puzzle = reader.read()
        page = reader.page

    # Solve
    result = solve(puzzle)

    # Output
    if not args.no_display:
        display_solution(puzzle, result)

    if not result.solved:
        print("No solution found!")
        sys.exit(1)

    if args.save:
        export_json(puzzle, result, args.save)

    if args.auto_play:
        if page is None:
            print("Error: --auto-play requires --browser mode")
            sys.exit(1)
        from src.output.playwright_player import play_solution
        play_solution(page, puzzle, result.path)
