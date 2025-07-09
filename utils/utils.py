import os
from dotenv import load_dotenv
# from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
import subprocess
from docx import Document
from pypdf import PdfReader
from langchain.agents import AgentExecutor
from langchain.prompts import HumanMessagePromptTemplate

load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
mistral_api_key = os.environ.get("MISTRAL_API_KEY", "")

# def get_anthropic_model(model: str = "claude-3-5-haiku-latest") -> ChatAnthropic:
#     """
#     Returns an Anthropic model to be used for further tasks.

#     Args:
#         model (str, optional): The name & version of the model from Anthropic. Defaults to "claude-3-5-haiku-latest".

#     Returns:
#         ChatAnthropic: Model to be used for further tasks
#     """

#     # Get list of available models from Anthropic
#     list_of_available_models = [
#         "claude-3-5-haiku-latest",
#         "claude-3-7-sonnet-latest", 
#         "claude-3-5-sonnet-latest", 
#         "claude-3-5-sonnet-20240620", 
#         "claude-3-opus-latest", 
#         "claude-3-sonnet-20240229", 
#         "claude-3-haiku-20240307"
#     ]
#     DEFAULT_MODEL = list_of_available_models[0]

#     if model not in list_of_available_models:
#         print(f"Model {model} not available. Defaulting to {DEFAULT_MODEL} instead.")
#     else:
#         print(f"Using model {model}...")
    
#     return ChatAnthropic(
#         model=model if model in list_of_available_models else DEFAULT_MODEL,
#         temperature=0,
#         timeout=None,
#         max_retries=2,
#         api_key=anthropic_api_key
#     )
    
def get_mistral_model(model: str = "mistral-small-latest") -> ChatMistralAI:
    """
    Returns an Mistral model to be used for further tasks.

    Args:
        model (str, optional): The name & version of the model from Mistral. Defaults to "mistral-small-latest".

    Returns:
        ChatMistralAI: Model to be used for further tasks
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
        print(f"Model {model} not available. Defaulting to {DEFAULT_MODEL} instead...")
    else:
        print(f"Using model {model}...")
    
    return ChatMistralAI(
        model=model if model in list_of_available_models else DEFAULT_MODEL,
        temperature=0,
        max_retries=2,
        mistral_api_key=mistral_api_key
    )

def get_available_ollama_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        header = lines[0]
        header_parts = header.split()
        model_details = lines[1:]
        
        models = []
        for model_detail in model_details:
            parts = model_detail.split('   ')
            if len(parts) == len(header_parts):
              models.append({
                  header_parts[i]: parts[i]
                  for i in range(len(parts))
              })
        return models
    except subprocess.CalledProcessError as e:
        print(f"Error executing ollama list: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_ollama_model(model: str = "mistral:latest") -> ChatOllama:
    """
    Returns a downloaded model (via Ollama) to be used for further tasks.

    Args:
        model (str, optional): The name & version of the model from Mistral. Defaults to "mistral-small-latest".

    Returns:
        ChatOllama: Model to be used for further tasks
    """
    
    list_of_available_models = [model['NAME'] for model in get_available_ollama_models()]
    
    DEFAULT_MODEL = list_of_available_models[0]

    if model not in list_of_available_models:
        print(f"Model {model} not available. Defaulting to {DEFAULT_MODEL} instead...")
    else:
        print(f"Using model {model}...")
    
    return ChatOllama(
        model=model if model in list_of_available_models else DEFAULT_MODEL,
        temperature=0,
        max_retries=2,
    )
    
def validate_agent_type(agent_type: str) -> bool:
    """
    Validates the agent_type based on our list of currently supported agent types.

    Args:
    agent_type (str): agent_type to be validated

    Returns:
    bool: True if currently supported, else False
    """

    list_of_agent_types = ['candidate', 'profile', 'skills', 'experience', 'supervisor']

    if agent_type not in list_of_agent_types:
        print(f"{agent_type} currently not supported, please choose from {list_of_agent_types}")
        return False
    return True

def parse_txt(file_path: str) -> str:
    """
    Parses the .txt file at the input file_path

    Args:
        file_path (str): File path to the desired .txt file

    Returns:
        str: File contents of the .txt file
    """
    
    with open(file_path, "r") as f:
        content = f.read()
        
    return content

def parse_docx(file_path: str) -> str:
    """
    Parses the .docx file at the input file_path

    Args:
        file_path (str): File path to the desired .docx file

    Returns:
        str: Text where each paragraph is separated by a '\n' character
    """
    
    document = Document(file_path)
    text = []
    
    for paragraph in document.paragraphs:
        cleaned_text = paragraph.text.replace("\xa0", "")
        text.append(cleaned_text)
    
    return '\n'.join(text)

def parse_pdf(file_path: str) -> str:
    """
    Parses the .pdf file at the input file_path

    Args:
        file_path (str): File path to the desired .pdf file

    Returns:
        str: File contents of the .pdf file
    """

    reader = PdfReader(file_path)
    num_pages = len(reader.pages)
    text = []

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        extracted_text = page.extract_text()
        text.append(extracted_text)
    
    return '\n\n'.join(text)