"""
Provide a tool for searching text files using regular expressions.
"""

import glob
import os
import re

from tools.ls import is_path_safe


def grep(regex, path):
    """Search files for lines matching a regular expression.

    >>> 'def repl' in grep('def repl', 'chat.py')
    True
    >>> 'def repl' in grep('def repl', '*.py')
    True
    >>> grep('xyz123nonexistent', 'nonexistent_file.txt')
    ''
    >>> grep('hello', '../secret.txt')
    'Error: Unsafe path.'
    >>> grep('hello', '/etc/passwd')
    'Error: Unsafe path.'
    >>> from unittest.mock import patch
    >>> with patch('glob.glob', return_value=['../secret.txt']):
    ...     grep('hello', '*.txt')
    ''
    >>> with patch('builtins.open', side_effect=PermissionError('Access denied')):
    ...     grep('hello', 'chat.py')
    'Error reading chat.py: Access denied'
    """
    if not is_path_safe(path):
        return "Error: Unsafe path."

    files = glob.glob(path)
    matches = []

    for file in files:
        if not is_path_safe(file):
            continue

        if os.path.isfile(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if re.search(regex, line):
                            matches.append(f"{file}: {line.strip()}")
            except Exception as e:
                return f"Error reading {file}: {e}"

    return '\n'.join(matches)
