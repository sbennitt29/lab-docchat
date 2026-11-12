"""Summarize a chatbot conversation and replace its history."""


def compact(chat):
    """
    Summarize the conversation and replace its history.

    >>> from unittest.mock import MagicMock, patch
    >>> chat = MagicMock()
    >>> chat.messages = [{'role': 'user', 'content': 'Hello'}]
    >>> with patch('chat.llm') as mock_llm:
    ...     mock_llm.return_value.chat.completions.create.return_value.choices[0].message.content = 'Known summary'
    ...     compact(chat)
    >>> chat.messages
    [{'role': 'system', 'content': 'Known summary'}]
    """
    from chat import llm

    messages = chat.messages + [
        {
            'role': 'user',
            'content': 'Summarize this conversation in at most five lines.'
        }
    ]

    completion = llm().chat.completions.create(
        messages=messages,
        model='openai/gpt-oss-20b'
    )

    summary = completion.choices[0].message.content

    chat.messages = [
        {'role': 'system', 'content': summary}
    ]
