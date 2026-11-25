"""Delete files matching a path or glob and commit the deletion."""

import glob
import git
from pathlib import Path
from tools.ls import is_path_safe


def rm(path):
    """Delete matching files and make one Git commit."""
    if not is_path_safe(path):
        return "Error: Unsafe path."

    files = [
        file for file in glob.glob(path, recursive=True)
        if Path(file).is_file()
    ]

    for file in files:
        if not is_path_safe(file):
            return "Error: Unsafe path."

    if not files:
        return "No matching files."

    repo = git.Repo('.')

    for file in files:
        Path(file).unlink()

    repo.git.add("-A", "--", *files)
    repo.git.commit("--only", "-m", f"[docchat] rm {path}", "--", *files)

    return '\n'.join(files)