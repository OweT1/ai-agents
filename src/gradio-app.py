import gradio as gr
from PIL import Image
import numpy as np

from helper import parse_data_file, convert_image_bytes_to_PIL, get_workflow_file_bytes, call_evaluation
from langgraph_workflow import  get_agent_workflow

def generate_response(candidate_file, job_url):
  candidate_profile = parse_data_file(candidate_file)
  yield "🟡 Processing with LangGraph...", "", ""
  response = call_evaluation(candidate_profile, job_url)
  response_evaluations = response["evaluations"]
  
  # Extract out evaluation components
  experience_evaluation = response_evaluations["experience_evaluation"]
  profile_evaluation = response_evaluations["profile_evaluation"]
  skills_evaluation = response_evaluations["skills_evaluation"]
  final_evaluation = response_evaluations["final_evaluation"]
  improvements = response["improvement"]
  
  yield "✅ Evaluation complete!", final_evaluation, improvements

with gr.Blocks(title="LangGraph Candidate Evaluator") as app:
  gr.Markdown("## 🧠 Candidate Evaluation App with LangGraph")
  gr.Markdown("Upload a candidate's profile and a job listing via the website URL to evaluate fit and receive improvement suggestions.")

  with gr.Row():
    with gr.Column():
      candidate_input = gr.File(label="Resume", file_types=['.txt', '.pdf', '.docx'])
      job_url_input = gr.Textbox(label="🔗 Job Listing URL", placeholder="e.g. https://lifeattiktok.com/...")

      # workflow_img = gr.Image(label="Workflow Diagram (Optional)", type="filepath", tool=None)
      submit_btn = gr.Button("🔍 Run Evaluation")
      app_workflow = gr.Image(label="App Workflow", value=Image.open('assets/workflow.png'), type='pil')

    with gr.Column():
      status = gr.Textbox(label="Status", interactive=False)
      eval_output = gr.Textbox(label="✅ Final Evaluation", lines=5, interactive=False)
      improve_output = gr.Textbox(label="📈 Areas for Improvement", lines=5, interactive=False)

  submit_btn.click(
    fn=generate_response,
    inputs=[candidate_input, job_url_input],
    outputs=[status, eval_output, improve_output],
    show_progress=True
  )

if __name__ == "__main__":
  app.launch()
  
# Old Gradio App Implementation
# def generate_response(candidate_file, job_url):
#   candidate_profile = parse_data_file(candidate_file)
#   response = call_evaluation(candidate_profile, job_url)
#   response_evaluations = response["evaluations"]
  
#   # Extract out evaluation components
#   experience_evaluation = response_evaluations["experience_evaluation"]
#   profile_evaluation = response_evaluations["profile_evaluation"]
#   skills_evaluation = response_evaluations["skills_evaluation"]
#   final_evaluation = response_evaluations["final_evaluation"]
#   improvements = response["improvement"]
  
  # return (
  #   convert_image_bytes_to_PIL(get_workflow_file_bytes(get_agent_workflow(candidate_profile, job_url))), 
  #   experience_evaluation, 
  #   profile_evaluation, 
  #   skills_evaluation,
  #   final_evaluation,
  #   improvements
  # )

# # Inputs
# candidate_details = gr.File(label="Resume", file_types=['.txt', '.pdf', '.docx'])
# job_link = gr.Textbox(label="Job Link", lines=1)

# # Outputs
# app_workflow = gr.Image(label="App Workflow", type='pil')
# experience_evaluation = gr.Textbox(label="Experience Evaluation", lines=5)
# profile_evaluation = gr.Textbox(label="Profile Evaluation", lines=5)
# skills_evaluation = gr.Textbox(label="Skills Evaluation", lines=5)
# final_evaluation = gr.Textbox(label="Final Evaluation", lines=5)
# improvements = gr.Textbox(label="Areas for Improvement", lines=5)

# app = gr.Interface(
#   fn=generate_response,
#   inputs=[candidate_details, job_link],
#   outputs=[app_workflow, experience_evaluation, profile_evaluation, skills_evaluation, final_evaluation, improvements],
#   title="Evaluation Bot"
# )