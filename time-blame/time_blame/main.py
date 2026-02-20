"""Main entry point for Time Blame."""

import sys
from time_blame.app import run_tui


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: time-blame <file-path>")
        print("\nExample:")
        print("  time-blame src/main.py")
        sys.exit(1)

    file_path = sys.argv[1]

    # Run the TUI
    run_tui(file_path)


if __name__ == "__main__":
    main()
