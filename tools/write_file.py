"""Write a single file, commit the change, and run doctests."""

from tools.write_files import write_files


def write_file(path, contents=None, commit_message=None, diff=None):
    """Write or patch one file using the shared writing function.

    >>> write_file('../secret.txt', 'hello', 'Test')
    'Error: Unsafe path.'
    >>> write_file('/tmp/example.txt', 'hello', 'Test')
    'Error: Unsafe path.'
    >>> write_file('example.txt', commit_message='Test')
    'Error: Provide either contents or diff.'
    """
    file = {'path': path}

    if contents is not None:
        file['contents'] = contents

    if diff is not None:
        file['diff'] = diff

    return write_files([file], commit_message)
