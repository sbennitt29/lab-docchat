"""
Provide a tool for reading the contents of text files.
"""

from tools.ls import is_path_safe


def cat(file):
    """Read a text file while preventing access to unsafe paths.

    >>> 'def repl' in cat('chat.py')
    True
    >>> cat('nonexistent_file.txt')
    'Error: File not found.'
    >>> from unittest.mock import patch
    >>> with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', bytes([255]), 0, 1, 'invalid start byte')):
    ...     result = cat('binary_file')
    >>> result.startswith('Error:')
    True
    >>> cat('../secret.txt')
    'Error: Unsafe path.'
    >>> cat('/etc/passwd')
    'Error: Unsafe path.'
    """
    if not is_path_safe(file):
        return "Error: Unsafe path."
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {str(e)}"
