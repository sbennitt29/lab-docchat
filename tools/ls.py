"""
Provide a tool for listing files in a directory.
"""

import glob
import os


def is_path_safe(path):
    """Check whether a path stays inside the current directory.

    >>> is_path_safe('notes.txt')
    True
    >>> is_path_safe('../secret.txt')
    False
    >>> is_path_safe('/etc')
    False
    """
    if os.path.isabs(path):
        return False
    if '..' in path.split(os.sep):
        return False
    base = os.path.realpath(os.getcwd())
    target = os.path.realpath(path)
    return os.path.commonpath([base, target]) == base


def ls(path='.'):
    """List files in a directory while preventing unsafe paths.

    >>> ls() == sorted(ls())
    True
    >>> './chat.py' in ls()
    True
    >>> ls('nonexistent_directory')
    []
    >>> ls('../')
    'Error: Unsafe path.'
    >>> ls('/etc')
    'Error: Unsafe path.'
    """
    if not is_path_safe(path):
        return "Error: Unsafe path."
    files = glob.glob(f'{path}/*')
    files = sorted(files)
    return files
