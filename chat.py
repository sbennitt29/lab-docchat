"""
Implement an interactive chatbot that communicates with Groq.
Support automatic tool calling and manual slash commands.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json
from tools.calculate import calculate
from tools.ls import ls
from tools.cat import cat
from tools.grep import grep
import sys

load_dotenv()
client = None


def llm():
    """Create and return the Groq client when it is first needed.
    >>> from unittest.mock import patch
    >>> with patch('chat.Groq') as mock_groq:
    ...     with patch('chat.client', None):
    ...         first = llm()
    ...         second = llm()
    ...         print(first is second)
    ...         print(mock_groq.call_count)
    True
    1
    """
    global client
    if client is None:
        client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    return client


tools = [{
    'type': 'function',
    'function': {
        'name': 'calculate',
        'description': 'Calculate a mathematical expression.',
        'parameters': {
            'type': 'object',
            'properties': {
                'expression': {
                    'type': 'string',
                    'description': 'The mathematical expression to calculate.'
                }
            },
            'required': ['expression']
        }
    }
},
    {
    'type': 'function',
    'function': {
        'name': 'ls',
        'description': "List files in a directory. When the user asks to list files without specifying a path, or refers to the current directory, always use '.' as the path. Do not use '/' unless explicitly requested.",
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'The path to the directory to list.'
                }
            },
            'required': []
        }
    }
},
    {
    'type': 'function',
    'function': {
        'name': 'cat',
        'description': 'Read the contents of a file.',
        'parameters': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'description': 'The path to the file to read.'
                }
            },
            'required': ['file']
        }
    }
},
    {
    'type': 'function',
    'function': {
        'name': 'grep',
        'description': 'Search for a regex pattern in files matching the given path.',
        'parameters': {
            'type': 'object',
            'properties': {
                'regex': {
                    'type': 'string',
                    'description': 'The regex pattern to search for.'
                },
                'path': {
                    'type': 'string',
                    'description': 'The path to search in.'
                }
            },
            'required': ['regex', 'path']
        }
    }
}
]


class Chat:
    """
    Manage a conversation with a language model.
    Store conversation history and execute tools requested by the model.

    >>> chat = Chat(system='Be helpful.')
    >>> chat.messages[0]['content']
    'Be helpful.'
    """

    def __init__(self, system='You are a helpful assistant.  Respond in complete sentences using plain text without Markdown formatting.'):
        '''Initialize a Chat instance with a system prompt and conversation history.'''
        self.messages = [{'role': 'system', 'content': system}]

    def send_message(self, message, temperature=0.8, debug=False):
        """Send a message and retain the reply.

        >>> from unittest.mock import patch
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.return_value.choices[0].message.content = 'Hello!'
        ...     request.return_value.choices[0].message.tool_calls = None
        ...     chat = Chat(system='Be brief.')
        ...     print(chat.send_message('Hi', temperature=0))
        Hello!
        >>> expected = [
        ...     {'role': 'system', 'content': 'Be brief.'},
        ...     {'role': 'user', 'content': 'Hi'},
        ...     {'role': 'assistant', 'content': 'Hello!'},
        ... ]
        >>> chat.messages == expected
        True
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.return_value.choices[0].message.content = 'First reply'
        ...     request.return_value.choices[0].message.tool_calls = None
        ...     chat = Chat(system='Be brief.')
        ...     first = chat.send_message('Hello', temperature=0)
        ...     request.return_value.choices[0].message.content = 'Second reply'
        ...     second = chat.send_message('Remember me?', temperature=0)
        ...     print(first, second)
        First reply Second reply
        >>> len(chat.messages)
        5
        >>> chat.messages[1]['content']
        'Hello'
        >>> chat.messages[3]['content']
        'Remember me?'
        >>> with patch('builtins.input', side_effect=['Hello', 'How are you?', EOFError]):
        ...     with patch('chat.llm') as mock_llm:
        ...         request = mock_llm.return_value.chat.completions.create
        ...         request.return_value.choices[0].message.content = 'Hi there!'
        ...         request.return_value.choices[0].message.tool_calls = None
        ...         repl(temperature=0)
        Hi there!
        Hi there!
        <BLANKLINE>
        >>> from unittest.mock import MagicMock
        >>> tool_call = MagicMock()
        >>> tool_call.function.name = 'calculate'
        >>> tool_call.function.arguments = '{"expression": "2 + 3"}'
        >>> tool_call.id = '123'
        >>> first_response = MagicMock()
        >>> first_response.choices[0].message.tool_calls = [tool_call]

        >>> second_response = MagicMock()
        >>> second_response.choices[0].message.tool_calls = None
        >>> second_response.choices[0].message.content = 'The answer is 5.'
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.side_effect = [first_response, second_response]
        ...     chat = Chat()
        ...     result = chat.send_message('What is 2 + 3?', temperature=0)
        ...     print(result)
        The answer is 5.
        >>> tool_results = [m for m in chat.messages if m['role'] == 'tool']
        >>> tool_results[0]['content']
        '5'
        >>> ls_tool_call = MagicMock()
        >>> ls_tool_call.function.name = 'ls'
        >>> ls_tool_call.function.arguments = '{"path": "."}'
        >>> ls_tool_call.id = '456'
        >>> ls_first_response = MagicMock()
        >>> ls_first_response.choices[0].message.tool_calls = [ls_tool_call]

        >>> ls_second_response = MagicMock()
        >>> ls_second_response.choices[0].message.tool_calls = None
        >>> ls_second_response.choices[0].message.content = 'Here are the files in the current directory.'
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.side_effect = [ls_first_response, ls_second_response]
        ...     chat = Chat()
        ...     result = chat.send_message('What files are in the current directory?', temperature=0)
        ...     print(result)
        Here are the files in the current directory.
        >>> tool_results = [m for m in chat.messages if m['role'] == 'tool']
        >>> tool_results[0]['content'] == str(ls('.'))
        True
        >>> cat_tool_call = MagicMock()
        >>> cat_tool_call.function.name = 'cat'
        >>> cat_tool_call.function.arguments = '{"file": "notes.txt"}'
        >>> cat_tool_call.id = '789'
        >>> cat_first_response = MagicMock()
        >>> cat_first_response.choices[0].message.tool_calls = [cat_tool_call]
        >>> cat_second_response = MagicMock()
        >>> cat_second_response.choices[0].message.tool_calls = None
        >>> cat_second_response.choices[0].message.content = 'Here are the contents of notes.txt.'
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.side_effect = [cat_first_response, cat_second_response]
        ...     chat = Chat()
        ...     result = chat.send_message('What is in notes.txt?', temperature=0)
        ...     print(result)
        Here are the contents of notes.txt.
        >>> tool_results = [m for m in chat.messages if m['role'] == 'tool']
        >>> tool_results[0]['content'] == str(cat('notes.txt'))
        True
        >>> grep_tool_call = MagicMock()
        >>> grep_tool_call.function.name = 'grep'
        >>> grep_tool_call.function.arguments = '{"regex": "def repl", "path": "chat.py"}'
        >>> grep_tool_call.id = '101'
        >>> grep_first_response = MagicMock()
        >>> grep_first_response.choices[0].message.tool_calls = [grep_tool_call]
        >>> grep_second_response = MagicMock()
        >>> grep_second_response.choices[0].message.tool_calls = None
        >>> grep_second_response.choices[0].message.content = 'Here are the lines matching the regex in chat.py.'
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.side_effect = [grep_first_response, grep_second_response]
        ...     chat = Chat()
        ...     result = chat.send_message('What lines in chat.py match the regex "def repl"?', temperature=0)
        ...     print(result)
        Here are the lines matching the regex in chat.py.
        >>> tool_results = [m for m in chat.messages if m['role'] == 'tool']
        >>> tool_results[0]['content'] == str(grep('def repl', 'chat.py'))
        True
        >>> unknown_tool_call = MagicMock()
        >>> unknown_tool_call.function.name = 'unknown_tool'
        >>> unknown_tool_call.function.arguments = '{}'
        >>> unknown_tool_call.id = '999'
        >>> unknown_first_response = MagicMock()
        >>> unknown_first_response.choices[0].message.tool_calls = [unknown_tool_call]
        >>> unknown_second_response = MagicMock()
        >>> unknown_second_response.choices[0].message.tool_calls = None
        >>> unknown_second_response.choices[0].message.content = 'Unknown tool requested.'
        >>> with patch('chat.llm') as mock_llm:
        ...     request = mock_llm.return_value.chat.completions.create
        ...     request.side_effect = [unknown_first_response, unknown_second_response]
        ...     chat = Chat()
        ...     result = chat.send_message('Use an unknown tool.', temperature=0)
        ...     print(result)
        Unknown tool requested.
        >>> tool_results = [m for m in chat.messages if m['role'] == 'tool']
        >>> tool_results[0]['content']
        'Error: Unknown tool.'
        """
        self.messages.append({'role': 'user', 'content': message})

        while True:
            completion = llm().chat.completions.create(
                messages=self.messages,
                model='openai/gpt-oss-20b',
                temperature=temperature,
                tools=tools,
                timeout=30,
            )

            assistant_message = completion.choices[0].message

            if not assistant_message.tool_calls:
                reply = assistant_message.content
                self.messages.append({'role': 'assistant', 'content': reply})
                return reply

            self.messages.append(
                assistant_message.model_dump(exclude_none=True)
            )

            for tool_call in assistant_message.tool_calls:
                arguments = json.loads(tool_call.function.arguments)

                if debug:
                    print(f"Tool: {tool_call.function.name}, Arguments: {arguments}")


                if tool_call.function.name == 'calculate':
                    result = calculate(arguments['expression'])
                elif tool_call.function.name == 'ls':
                    result = ls(arguments.get('path', '.'))
                elif tool_call.function.name == 'cat':
                    result = cat(arguments['file'])
                elif tool_call.function.name == 'grep':
                    result = grep(arguments['regex'], arguments['path'])
                else:
                    result = 'Error: Unknown tool.'

                self.messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': str(result)
                })


def repl(temperature=0.8, debug=False):
    """
    Run an interactive chat session.

    >>> from unittest.mock import patch
    >>> with patch('builtins.input', side_effect=['Hello', EOFError]):
    ...     with patch('chat.llm') as mock_llm:
    ...         request = mock_llm.return_value.chat.completions.create
    ...         request.return_value.choices[0].message.content = 'Hi there!'
    ...         request.return_value.choices[0].message.tool_calls = None
    ...         repl(temperature=0)
    Hi there!
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=KeyboardInterrupt):
    ...     repl(temperature=0)
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['Hello', 'How are you?', EOFError]):
    ...     with patch('chat.llm') as mock_llm:
    ...         request = mock_llm.return_value.chat.completions.create
    ...         request.return_value.choices[0].message.content = 'Hi there!'
    ...         request.return_value.choices[0].message.tool_calls = None
    ...         repl(temperature=0)
    ...         second_messages = request.call_args_list[1].kwargs['messages'][:4]
    ...         print([(m['role'], m['content']) for m in second_messages])
    Hi there!
    Hi there!
    <BLANKLINE>
    [('system', 'You are a helpful assistant.  Respond in complete sentences using plain text without Markdown formatting.'), ('user', 'Hello'), ('assistant', 'Hi there!'), ('user', 'How are you?')]
    >>> with patch('builtins.input', side_effect=['/calculate 2 + 3', EOFError]):
    ...     repl(temperature=0)
    5
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/ls nonexistent_directory', EOFError]):
    ...     with patch('chat.llm') as mock_llm:
    ...         request = mock_llm.return_value.chat.completions.create
    ...         repl(temperature=0)
    ...         print(request.call_count)
    []
    <BLANKLINE>
    0
    >>> with patch('builtins.input', side_effect=['/calculate 2 + 3', 'What was my calculation?', EOFError]):
    ...     with patch('chat.llm') as mock_llm:
    ...         request = mock_llm.return_value.chat.completions.create
    ...         request.return_value.choices[0].message.content = 'Your calculation was 2 + 3 = 5.'
    ...         request.return_value.choices[0].message.tool_calls = None
    ...         repl(temperature=0)
    ...         messages = request.call_args_list[0].kwargs['messages']
    ...         print(messages[2])
    5
    Your calculation was 2 + 3 = 5.
    <BLANKLINE>
    {'role': 'system', 'content': '5'}
    >>> with patch('builtins.input', side_effect=['/cat nonexistent_file.txt', EOFError]):
    ...     repl(temperature=0)
    Error: File not found.
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/grep xyz123nonexistent notes.txt', EOFError]):
    ...     repl(temperature=0)
    <BLANKLINE>
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/calculate', EOFError]):
    ...     repl(temperature=0)
    Error: No expression provided for 'calculate' command.
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/ls .', EOFError]):
    ...     with patch('chat.ls', return_value=['chat.py']) as mock_ls:
    ...         repl(temperature=0)
    ...         mock_ls.assert_called_once_with('.')
    ['chat.py']
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/cat', EOFError]):
    ...     repl(temperature=0)
    Error: No file specified for 'cat' command.
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/grep hello', EOFError]):
    ...     repl(temperature=0)
    Error: 'grep' command requires a regex and a path.
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/hello', EOFError]):
    ...     repl(temperature=0)
    Error: Unknown command '/hello'.
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['/ls', EOFError]):
    ...     with patch('chat.ls', return_value=['chat.py']) as mock_ls:
    ...         repl(temperature=0)
    ...         mock_ls.assert_called_once_with()
    ['chat.py']
    <BLANKLINE>
    >>> import runpy
    >>> with patch('sys.argv', ['chat.py']):
    ...     with patch('builtins.input', side_effect=[EOFError]):
    ...         _ = runpy.run_path('chat.py', run_name='__main__')
    <BLANKLINE>
    """
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')
            if user_input.startswith('/'):
                parts = user_input.split()
                command = parts[0][1:]
                arguments = parts[1:]
                if command == 'calculate':
                    if arguments:
                        expression = ' '.join(arguments)
                        result = calculate(expression)
                    else:
                        print("Error: No expression provided for 'calculate' command.")
                        continue
                elif command == 'ls':
                    if arguments:
                        result = ls(arguments[0])
                    else:
                        result = ls()
                elif command == 'cat':
                    if arguments:
                        result = cat(arguments[0])
                    else:
                        print("Error: No file specified for 'cat' command.")
                        continue
                elif command == 'grep':
                    if len(arguments) >= 2:
                        regex = arguments[0]
                        path = arguments[1]
                        result = grep(regex, path)
                    else:
                        print("Error: 'grep' command requires a regex and a path.")
                        continue
                else:
                    print(f"Error: Unknown command '/{command}'.")
                    continue
                chat.messages.append({
                    'role': 'user',
                    'content': user_input
                })
                chat.messages.append({
                    'role': 'system',
                    'content': str(result)
                })
                print(result)
            else:
                print(chat.send_message(user_input, temperature=temperature, debug=debug))
    except (KeyboardInterrupt, EOFError):
        print()


def main():
    """
    Run the chatbot from the command line.

    >>> from unittest.mock import patch
    >>> with patch('sys.argv', ['chat.py']), patch('chat.repl') as mock_repl:
    ...     main()
    ...     mock_repl.assert_called_once_with()
    """
    if '--debug' in sys.argv[1:]:
        repl(debug=True)
    elif len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
        chat = Chat()
        print(chat.send_message(message))
    else:
        repl()


if __name__ == '__main__':
    main()