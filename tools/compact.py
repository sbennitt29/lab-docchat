def compact(chat):
    """Summarize the conversation and replace its history."""

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