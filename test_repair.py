"""Test the automatic repair loop without contacting the model."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from tools.repair import repair


def test_repair():
    """Test successful, unsuccessful, and invalid repairs."""
    original_dir = os.getcwd()

    broken = '''def double(x):
    """
    >>> double(3)
    6
    """
    return x + 2
'''

    fixed = broken.replace('return x + 2', 'return x * 2')
    cheated = broken.replace('    6\n', '    5\n')

    with tempfile.TemporaryDirectory() as directory:
        try:
            os.chdir(directory)
            file = Path('example.py')

            # Test 1: Already passing.
            file.write_text(fixed, encoding='utf-8')
            chat = MagicMock()

            assert repair(chat, 'example.py') is True
            chat.send_message.assert_not_called()
            print('Test 1 passed: Already passing.')

            # Test 2: Successful repair.
            file.write_text(broken, encoding='utf-8')
            chat = MagicMock()
            chat.send_message.side_effect = (
                lambda message: file.write_text(fixed, encoding='utf-8')
            )

            assert repair(chat, 'example.py') is True
            assert chat.send_message.call_count == 1
            print('Test 2 passed: Successful repair.')

            # Test 3: Unsuccessful repair attempts.
            file.write_text(broken, encoding='utf-8')
            chat = MagicMock()

            assert repair(chat, 'example.py', max_rounds=3) is False
            assert chat.send_message.call_count == 3
            print('Test 3 passed: Maximum rounds respected.')

            # Test 4: Zero repair attempts.
            chat = MagicMock()

            assert repair(chat, 'example.py', max_rounds=0) is False
            chat.send_message.assert_not_called()
            print('Test 4 passed: Zero rounds.')

            # Test 5: Agent changes the expected answer.
            file.write_text(broken, encoding='utf-8')
            chat = MagicMock()
            chat.send_message.side_effect = (
                lambda message: file.write_text(cheated, encoding='utf-8')
            )

            assert repair(chat, 'example.py') is False
            assert file.read_text(encoding='utf-8') == broken
            print('Test 5 passed: Changed doctest rejected.')

        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    test_repair()
