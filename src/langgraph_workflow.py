import asyncio
from pydantic import BaseModel
from typing import Annotated, Sequence
from langgraph.graph import StateGraph, END

from utils.tools import web_crawl
from utils.utils import get_mistral_model, extract_json
from utils.agents import get_custom_agent

def merge_last(a, b):
  return b

def merge_dict(a, b):
  for key, val in b.items():
    a[key] = val
  return a

class EvaluationState(BaseModel):
  candidate_details: Annotated[str, merge_last]
  company_details: Annotated[str, merge_last]
  job_details: Annotated[str, merge_last]
  evaluations: Annotated[dict[str, str], merge_dict]
  improvements: Annotated[str, merge_last]

def information_node(state: EvaluationState, job_url: str, company_details: str, job_details: str, company_info_input_type: str, model):
  if company_info_input_type == "URL":
    webpage_content = asyncio.run(web_crawl(job_url))
    
    information_agent = get_custom_agent(
      model=model,
      agent_type="information",
      webpage_content=webpage_content
    )
    
    result = information_agent.invoke(
      {"content": f"Use the following webpage content to extract company and job details. Webpage Content: {webpage_content}"})
    result_json = extract_json(result['messages'][-1].content)
    print(result_json)
    
    company_details = result_json['Company_Details']
    job_details = result_json['Job_Details']
  
  updated_state = state.dict()
  updated_state["company_details"] = company_details
  updated_state["job_details"] = job_details
  
  return EvaluationState(**updated_state)
  
def experience_node(state: EvaluationState, model):
  experience_agent = get_custom_agent(
    model=model,
    agent_type="experience",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details
  )
  
  result = experience_agent.invoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["evaluations"]["experience_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
def profile_node(state: EvaluationState, model):
  profile_agent = get_custom_agent(
    model=model,
    agent_type="profile",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details
  )
  
  result = profile_agent.invoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["evaluations"]["profile_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
def skills_node(state: EvaluationState, model):
  skills_agent = get_custom_agent(
    model=model,
    agent_type="skills",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details
  )
  
  result = skills_agent.invoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["evaluations"]["skills_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
def evaluator_node(state: EvaluationState, model):
  evaluator_agent = get_custom_agent(
    model=model,
    agent_type="overall_evaluator",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details,
    evaluations=state.evaluations
  )

  result = evaluator_agent.invoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["evaluations"]["final_evaluation"] = result_extracted
  return EvaluationState(**updated_state)

def improvement_node(state: EvaluationState, model):
  improvement_agent = get_custom_agent(
    model=model,
    agent_type="improvement",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details,
    evaluations=state.evaluations
  )

  result = improvement_agent.invoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["improvements"] = result_extracted
  return EvaluationState(**updated_state)
  
def get_agent_workflow(candidate_profile, job_url, company_details, job_details, company_info_input_type):
  model = get_mistral_model()
  workflow = StateGraph(EvaluationState)
  
  # Define the nodes
  workflow.add_node("information", lambda state: information_node(state, job_url, company_details, job_details, company_info_input_type, model))
  workflow.add_node("skills", lambda state: skills_node(state, model))
  workflow.add_node("experience", lambda state: experience_node(state, model))
  workflow.add_node("profile", lambda state: profile_node(state, model))
  workflow.add_node("evaluator", lambda state: evaluator_node(state, model))
  workflow.add_node("improvement", lambda state: improvement_node(state, model))
  
  # Define the edges/connections
  workflow.set_entry_point("information")
  
  workflow.add_edge("information", "skills")
  workflow.add_edge("information", "experience")
  workflow.add_edge("information", "profile")
  
  workflow.add_edge(["skills", "experience", "profile"], "evaluator")
  workflow.add_edge("evaluator", "improvement")
  workflow.add_edge("improvement", END)
  
  app = workflow.compile()
  app.get_graph().draw_mermaid_png(output_file_path="assets/workflow.png")
  return app


# if __name__ == "__main__":
#   model = get_mistral_model()
  
#   job_url = "https://lifeattiktok.com/search/7408439668049742106"
#   webpage_content = asyncio.run(web_crawl(job_url))
#   information_agent = get_custom_agent(
#     model=model,
#     agent_type="information",
#     webpage_content=webpage_content
#   )
  
#   result = information_agent.invoke(
#     {"content": f"Use the following webpage content to extract company and job details. Webpage Content: {webpage_content}"})
  
#   result_json = extract_json(result['messages'][-1].content)
#   print(result_json)

  