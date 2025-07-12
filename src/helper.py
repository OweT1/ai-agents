import os
from PIL import Image
import io

from utils.utils import parse_docx, parse_txt, parse_pdf
from utils.agents import get_custom_agent
from langgraph_workflow import get_agent_workflow

def parse_data_file(data_file_path):
  _, file_ext = os.path.splitext(data_file_path)
  
  if file_ext == ".docx":
    return parse_docx(data_file_path)
  elif file_ext == ".txt":
    return parse_txt(data_file_path)
  elif file_ext == ".pdf":
    return parse_pdf(data_file_path)

def get_workflow_file_bytes(workflow):
  return workflow.get_graph().draw_mermaid_png()

def convert_image_bytes_to_PIL(image_bytes):
  image_stream = io.BytesIO(image_bytes)
  pil_image = Image.open(image_stream)
  
  return pil_image

def call_evaluation(candidate_profile, job_url):
  app = get_agent_workflow(candidate_profile, job_url)
  
  system_message = "Evaluate whether the candidate is suitable for the job at the company."
  
  result = app.invoke({
    "candidate_details": candidate_profile,
    "company_details": "",
    "job_details": ""
  })
  return result
  
  # output = []
  # for step in app.stream(
  #   {
  #     "messages": [{
  #       "role": "human", 
  #       "content": system_message
  #       }]
  #   }, stream_mode="updates"
  # ):
  #   agent = list(step.keys())[0]
    
  #   if step[agent]:
  #     agent_result = step[agent]['messages'][-1]
  #     agent_output = (agent, agent_result)
  #     output.append(agent_output)
  
  # output_str = collapse_list_of_messages_to_str(output)
  # return output_str
    