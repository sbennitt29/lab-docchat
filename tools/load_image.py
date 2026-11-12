import base64
from pathlib import Path


def load_image(chat, path):
    """Add a local PNG image to the chat history."""

    image_path = Path(path)

    # Reject absolute paths and parent-directory references
    if image_path.is_absolute() or '..' in image_path.parts:
        raise ValueError('Image path must be relative and cannot contain ..')

    # Only accept PNG files
    if image_path.suffix.lower() != '.png':
        raise ValueError('Image must be a PNG file')

    # Read and encode the image
    image_bytes = image_path.read_bytes()
    encoded_image = base64.b64encode(image_bytes).decode('ascii')

    # Create an OpenAI-compatible image content block
    image_block = {
        'type': 'image_url',
        'image_url': {
            'url': f'data:image/png;base64,{encoded_image}'
        }
    }

    # Add the image to the conversation history
    chat.messages.append({
        'role': 'user',
        'content': [image_block]
    })