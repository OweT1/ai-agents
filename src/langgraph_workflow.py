import asyncio
from pydantic import BaseModel
from typing import Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
import operator
import re

from src.utils.tools import web_crawl, tavily_search
from src.utils.utils import (
  get_mistral_model,
  extract_json,
)
from src.utils.agents import get_custom_agent

# --- Helper Functions --- #
def collapse_dict_to_str(evaluation_dict: dict[str, str]):
  output = ""
  for key, val in evaluation_dict.items():
    output += f"{key}\n{val}\n"
  return output
  
def extract_score(text):
  matches = re.findall(r"Score:\s*(.+)", text)
  return matches[-1].strip() if matches else None

def extract_remarks(text):
  matches = re.findall(r"Remarks:\s*(.+)", text)
  return matches[-1].strip() if matches else None
  
def extract_curr_improvement(text):
  match = re.search(r"<improvements_for_current_job>\s*(.*?)\s*</improvements_for_current_job>", text, re.DOTALL)
  return match.group(1).strip() if match else None

def extract_similar_improvement(text):
  match = re.search(r"<improvements_for_similar_jobs>\s*(.*?)\s*</improvements_for_similar_jobs>", text, re.DOTALL) 
  return match.group(1).strip() if match else None

def merge_last(a, b):
  return b

def merge_dict(a, b):
  for key, val in b.items():
    a[key] = val
  return a
# --- Pydantic Models --- #
class EvaluationState(BaseModel):
  candidate_details: Annotated[str, merge_last]
  company_details: Annotated[str, merge_last]
  job_details: Annotated[str, merge_last]
  evaluations: Annotated[dict[str, str], merge_dict]
  improvements: Annotated[dict[str, str], merge_dict]
  messages: Annotated[list[dict[str, str]], operator.add]
  
def should_go_to_improvement(state: EvaluationState):
  if "tool_calls" in state.messages[-1]:
    return "evaluator_tools"
  else:
    return "improvement"

# --- LangGraph Nodes --- #
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
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
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
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
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
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
  updated_state["evaluations"]["skills_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
def evaluator_node(state: EvaluationState, model):
  evaluator_agent = get_custom_agent(
    model=model,
    agent_type="overall_evaluator",
    tools=[tavily_search],#, web_crawl],
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details,
    evaluations=collapse_dict_to_str(state.evaluations),
  )

  result = evaluator_agent.invoke({
    "messages": state.messages + [{"role": "human", "content": "Evaluate based on previous evaluations and the provided instructions"}]
  })
  result_extracted = result['messages'][-1].content
  final_result_extracted = result_extracted[-1]['text'] if isinstance(result_extracted, list) else result_extracted
  print(final_result_extracted)
  final_result_parsed = extract_json(final_result_extracted)
  final_evaluation_score = final_result_parsed["Score"]
  final_evaluation_remarks = final_result_parsed["Remarks"]

  updated_state = state.dict()
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
  
  updated_state["evaluations"]["final_evaluation"] = result_extracted
  updated_state["evaluations"]["final_evaluation_score"] = final_evaluation_score
  updated_state["evaluations"]["final_evaluation_remarks"] = final_evaluation_remarks
  return EvaluationState(**updated_state)
  
def improvement_node(state: EvaluationState, model):
  improvement_agent = get_custom_agent(
    model=model,
    agent_type="improvement",
    tools=[tavily_search],#, web_crawl],
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details,
    evaluations=collapse_dict_to_str(state.evaluations),
  )

  result = improvement_agent.invoke({
    "messages": state.messages + [{"role": "human", "content": "Provide Areas of improvement based on previous evaluations and the provided instructions"}]
  })
  result_extracted = result['messages'][-1].content
  final_result_extracted = result_extracted[-1]['text'] if isinstance(result_extracted, list) else result_extracted
  print(final_result_extracted)
  updated_state = state.dict()
  updated_state["messages"].append({
    "role": "assistant",
    "content": final_result_extracted
  })
  updated_state["improvements"]["current"] = extract_curr_improvement(final_result_extracted).replace("*", "")
  updated_state["improvements"]["similar"] = extract_similar_improvement(final_result_extracted).replace("*", "")
  return EvaluationState(**updated_state)

# --- LangGraph Workflow --- #
def get_agent_workflow(candidate_profile, job_url, company_details, job_details, company_info_input_type):
  model = get_mistral_model("mistral-small-latest")
  big_model = get_mistral_model()
  tools=[tavily_search]#, web_crawl]
  model_with_tools=big_model.bind_tools(tools)
  tools_node=ToolNode(tools)
  
  workflow = StateGraph(EvaluationState)
  
  # Define the nodes
  workflow.add_node("information", lambda state: information_node(state, job_url, company_details, job_details, company_info_input_type, model))
  workflow.add_node("skills", lambda state: skills_node(state, model))
  workflow.add_node("experience", lambda state: experience_node(state, model))
  workflow.add_node("profile", lambda state: profile_node(state, model))
  workflow.add_node("evaluator", lambda state: evaluator_node(state, model_with_tools))
  workflow.add_node("improvement", lambda state: improvement_node(state, model_with_tools))
  workflow.add_node("evaluator_tools", tools_node)
  workflow.add_node("improvement_tools", tools_node)
  
  # Define the edges/connections
  workflow.set_entry_point("information")
  
  workflow.add_edge("information", "skills")
  workflow.add_edge("information", "experience")
  workflow.add_edge("information", "profile")
  
  workflow.add_edge(["skills", "experience", "profile"], "evaluator")
  workflow.add_conditional_edges("evaluator", should_go_to_improvement, ["evaluator_tools", "improvement"])
  workflow.add_edge("evaluator_tools", "evaluator")
  workflow.add_edge("evaluator", "improvement")

  workflow.add_conditional_edges("improvement", tools_condition, ["improvement_tools", END])
  workflow.add_edge("improvement_tools", "improvement")
  workflow.add_edge("improvement", END)
  
  app = workflow.compile()
  app.get_graph().draw_mermaid_png(output_file_path="assets/workflow.png")
  return app
  