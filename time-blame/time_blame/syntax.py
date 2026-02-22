"""Syntax highlighting utilities for Time Blame."""

from pathlib import Path

lexer_map = {
    # Python
    "py": "python",
    "pyw": "python",
    "pyi": "python",
    # JavaScript/TypeScript
    "js": "javascript",
    "jsx": "jsx",
    "ts": "typescript",
    "tsx": "tsx",
    "mjs": "javascript",
    # Web
    "html": "html",
    "htm": "html",
    "css": "css",
    "scss": "scss",
    "sass": "sass",
    "less": "less",
    # Config/Data
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
    "toml": "toml",
    "xml": "xml",
    "ini": "ini",
    # Shell
    "sh": "bash",
    "bash": "bash",
    "zsh": "bash",
    "fish": "fish",
    # C/C++
    "c": "c",
    "h": "c",
    "cpp": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp",
    "hxx": "cpp",
    # Other compiled
    "java": "java",
    "go": "go",
    "rs": "rust",
    "swift": "swift",
    "kt": "kotlin",
    "scala": "scala",
    # Scripting
    "rb": "ruby",
    "php": "php",
    "pl": "perl",
    "lua": "lua",
    # Markup
    "md": "markdown",
    "markdown": "markdown",
    "rst": "rst",
    "tex": "latex",
    # Database
    "sql": "sql",
    # Other
    "Makefile": "make",
    "Dockerfile": "docker",
    "gitignore": "text",
}


def detect_lexer(filename: str) -> str:
    """Detect the appropriate lexer from filename"""
    # Handle special files without extensions
    basename = Path(filename).name
    if basename in lexer_map:
        return lexer_map[basename]

    # Get extension without the dot
    ext = Path(filename).suffix.lstrip(".")
    return lexer_map.get(ext, "text")
