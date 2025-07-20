import os
from langchain.tools import tool
from dotenv import load_dotenv
import asyncio

from crawl4ai import *
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

from tavily import TavilyClient

load_dotenv()
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# @tool
async def web_crawl(web_url: str) -> str:
  """
  Crawls the web content in the web_url

  Args:
      web_url (str): URL for the desired webpage

  Returns:
      str: Markdown content of the webpage
  """
  browser_config = BrowserConfig(verbose=True)
  
  md_generator = DefaultMarkdownGenerator(
      options={
          "ignore_links": True,
          "escape_html": False,
      }
    )
  run_config = CrawlerRunConfig(
      # Content filtering
      word_count_threshold=10,
      excluded_tags=['form', 'header'],
      exclude_external_links=True,

      # Content processing
      process_iframes=True,
      remove_overlay_elements=True,

      # Cache control
      cache_mode=CacheMode.ENABLED,  # Use cache if available
      
      # Markdown generator
      markdown_generator=md_generator
  )
  
  async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(
      url=web_url,
      config=run_config
    )
    
    return result.markdown

@tool
def tavily_search(query: str) -> str:
  """
  Performs a search using the query to get relevant information from the web.

  Args:
      query (str): Query input by user

  Returns:
      str: Information on the web that is relevant to the query.
      
  The information returned should be used to craft a meaningful and informative response to the user. 
  """
  
  print('performing tavily search on', query)
  tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
  response = tavily_client.search(query)
  
  return response