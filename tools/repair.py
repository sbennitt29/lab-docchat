"""Automatically repair Python files with failing doctests."""

import ast
import doctest
import subprocess
import sys
from collections import Counter
from pathlib import Path
from tools.ls import is_path_safe
import importlib.util


def get_examples(contents):
    """Extract doctest examples and expected answers from docstrings."""
    tree = ast.parse(contents)
    parser = doctest.DocTestParser()
    examples = Counter()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef,
                             ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)

            if docstring:
                for example in parser.get_examples(docstring):
                    examples[(example.source, example.want)] += 1

    return examples


def run_tests(path):
    """Run verbose doctests and return the subprocess result."""
    cache = Path(importlib.util.cache_from_source(str(path)))
    cache.unlink(missing_ok=True)

    return subprocess.run(
        [sys.executable, '-B', '-m', 'doctest', '--verbose', path],
        capture_output=True,
        text=True
    )


def repair(chat, path, max_rounds=5):
    """Attempt to repair failing doctests while preserving original tests.

    >>> repair(None, '../secret.py')
    False
    >>> repair(None, '/tmp/example.py')
    False
    """
    if not is_path_safe(path):
        return False

    file = Path(path)

    if not file.is_file():
        return False

    try:
        original_examples = get_examples(
            file.read_text(encoding='utf-8')
        )
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return False

    result = run_tests(path)

    if result.returncode == 0:
        return True

    for _ in range(max_rounds):
        previous_contents = file.read_bytes()

        report = result.stdout + result.stderr

        chat.send_message(
            f"Fix the failing doctests in {path}. "
            f"Keep all original doctests unchanged.\n\n"
            f"Failure report:\n{report}"
        )

        try:
            current_examples = get_examples(
                file.read_text(encoding='utf-8')
            )
        except (OSError, UnicodeError, SyntaxError, ValueError):
            file.write_bytes(previous_contents)
            return False

        if original_examples - current_examples:
            file.write_bytes(previous_contents)
            return False

        result = run_tests(path)

        if result.returncode == 0:
            return True

    return False
