import os
from langchain.tools import tool
import asyncio
from crawl4ai import *
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

@tool
def get_list_of_candidate_data_files():
  """
  Returns the list of candidate data files.

  Returns:
      List: list of candidate data files
  """
  return os.listdir('data/candidates')

@tool
def get_list_of_company_job_data_files():
  """
  Returns the list of candidate data files.

  Returns:
      List: list of candidate data files
  """
  return os.listdir('data/companies')

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