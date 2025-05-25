from utils.utils import validate_agent_type

def get_agent_prompt(agent_type: str, candidate_details: str, company: str, job_details: str) -> str:
    """
    Retrieves the relevant prompt based on the agent_type

    Args:
        agent_type (str): Currently only supporting ['profile', 'skill', 'experience', 'supervisor'] types
        candidate_details (str): Describes the candidate's experiences etc
        company (str): Name of company
        job_details (str): Describes the relevant portion of the job details, depending on the agent_type

    Returns:
        str: Unique prompt based on the agent_type, filled with the relevant details.
    """

    if not validate_agent_type(agent_type):
        return ""
    
    with open(f"prompts/{agent_type}.txt", "r") as f:
        prompt = f.read()

    updated_prompt = prompt.format(company = company, candidate_details = candidate_details, job_details = job_details)
    return updated_prompt