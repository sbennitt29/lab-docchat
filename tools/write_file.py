"""Write a single file, commit the change, and run doctests."""

from tools.write_files import write_files


def write_file(path, contents, commit_message):
    """Write one file using the shared writing function."""
    return write_files(
        [{'path': path, 'contents': contents}],
        commit_message
    )