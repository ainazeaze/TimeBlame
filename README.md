# time-blame

A terminal UI for browsing a file's Git history. Select any commit in the timeline and instantly see what the file looked like at that point, with syntax highlighting.

## Requirements

- Python 3.12+
- A Git repository

## Installation

```bash
cd time-blame
pip install -e .
```

## Usage

```bash
time-blame <file-path>
```

Example:

```bash
time-blame src/main.py
```

## Keybindings

| Key | Action |
|-----|--------|
| Up / Down | Navigate commits |
| Page Up / Page Down | Jump 10 commits |
| Home / End | Jump to newest / oldest commit |
| r | Reload history |
| q | Quit |

## Dependencies

- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Rich](https://github.com/Textualize/rich) - Syntax highlighting
