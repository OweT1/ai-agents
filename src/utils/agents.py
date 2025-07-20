from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from utils.utils import (
   get_agent_prompt,
   validate_agent_type
)

def get_custom_agent(model, agent_type: str, tools = [], agents = [], **kwargs):
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
  prompt = get_agent_prompt(agent_type=agent_type).format(**kwargs)
  
  if agent_type == 'supervisor':
    agent = create_supervisor(
      agents=agents,
      supervisor_name='supervisor_agent',
      model=model,
      prompt=prompt,
      output_mode="full_history"
    )
  else:
    agent = create_react_agent(
      model=model,
      name=f"{agent_type}_agent",
      prompt=prompt,
      tools=tools
    )
     
  return agent