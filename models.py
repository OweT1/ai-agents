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
  
  return ChatAnthropic(
      model=model,
      temperature=0,
      max_tokens=1024,
      timeout=None,
      max_retries=2,
      api_key=anthropic_api_key
  )