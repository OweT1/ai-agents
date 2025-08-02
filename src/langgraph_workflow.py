import asyncio
from pydantic import BaseModel, PrivateAttr
from typing import Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
import operator
import re
from langchain_mistralai import ChatMistralAI

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
  model: Annotated[ChatMistralAI, merge_last]
  
  company_info_input_type: Annotated[str, merge_last]
  job_url: Annotated[str, merge_last]
  company_details: Annotated[str, merge_last]
  job_details: Annotated[str, merge_last]
  
  candidate_details: Annotated[str, merge_last]
  evaluations: Annotated[dict[str, str], merge_dict]
  improvements: Annotated[dict[str, str], merge_dict]
  messages: Annotated[list[dict[str, str]], operator.add]
  
def should_go_to_improvement(state: EvaluationState):
  if "tool_calls" in state.messages[-1]:
    return "evaluator_tools"
  else:
    return "improvement"

# --- LangGraph Nodes --- #
async def information_node(state: EvaluationState):
  if state.company_info_input_type == "URL":
    webpage_content = await web_crawl(state.job_url)
    
    information_agent = get_custom_agent(
      model=state.model,
      agent_type="information",
      webpage_content=webpage_content
    )
    
    result = await information_agent.ainvoke(
      {"content": f"Use the following webpage content to extract company and job details. Webpage Content: {webpage_content}"}
    )
    result_json = extract_json(result['messages'][-1].content)
    print(result_json)
    
    company_details = result_json['Company_Details']
    job_details = result_json['Job_Details']
  
  updated_state = state.dict()
  updated_state["company_details"] = company_details or state.company_details
  updated_state["job_details"] = job_details or state.job_details
  
  return EvaluationState(**updated_state)
  
async def experience_node(state: EvaluationState):
  experience_agent = get_custom_agent(
    model=state.model,
    agent_type="experience",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details
  )
  result = await experience_agent.ainvoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
  updated_state["evaluations"]["experience_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
async def profile_node(state: EvaluationState):
  profile_agent = get_custom_agent(
    model=state.model,
    agent_type="profile",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details
  )
  
  result = await profile_agent.ainvoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
  updated_state["evaluations"]["profile_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
async def skills_node(state: EvaluationState):
  skills_agent = get_custom_agent(
    model=state.model,
    agent_type="skills",
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details
  )
  
  result = await skills_agent.ainvoke(state.dict())
  result_extracted = result['messages'][-1].content
  
  updated_state = state.dict()
  updated_state["messages"].append({
    "role": "assistant",
    "content": result_extracted
  })
  updated_state["evaluations"]["skills_evaluation"] = result_extracted
  return EvaluationState(**updated_state)
  
async def evaluator_node(state: EvaluationState):  
  evaluator_agent = get_custom_agent(
    model=state.model,
    agent_type="overall_evaluator",
    tools=[tavily_search],#, web_crawl],
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details,
    evaluations=collapse_dict_to_str(state.evaluations),
  )

  result = await evaluator_agent.ainvoke({
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
  
async def improvement_node(state: EvaluationState):
  improvement_agent = get_custom_agent(
    model=state.model,
    agent_type="improvement",
    tools=[tavily_search],#, web_crawl],
    candidate_details=state.candidate_details,
    company_details=state.company_details,
    job_details=state.job_details,
    evaluations=collapse_dict_to_str(state.evaluations),
  )

  result = await improvement_agent.ainvoke({
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
async def get_agent_workflow(tools):
  tools_node=ToolNode(tools)
  
  workflow = StateGraph(EvaluationState)
  
  # Define the nodes
  workflow.add_node("information", information_node)
  workflow.add_node("skills", skills_node)
  workflow.add_node("experience", experience_node)
  workflow.add_node("profile", profile_node)
  workflow.add_node("evaluator", evaluator_node)
  workflow.add_node("improvement", improvement_node)
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
  