"""Git operations for Time Blame."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Commit:
    """Represents a single commit."""

    hash: str
    timestamp: int
    author: str
    subject: str


class GitRepo:
    """Handles Git repository operations."""

    def __init__(self, path: Path | None = None):
        """Initialize with optional path, defaults to current directory."""
        self.path: Path = path or Path.cwd()
        self.repo_root = self._find_repo_root()

    def _find_repo_root(self) -> Path:
        """Find the Git repository root."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            raise ValueError(f"Not a git repository: {self.path}")

    def get_file_history(self, file_path: str) -> list[Commit]:
        """
        Get commit history for a specific file.

        Args:
            file_path: Path to the file (relative or absolute)

        Returns:
            List of Commit objects, newest first
        """
        # Convert to path relative to repo root
        target_path = Path(file_path)
        if target_path.is_absolute():
            try:
                target_path = target_path.relative_to(self.repo_root)
            except ValueError:
                raise ValueError(f"File {file_path} is not in repository")

        # Get commit history using git log
        # Format: hash<TAB>timestamp<TAB>author<TAB>subject
        cmd = [
            "git",
            "log",
            "--follow",
            "--pretty=format:%H%x09%ct%x09%an%x09%s",
            "--",
            str(target_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to get history for {file_path}: {e.stderr}")

        if not result.stdout.strip():
            raise ValueError(f"No history found for {file_path}")

        commits = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split("\t", 3)
            if len(parts) == 4:
                commit = Commit(
                    hash=parts[0],
                    timestamp=int(parts[1]),
                    author=parts[2],
                    subject=parts[3],
                )
                commits.append(commit)

        return commits

    def get_file_at_commit(self, commit_hash: str, file_path: str) -> str:
        """
        Get file contents at a specific commit.

        Args:
            commit_hash: The commit hash
            file_path: Path to the file (relative to repo root)

        Returns:
            File contents as string
        """
        # Ensure path is relative to repo root
        target_path = Path(file_path)
        if target_path.is_absolute():
            try:
                target_path = target_path.relative_to(self.repo_root)
            except ValueError:
                raise ValueError(f"File {file_path} is not in repository")

        cmd = ["git", "show", f"{commit_hash}:{target_path}"]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Handle special cases
            if "does not exist" in e.stderr or "exists on disk, but not in" in e.stderr:
                return "[File did not exist at this commit]"
            elif "is a binary file" in e.stderr:
                return "[Binary file - cannot display]"
            else:
                return "[Error loading file: {e.stderr}]"
