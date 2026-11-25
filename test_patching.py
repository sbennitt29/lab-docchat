"""Test patching tools without contacting the AI model."""

import os
import tempfile
import git
from pathlib import Path
from tools.write_file import write_file
from tools.write_files import write_files


def test_patching():
    """Test successful patches, invalid patches, and mixed batches."""
    original_dir = os.getcwd()

    with tempfile.TemporaryDirectory() as directory:
        try:
            os.chdir(directory)

            repo = git.Repo.init('.')
            repo.config_writer().set_value(
                'user', 'name', 'Test User'
            ).release()
            repo.config_writer().set_value(
                'user', 'email', 'test@example.com'
            ).release()

            notes = Path('notes.txt')
            notes.write_text('first\nold\nlast\n', encoding='utf-8')

            repo.index.add(['notes.txt'])
            repo.index.commit('Initial commit')

            # Test 1: Successful single-file patch.
            patch = (
                '--- a/notes.txt\n'
                '+++ b/notes.txt\n'
                '@@ -1,3 +1,3 @@\n'
                ' first\n'
                '-old\n'
                '+new\n'
                ' last\n'
            )

            before = repo.head.commit.hexsha

            result = write_file(
                'notes.txt',
                commit_message='Patch notes',
                diff=patch
            )

            assert result == '', result
            assert notes.read_text() == 'first\nnew\nlast\n'
            assert repo.head.commit.hexsha != before
            assert repo.head.commit.parents[0].hexsha == before
            print('Test 1 passed: Single-file patch.')

            # Test 2: Invalid patch context.
            before = repo.head.commit.hexsha
            original = notes.read_text()

            result = write_file(
                'notes.txt',
                commit_message='Invalid patch',
                diff=patch
            )

            assert result.startswith('Error:')
            assert notes.read_text() == original
            assert repo.head.commit.hexsha == before
            print('Test 2 passed: Invalid context rejected.')

            # Test 3: Mismatched filename.
            wrong_patch = patch.replace('notes.txt', 'other.txt')

            result = write_file(
                'notes.txt',
                commit_message='Wrong filename',
                diff=wrong_patch
            )

            assert result.startswith('Error:')
            assert notes.read_text() == original
            assert repo.head.commit.hexsha == before
            print('Test 3 passed: Wrong filename rejected.')

            # Test 4: Successful mixed batch.
            second_patch = (
                '--- a/notes.txt\n'
                '+++ b/notes.txt\n'
                '@@ -1,3 +1,3 @@\n'
                ' first\n'
                '-new\n'
                '+updated\n'
                ' last\n'
            )

            result = write_files([
                {'path': 'notes.txt', 'diff': second_patch},
                {'path': 'created.txt', 'contents': 'Hello\n'}
            ], 'Mixed batch')

            assert result == '', result
            assert notes.read_text() == 'first\nupdated\nlast\n'
            assert Path('created.txt').read_text() == 'Hello\n'
            assert repo.head.commit.parents[0].hexsha == before
            print('Test 4 passed: Mixed batch and single commit.')

            # Test 5: Invalid batch leaves everything unchanged.
            before = repo.head.commit.hexsha
            original = notes.read_text()

            result = write_files([
                {'path': 'notes.txt', 'contents': 'Changed\n'},
                {'path': 'should_not_exist.txt', 'contents': 'Hello'},
                {'path': 'created.txt', 'diff': patch}
            ], 'Invalid batch')

            assert result.startswith('Error:')
            assert notes.read_text() == original
            assert not Path('should_not_exist.txt').exists()
            assert Path('created.txt').read_text() == 'Hello\n'
            assert repo.head.commit.hexsha == before
            print('Test 5 passed: Invalid batch leaves files unchanged.')

            # Test 6: Multiple hunks.
            numbers = Path('numbers.txt')
            numbers.write_text(
                'one\ntwo\nthree\nfour\nfive\nsix\nseven\n',
                encoding='utf-8'
            )

            repo.index.add(['numbers.txt'])
            repo.index.commit('Add numbers')

            multi_patch = (
                '--- a/numbers.txt\n'
                '+++ b/numbers.txt\n'
                '@@ -1,3 +1,3 @@\n'
                ' one\n'
                '-two\n'
                '+TWO\n'
                ' three\n'
                '@@ -5,3 +5,3 @@\n'
                ' five\n'
                '-six\n'
                '+SIX\n'
                ' seven\n'
            )

            result = write_file(
                'numbers.txt',
                commit_message='Multiple hunks',
                diff=multi_patch
            )

            assert result == '', result
            assert numbers.read_text() == (
                'one\nTWO\nthree\nfour\nfive\nSIX\nseven\n'
            )
            print('Test 6 passed: Multiple hunks.')

            # Test 7: Python patch returns doctest report.
            python_file = Path('example.py')
            python_file.write_text(
                'def double(x):\n'
                '    """Double a number.\n'
                '    >>> double(3)\n'
                '    6\n'
                '    """\n'
                '    return x + 2\n',
                encoding='utf-8'
            )

            repo.index.add(['example.py'])
            repo.index.commit('Add Python example')

            python_patch = (
                '--- a/example.py\n'
                '+++ b/example.py\n'
                '@@ -4,3 +4,3 @@\n'
                '     6\n'
                '     """\n'
                '-    return x + 2\n'
                '+    return x * 2\n'
            )

            result = write_file(
                'example.py',
                commit_message='Fix double',
                diff=python_patch
            )

            assert 'Test passed.' in result, result
            assert 'return x * 2' in python_file.read_text()
            print('Test 7 passed: Python patch and doctest report.')

        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    test_patching()
