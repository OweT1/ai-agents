import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI

load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
mistral_api_key = os.environ.get("MISTRAL_API_KEY", "")

def get_anthropic_model(model: str = "claude-3-5-haiku-latest") -> ChatAnthropic:
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
    
def get_mistral_model(model: str = "mistral-small-latest") -> ChatMistralAI:
    """
    Returns an Mistral model to be used for further tasks.

    Args:
        model (str, optional): The name & version of the model from Mistral. Defaults to "mistral-small-latest".

    Returns:
        ChatAnthropic: Model to be used for further tasks
    """

    # Get list of available models from MistralAI - https://docs.mistral.ai/getting-started/models/models_overview/
    list_of_available_models = [
        "mistral-small-latest",
        "pixtral-12b-2409",
        "open-mistral-nemo",
        "open-codestral-mamba"
    ]
    DEFAULT_MODEL = list_of_available_models[0]

    if model not in list_of_available_models:
        print(f"Model {model} not available. Defaulting to {DEFAULT_MODEL} instead.")
    
    return ChatMistralAI(
        model=model if model in list_of_available_models else DEFAULT_MODEL,
        temperature=0,
        max_tokens=1024,
        max_retries=2,
        mistral_api_key=mistral_api_key
    )
    
def validate_agent_type(agent_type: str) -> bool:
    """
    Validates the agent_type based on our list of currently supported agent types.

    Args:
    agent_type (str): agent_type to be validated

    Returns:
    bool: True if currently supported, else False
    """

    list_of_agent_types = ['profile', 'skills', 'experience', 'supervisor']

    if agent_type not in list_of_agent_types:
        print(f"{agent_type} currently not supported, please choose from {list_of_agent_types}")
        return False
    return True