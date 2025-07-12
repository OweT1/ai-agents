import gradio as gr
from PIL import Image
import numpy as np

from utils.utils import collapse_list_of_dict_to_dict
from helper import parse_data_file, convert_image_bytes_to_PIL, get_workflow_file_bytes, call_evaluation
from langgraph_workflow import  get_agent_workflow

def generate_response(candidate_file, job_url):
  candidate_profile = parse_data_file(candidate_file)
  response = call_evaluation(candidate_profile, job_url)
  response_evaluations = collapse_list_of_dict_to_dict(response["evaluations"])
  
  # Extract out evaluation components
  experience_evaluation = response_evaluations["experience_evaluation"]
  profile_evaluation = response_evaluations["profile_evaluation"]
  skills_evaluation = response_evaluations["skills_evaluation"]
  final_evaluation = response_evaluations["final_evaluation"]
  
  return (
    convert_image_bytes_to_PIL(get_workflow_file_bytes(get_agent_workflow(candidate_profile, job_url))), 
    experience_evaluation, 
    profile_evaluation, 
    skills_evaluation,
    final_evaluation
  )

# Inputs
candidate_details = gr.File(label="Resume", file_types=['.txt', '.pdf', '.docx'])
job_link = gr.Textbox(label="Job Link", lines=1)

# Outputs
app_workflow = gr.Image(label="App Workflow", type='pil')
experience_evaluation = gr.Textbox(label="Experience Evaluation", lines=5)
profile_evaluation = gr.Textbox(label="Profile Evaluation", lines=5)
skills_evaluation = gr.Textbox(label="Skills Evaluation", lines=5)
final_evaluation = gr.Textbox(label="Final Evaluation", lines=5)

# with gr.Blocks() as demo:
#   with gr.Column():
#     candidate_details = candidate_details
#     company_details = company_details
#     job_details = job_details
#   with gr.Column():
#     app_workflow = app_workflow
#     evaluation = evaluation

app = gr.Interface(
  fn=generate_response,
  inputs=[candidate_details, job_link],
  outputs=[app_workflow, experience_evaluation, profile_evaluation, skills_evaluation, final_evaluation],
  title="Evaluation Bot"
)

if __name__ == "__main__":
  app.launch()