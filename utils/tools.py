import os
from langchain.tools import tool

@tool
def get_list_of_candidate_data_files():
  """
  Returns the list of candidate data files.

  Returns:
      List: list of candidate data files
  """
  return os.listdir('data/candidates')

def get_candidate_data(name: str) -> str:
  return ""

def get_company_data(company_name: str, role_name: str) -> str:
  return ""