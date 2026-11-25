"""Write multiple files, commit changes, and run doctests."""

import git
from pathlib import Path
from tools.ls import is_path_safe
from tools.doctests import doctests


def write_files(files, commit_message):
    """Write files, make one Git commit, and return doctest reports."""
    for file in files:
        if not is_path_safe(file['path']):
            return "Error: Unsafe path."

    repo = git.Repo('.')
    paths = []
    reports = []

    for file in files:
        path = file['path']
        contents = file['contents']

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(contents, encoding='utf-8')
        paths.append(path)

    repo.index.add(paths)
    repo.git.commit("--only", "-m", f"[docchat] {commit_message}", "--", *paths)

    for path in paths:
        if path.endswith('.py'):
            reports.append(doctests(path))

    return '\n'.join(reports)