import os
from PIL import Image
import io
import gradio as gr

from utils.utils import parse_docx, parse_txt, parse_pdf
from utils.agents import get_custom_agent
from langgraph_workflow import get_agent_workflow

# --- Gradio Components --- #
def get_candidate_file_input():
  return gr.File(label="Resume", file_types=['.txt', '.pdf', '.docx'])
  
def get_company_info_input_radio():
  return gr.Radio(label="Company Info Input Type", choices = ["URL", "Text"], value="URL")  
  
def get_job_listing_url_textbox(visible):
  return gr.Textbox(label="🔗 Job Listing URL", placeholder="e.g. https://lifeattiktok.com/...", visible=visible)

def get_company_details_textbox(visible):
  return gr.Textbox(label="Company Details", placeholder="Tiktok is a leading...", lines=5, visible=visible)

def get_job_details_textbox(visible):
  return gr.Textbox(label="Job Details", placeholder="You will work as a Data Scientist Intern...", lines=5, visible=visible)

def get_submit_button():
  return gr.Button("🔍 Run Evaluation")

def get_app_workflow():
  return gr.Image(label="App Workflow", value=Image.open('assets/workflow.png'), type='pil')

def get_status_textbox():
  return gr.Textbox(label="Status", interactive=False)

def get_evaluation_textbox():
  return gr.Textbox(label="✅ Evaluation", lines=5, interactive=False)

def get_improvement_textbox():
  return gr.Textbox(label="📈 Areas for Improvement", lines=5, interactive=False)

def change_company_info_input(choice):
  if choice == "Text":
    job_url_visible=False
    company_visible=True
    job_visible=True
  else:
    job_url_visible=True
    company_visible=False
    job_visible=False  
  return (
    get_job_listing_url_textbox(job_url_visible),
    get_company_details_textbox(company_visible),
    get_job_details_textbox(job_visible)
  )

# --- Submit Button / Evaluation Functions --- #
def call_evaluation(candidate_profile, job_url, company_details, job_details, company_info_input_type):
  app = get_agent_workflow(candidate_profile, job_url, company_details, job_details, company_info_input_type)
  
  system_message = "Evaluate whether the candidate is suitable for the job at the company."
  
  result = app.invoke({
    "candidate_details": candidate_profile,
    "company_details": "",
    "job_details": "",
    "evaluations": {},
    "improvements": ""
  })
  return result

def generate_response(candidate_file, job_url, company_details, job_details, company_info_input_type):
  candidate_profile = parse_data_file(candidate_file)
  yield "🟡 Processing with LangGraph...", "", ""
  response = call_evaluation(candidate_profile, job_url, company_details, job_details, company_info_input_type)
  response_evaluations = response["evaluations"]
  
  # Extract out evaluation components
  experience_evaluation = response_evaluations["experience_evaluation"]
  profile_evaluation = response_evaluations["profile_evaluation"]
  skills_evaluation = response_evaluations["skills_evaluation"]
  final_evaluation = response_evaluations["final_evaluation"]
  improvements = response["improvements"]
  
  yield "✅ Evaluation complete!", final_evaluation, improvements

# --- Other helper Functions --- #
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