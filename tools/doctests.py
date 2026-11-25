"""Run doctests on a Python file."""

import subprocess
import sys
from tools.ls import is_path_safe


def doctests(path):
    """Run verbose doctests and return their output.
    
    >>> doctests('../secret.py')
    'Error: Unsafe path.'
    >>> doctests('/tmp/example.py')
    'Error: Unsafe path.'
    """
    if not is_path_safe(path):
        return "Error: Unsafe path."

    result = subprocess.run(
        [sys.executable, "-m", "doctest", "--verbose", path],
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr
