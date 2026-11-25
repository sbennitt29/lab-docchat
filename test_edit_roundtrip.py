"""Test a model-requested file edit without contacting the model."""

import json
import os
import tempfile
import git
from unittest.mock import MagicMock, patch
from chat import Chat


def test_edit_roundtrip():
    """Verify that a model-requested write executes and returns its result."""
    original_dir = os.getcwd()

    with tempfile.TemporaryDirectory() as directory:
        try:
            os.chdir(directory)
            git.Repo.init('.')

            tool_call = MagicMock()
            tool_call.function.name = 'write_file'
            tool_call.function.arguments = json.dumps({
                'path': 'example.txt',
                'contents': 'Hello world!',
                'commit_message': 'Add example file'
            })
            tool_call.id = '123'

            first_response = MagicMock()
            first_response.choices[0].message.tool_calls = [tool_call]

            second_response = MagicMock()
            second_response.choices[0].message.tool_calls = None
            second_response.choices[0].message.content = 'File created.'

            with patch('chat.llm') as mock_llm:
                request = mock_llm.return_value.chat.completions.create
                request.side_effect = [first_response, second_response]

                chat = Chat()
                reply = chat.send_message('Create example.txt.')

                assert reply == 'File created.'
                assert request.call_count == 2

                with open('example.txt', encoding='utf-8') as file:
                    assert file.read() == 'Hello world!'

                tool_results = [
                    message for message in chat.messages
                    if message['role'] == 'tool'
                ]

                assert len(tool_results) == 1
                assert tool_results[0]['tool_call_id'] == '123'
                assert tool_results[0] in request.call_args.kwargs['messages']

                repo = git.Repo('.')
                assert repo.head.commit.message.strip() == '[docchat] Add example file'

                print('Tool round trip passed!')

        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    test_edit_roundtrip()
