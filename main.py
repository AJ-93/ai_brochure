import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from scraper import WebsiteScraper
from IPython.display import Markdown, display

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

PROMPTS_DIR = Path(__file__).parent / "prompts"

MODEL = 'gpt-5-nano'
openai = OpenAI()

WEBSITE_FOR_BROCHURE = "https://edwarddonner.com"

def load_prompt(filename: str, **kwargs) -> str:
    template = (PROMPTS_DIR / filename).read_text()
    return template.format(**kwargs)

def get_link_user_prompt(url):
    user_prompt = load_prompt("link_user_prompt.txt.j2", url=url)
    links_of_the_website = WebsiteScraper.fetch_website_links(url)
    user_prompt += "\n".join(links_of_the_website)
    return user_prompt

def select_relevant_links(url):
    print(f"Selecting relevant links for {url} by calling {MODEL}")
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system", "content": load_prompt("link_system_prompt.txt.j2")},
            {"role":"user", "content": get_link_user_prompt(url)},
        ],
        response_format={"type":"json_object"}
    )
    results = response.choices[0].message.content
    relevant_links = json.loads(results)
    print(f"Found {len(relevant_links['relevant_links'])} relevant links")
    return relevant_links

def fetch_webpage_and_relevant_links(url):
    website_content = WebsiteScraper.fetch_website_contents(url)
    relevant_links = select_relevant_links(url)
    result = f"## Landing Page:\n\n{website_content}\n## Relevant Links:\n"
    for link in relevant_links['relevant_links']:
        result += f"\n\n### Link: {link['type']}\n"
        result += WebsiteScraper.fetch_website_contents(link['url'])
    return result

def get_brochure_user_prompt(company_name, url):
    user_prompt = load_prompt("brochure_user_prompt.txt.j2", company_name=company_name)
    user_prompt += fetch_webpage_and_relevant_links(url)
    user_prompt = user_prompt[:5_000]
    return user_prompt

def create_brochure(company_name, url):
    brochure_user_prompt = get_brochure_user_prompt(company_name, url)
    brochure_system_prompt = load_prompt("brochure_system_prompt.txt.j2")
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system", "content": brochure_system_prompt},
            {"role":"user", "content": brochure_user_prompt},
        ],
    )
    results = response.choices[0].message.content
    display(Markdown(results))


if __name__ == '__main__':

    create_brochure("HuggingFace", "https://huggingface.co")
