import openai
from typing import List, Dict, Optional

# A list of commonly used OpenAI models
SUPPORTED_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
]

# Store the client instance globally
_api_key = None
client = None

def configure_api_key(api_key: str) -> bool:
    """
    Configures the OpenAI API key and validates it.
    """
    global _api_key, client
    if not api_key:
        return False
    try:
        _api_key = api_key
        client = openai.OpenAI(api_key=_api_key)
        # Attempt a simple API call to validate the key
        client.models.list()
        return True
    except openai.AuthenticationError as e:
        print(f"OpenAI API key validation failed: {e}")
        client = None
        return False
    except Exception as e:
        print(f"An unexpected error occurred during OpenAI client configuration: {e}")
        client = None
        return False

def generate_response(
    model_name: str,
    system_prompt: str,
    conversation_history: List[Dict[str, str]]
) -> Optional[str]:
    """
    Generates a response using the specified OpenAI model.
    """
    if not client:
        return "OpenAI client is not configured. Please set your API key."

    if model_name not in SUPPORTED_MODELS:
        return f"Error: Model '{model_name}' is not in the list of supported OpenAI models."

    # The first message in the history for OpenAI should be the system prompt
    messages = [{"role": "system", "content": system_prompt}]
    # Append the rest of the conversation history
    messages.extend(conversation_history)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        return f"OpenAI API Error: {e}"
    except Exception as e:
        print(f"An unexpected error occurred while generating response from OpenAI: {e}")
        return f"An unexpected error occurred: {e}"
