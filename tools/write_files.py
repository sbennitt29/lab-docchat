"""Write multiple files, commit changes, and run doctests."""

import git
from pathlib import Path
from tools.ls import is_path_safe
from tools.doctests import doctests
from tools.patch import apply_patch


def write_files(files, commit_message):
    """Write files, make one Git commit, and return doctest reports.

    >>> write_files([{'path': '../secret.txt', 'contents': 'hello'}], 'Test')
    'Error: Unsafe path.'
    >>> write_files([{'path': '/tmp/example.txt', 'contents': 'hello'}], 'Test')
    'Error: Unsafe path.'
    >>> write_files([{'path': 'example.txt'}], 'Test')
    'Error: Provide either contents or diff.'
    """
    prepared = {}
    reports = []

    # Validate every entry before modifying any files.
    for file in files:
        path = file['path']

        if not is_path_safe(path):
            return "Error: Unsafe path."

        path = Path(path).as_posix()

        if path in prepared:
            return "Error: Duplicate path."

        has_contents = 'contents' in file
        has_diff = 'diff' in file

        if has_contents == has_diff:
            return "Error: Provide either contents or diff."

        target = Path(path)

        if target.is_dir():
            return "Error: Path is a directory."

        if any(parent.is_file() for parent in target.parents):
            return "Error: Invalid parent directory."

        if has_diff:
            result = apply_patch(path, file['diff'])

            if isinstance(result, str):
                return result

            prepared[path] = result

        else:
            prepared[path] = file['contents'].encode('utf-8')

    # Reject conflicting paths within the batch.
    for path in prepared:
        for parent in Path(path).parents:
            if parent.as_posix() in prepared:
                return "Error: Conflicting paths."

    # Only modify files after every entry has been validated.
    repo = git.Repo('.')
    paths = []

    for path, contents in prepared.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(contents)
        paths.append(path)

    repo.index.add(paths)
    repo.git.commit("--only", "-m", f"[docchat] {commit_message}", "--", *paths)

    for path in paths:
        if path.endswith('.py'):
            reports.append(doctests(path))

    return '\n'.join(reports)
