from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from prompts.prompts import get_agent_prompt
from utils.utils import validate_agent_type

def get_custom_agent(model, agent_type: str, candidate_details: str, company: str, job_details: str, agents = []):
  """
  Creates the agent based on the agent_type, with the relevant inputs.

  Args:
    model: The model to be used for the react agent
    agent_type (str): agent_type to be used to create the appropriate agent
    candidate_details (str): Details to be input to the prompt
    company (str): Company to be input to the prompt
    job_details (str): Job Details to be input to the prompt
  
  Returns:
    Runnable: Returns the agent based on the agent_type
  """
  
  if not validate_agent_type(agent_type):
    return
  
  prompt = get_agent_prompt(
    agent_type=agent_type,
    candidate_details=candidate_details,
    company=company,
    job_details=job_details
  )
  
  if agent_type == 'supervisor':
    agent = create_supervisor(
      agents,
      model=model,
      prompt=prompt
    )
  else:
    agent = create_react_agent(
      model=model,
      name=f"{agent_type}_agent",
      prompt=prompt,
      tools=[]
    )
  
  return agent