# Resume Evaluator

## Set-up

### Setting up of Environment Variables

You will need an `.env` file containing some API keys. You can copy the .env file by doing

```
cp .env.template .env
```

Mainly, you will need an API key from Mistral. To do so, you will need to create an account and organisation, and get an API Key at https://console.mistral.ai/api-keys.

~~To get an API Key from Anthropic, you will need to create an account and get an API Key at https://console.anthropic.com/settings/keys.~~

### Install necessary packages

You will need to do the necessary set up. Primarily, you will need to install the required dependencies via

```
pip install -r requirements.txt
```

Additionally, we use an additional tool called `Crawl4AI` that helps to scrap data from a input URL. This tool requires an additional setup:

```
crawl4ai-setup
```

After the above steps, the setup should be good to go.

## Start up App

Primarily, you just need to start up the app by doing

```
python app.py
```

You should now be able to access the web app.

## Project Workflow

This project is about evaluating a provided resume based on the provided company & job description (via url / direct input), and providing some areas for improvement for the candidate.

The resume is evaluated based on 3 aspects

- Experience: Previous work/project experience
- Skills: Candidate's hard/technical skills
- Profile: Candidate's soft skills

The evaluation workflow looks like this:
![](assets/workflow.png)

The above workflow is built using LangGraph. A brief breakdown of the workflow:

- Information: Node to ingest the provided company & job description. If a URL is provided, we will crawl the URL to get the webpage content, and utilise a LLM to extract out the company & job description.
- Experience, Profile, Skills: Nodes to evaluate the resume based on the company & job description.
- Evaluator: Node to take in all the individual evaluations and form an overall evaluation of the candidate. It will also factor in the company's prestige.
- Improvement: Node to take in all the individual and overall evaluations and identify the areas for improvement. It will look for general areas for improvement that the candidate could consider for similar job roles from different companies
- Evaluator/Improvement Tools: Node to call whenever the Evaluator/Improvement node needs to call any tools. Currently, only a search tool (`tavily_search`) is included in the nodes for usage by the respective nodes.
