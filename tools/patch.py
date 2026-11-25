"""Validate unified diffs and prepare patched file contents."""

import subprocess
import tempfile
from pathlib import Path
from tools.ls import is_path_safe


def apply_patch(path, diff):
    """Return patched file contents without modifying the original file.

    >>> apply_patch('../secret.txt', '')
    'Error: Unsafe path.'
    >>> apply_patch('/tmp/example.txt', '')
    'Error: Unsafe path.'
    >>> apply_patch('nonexistent_file.txt', '')
    'Error: File does not exist.'
    """
    if not is_path_safe(path):
        return "Error: Unsafe path."

    if not Path(path).is_file():
        return "Error: File does not exist."

    path = Path(path).as_posix()
    lines = diff.splitlines()

    # Find the headers before the first hunk.
    headers = []
    for line in lines:
        if line.startswith('@@ '):
            break
        headers.append(line)

    old_headers = [
        line for line in headers if line.startswith('--- ')
    ]
    new_headers = [
        line for line in headers if line.startswith('+++ ')
    ]

    if old_headers != [f'--- a/{path}']:
        return "Error: Patch filename does not match."

    if new_headers != [f'+++ b/{path}']:
        return "Error: Patch filename does not match."

    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(path).read_bytes())

        # Ensure the original file is UTF-8 text.
        try:
            target.read_bytes().decode('utf-8')
        except UnicodeError:
            return "Error: File is not UTF-8 text."

        # Verify that the diff affects exactly one requested file.
        result = subprocess.run(
            ['git', 'apply', '--numstat', '-z'],
            input=diff.encode('utf-8'),
            capture_output=True,
            cwd=directory
        )

        entries = result.stdout.rstrip(b'\0').split(b'\0')

        if result.returncode != 0 or len(entries) != 1:
            return "Error: Invalid patch."

        fields = entries[0].split(b'\t', 2)

        if len(fields) != 3 or fields[2] != path.encode('utf-8'):
            return "Error: Patch filename does not match."

        # Reject file creation, deletion, renaming, and mode changes.
        result = subprocess.run(
            ['git', 'apply', '--summary'],
            input=diff.encode('utf-8'),
            capture_output=True,
            cwd=directory
        )

        if result.returncode != 0 or result.stdout.strip():
            return "Error: Unsupported patch."

        # Check whether the patch applies.
        result = subprocess.run(
            ['git', 'apply', '--check'],
            input=diff.encode('utf-8'),
            capture_output=True,
            cwd=directory
        )

        if result.returncode != 0:
            return "Error: Patch does not apply."

        # Apply the patch to the temporary copy.
        result = subprocess.run(
            ['git', 'apply', '--whitespace=nowarn'],
            input=diff.encode('utf-8'),
            capture_output=True,
            cwd=directory
        )

        if result.returncode != 0 or not target.is_file():
            return "Error: Patch failed."

        return target.read_bytes()
