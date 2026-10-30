import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = None

def llm(messages, temperature=1):
    global client
    if client is None:
        client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    completion = client.chat.completions.create(        messages=messages,
        model='openai/gpt-oss-20b',
        temperature=temperature,
    )
    return completion.choices[0].message.content


class Chat:
    def __init__(self, system='You are a helpful assistant.'):
        self.messages = [{'role': 'system', 'content': system}]

    def send_message(self, message, temperature=0.8):
        """Send a message and retain the reply.

        >>> from unittest.mock import patch
        >>> with patch('chat.llm', return_value='Hello!'):
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

        >>> with patch('chat.llm', side_effect=['First reply', 'Second reply']):
        ...     chat = Chat(system='Be brief.')
        ...     first = chat.send_message('Hello', temperature=0)
        ...     second = chat.send_message('Remember me?', temperature=0)
        ...     print(first, second)
        First reply Second reply
        >>> expected = [
        ...     {'role': 'system', 'content': 'Be brief.'},
        ...     {'role': 'user', 'content': 'Hello'},
        ...     {'role': 'assistant', 'content': 'First reply'},
        ...     {'role': 'user', 'content': 'Remember me?'},
        ...     {'role': 'assistant', 'content': 'Second reply'},
        ... ]
        >>> chat.messages == expected
        True
        """
        self.messages.append({'role': 'user', 'content': message})
        reply = llm(self.messages, temperature=temperature)
        self.messages.append({'role': 'assistant', 'content': reply})
        return reply

def repl(temperature=0.8):
    """
    Run an interactive chat session.

    >>> from unittest.mock import patch
    >>> with patch('builtins.input', side_effect=['Hello', EOFError]):
    ...     with patch('chat.llm', return_value='Hi there!'):
    ...         repl(temperature=0)
    Hi there!
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=KeyboardInterrupt):
    ...     repl(temperature=0)
    <BLANKLINE>
    >>> with patch('builtins.input', side_effect=['Hello', 'How are you?', EOFError]):
    ...     with patch('chat.llm', return_value='Hi there!'):
    ...         repl(temperature=0)
    Hi there!
    Hi there!
    <BLANKLINE>
    """
    chat = Chat(system='You are a helpful assistant. You always speak like a pirate.')
    try:
        while True:
            user_input = input('chat> ')
            print(chat.send_message(user_input, temperature=temperature))
    except (KeyboardInterrupt, EOFError):
        print()



if __name__ == '__main__':
    repl()