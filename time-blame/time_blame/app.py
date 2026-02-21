"""Textual TUI application for Time Blame."""

from datetime import datetime
from pathlib import Path

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from time_blame.git_ops import Commit, GitRepo

# Debug logging to file (since Textual captures stdout)
DEBUG_LOG = Path("/tmp/timeblame_debug.log")


def debug(msg: str):
    """Write debug message to file."""
    with open(DEBUG_LOG, "a") as f:
        f.write(f"{msg}\n")


class CommitListItem(ListItem):
    """A list item representing a commit."""

    def __init__(self, commit: Commit) -> None:
        self.commit = commit
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create the commit list item display."""
        short_hash = self.commit.hash[:7]
        date = datetime.fromtimestamp(self.commit.timestamp).strftime("%Y-%m-%d")
        author = self.commit.author

        # Format: hash  date  subject
        label_text = f"{short_hash} {author}  {date}  {self.commit.subject}"
        yield Label(label_text)


class CommitTimeline(ListView):
    """Timeline of commits for the selected file."""

    def __init__(self) -> None:
        super().__init__()


class FileViewer(Static):
    """Displays file contents at selected commit."""

    def __init__(self) -> None:
        super().__init__()
        self.current_content = ""

    def update_content(self, content: str, filename: str = "") -> None:
        """Update the displayed content."""
        self.current_content = content

        # Use Rich syntax highlighting if possible
        if content.startswith("[") and content.endswith("]"):
            # Error or special message
            self.update(content)
        else:
            # Try to syntax highlight
            try:
                syntax = Syntax(
                    content,
                    lexer="python",  # TODO: detect from filename
                    theme="monokai",
                    line_numbers=True,
                )
                self.update(syntax)
            except Exception:
                # Fallback to plain text
                self.update(content)


class TimeBlameApp(App):
    """Main Time Blame TUI application."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #timeline-container {
        width: 35%;
        border-right: solid $accent;
    }

    #file-container {
        width: 65%;
        height: 1fr;
    }

    CommitTimeline {
        height: 1fr;
    }

    FileViewer {
        padding: 1;
    }

    ListView {
        background: $surface;
    }

    ListView > ListItem.--highlight {
        background: $accent;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "reload", "Reload"),
    ]

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.repo = GitRepo()
        self.commits: list[Commit] = []
        self.timeline: CommitTimeline | None = None
        self.file_viewer: FileViewer | None = None
        self.title = f"Time Blame: {file_path}"
        self.sub_title = "Press ↑↓ to navigate, q to quit"

    def compose(self) -> ComposeResult:
        """Create the app layout."""
        debug("COMPOSE called")
        yield Header()

        # Main horizontal split
        with Horizontal():
            # Left: Commit timeline
            with Vertical(id="timeline-container"):
                debug("Creating timeline widget")
                self.timeline = CommitTimeline()
                yield self.timeline

            # Right: File viewer
            with VerticalScroll(id="file-container"):
                debug("Creating file viewer widget")
                self.file_viewer = FileViewer()
                yield self.file_viewer

        yield Footer()
        debug("::COMPOSE done")

    def on_mount(self) -> None:
        """Load commit history when app starts."""
        debug("::ON_MOUNT called")
        debug(f"Timeline widget: {self.timeline}")
        debug(f"File viewer widget: {self.file_viewer}")

        try:
            self.commits = self.repo.get_file_history(self.file_path)
            debug(f"Loaded {len(self.commits)} commits")

            # Populate timeline
            if self.timeline is not None:
                self.timeline.clear()
                for i, commit in enumerate(self.commits):
                    debug(f"Adding commit {i}: {commit.hash[:7]}")
                    self.timeline.append(CommitListItem(commit))
                debug(f"Timeline populated with {len(self.commits)} commits")
            else:
                debug("WARNING: timeline is None!")

            # Load first commit's file content
            if self.commits and self.file_viewer is not None:
                debug(f"Loading content for first commit: {self.commits[0].hash[:7]}")
                self._load_commit_content(self.commits[0])

        except ValueError as e:
            debug(f"ERROR in on_mount: {e}")
            if self.file_viewer is not None:
                self.file_viewer.update_content(f"[Error: {e}]")

        debug("::ON_MOUNT done")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle commit selection in timeline."""
        if isinstance(event.item, CommitListItem):
            self._load_commit_content(event.item.commit)

    def _load_commit_content(self, commit: Commit) -> None:
        """Load and display file content at given commit."""
        if self.file_viewer is None:
            return

        try:
            content = self.repo.get_file_at_commit(commit.hash, self.file_path)
            self.file_viewer.update_content(content, self.file_path)
        except Exception as e:
            self.file_viewer.update_content(f"[Error loading file: {e}]")

    def action_reload(self) -> None:
        """Reload commit history."""
        self.on_mount()


def run_tui(file_path: str) -> None:
    """Run the TUI application."""
    app = TimeBlameApp(file_path)
    app.run()
