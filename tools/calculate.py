'''
Provide a calculator tool for evaluating mathematical expressions.
'''

import re


def calculate(expression: str) -> str:
    '''Evaluate a mathematical expression and return the result.

    >>> calculate('2 + 3')
    '5'
    >>> calculate('2 + 3 * (4 - 1)')
    '11'
    >>> calculate('10/0')
    'Error: division by zero'
    >>> calculate('hello')
    'Error: Invalid characters in expression.'
    '''
    if bool(re.fullmatch(r'[0-9 +/*().-]+', expression)) is False:
        return "Error: Invalid characters in expression."
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
