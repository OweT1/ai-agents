import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

def get_anthropic_model(
    model: str = "claude-3-5-haiku-latest"
    ) -> ChatAnthropic:
    """
    Returns an Anthropic model to be used for further tasks.

    Args:
        model (str, optional): The name & version of the model from Anthropic. Defaults to "claude-3-5-haiku-latest".

    Returns:
        ChatAnthropic: Model to be used for further tasks
    """

    # Get list of available models from Anthropic
    list_of_available_models = [
        "claude-3-5-haiku-latest",
        "claude-3-7-sonnet-latest", 
        "claude-3-5-sonnet-latest", 
        "claude-3-5-sonnet-20240620", 
        "claude-3-opus-latest", 
        "claude-3-sonnet-20240229", 
        "claude-3-haiku-20240307"
    ]
    DEFAULT_MODEL = list_of_available_models[0]

    if model not in list_of_available_models:
        print(f"Model {model} not available. Defaulting to {DEFAULT_MODEL} instead.")
    
    return ChatAnthropic(
        model=model if model in list_of_available_models else DEFAULT_MODEL,
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=2,
        api_key=anthropic_api_key
    )