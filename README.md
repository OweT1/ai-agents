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
python src/gradio-app.py
```

You should now be able to access the web app!
