import gradio as gr
from PIL import Image
import numpy as np

from helper import (
  get_candidate_file_input,
  get_company_info_input_radio,
  get_job_listing_url_textbox,
  get_company_details_textbox,
  get_job_details_textbox,
  get_submit_button,
  get_app_workflow,
  get_status_textbox,
  get_evaluation_textbox,
  get_improvement_textbox,
  change_company_info_input,
  generate_response
)

with gr.Blocks(title="LangGraph Candidate Evaluator") as app:
  gr.Markdown("## 🧠 Candidate Evaluation App with LangGraph")
  gr.Markdown("Upload a candidate's profile and a job listing via the website URL to evaluate fit and receive improvement suggestions.")

  with gr.Row():
    with gr.Column():
      candidate_input = get_candidate_file_input()
      company_info_input_type = get_company_info_input_radio()
      job_url_input = get_job_listing_url_textbox(visible=True)
      company_details = get_company_details_textbox(visible=False)
      job_details = get_job_details_textbox(visible=False)
      
      submit_btn = get_submit_button()
      app_workflow = get_app_workflow()

    with gr.Column():
      status = get_status_textbox()
      eval_output = get_evaluation_textbox()
      improve_output = get_improvement_textbox()
  
  # Radio change
  company_info_input_type.change(fn=change_company_info_input, inputs=company_info_input_type, outputs=[job_url_input, company_details, job_details])
  # Submit Button
  submit_btn.click(
    fn=generate_response,
    inputs=[candidate_input, job_url_input, company_details, job_details, company_info_input_type],
    outputs=[status, eval_output, improve_output],
    show_progress=True
  )

if __name__ == "__main__":
  app.launch()