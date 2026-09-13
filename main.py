import os
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from scraper import WebsiteScraper

load_dotenv(override=True)

PROMPTS_DIR = Path(__file__).parent / "prompts"
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "llm_config.yaml"

WEBSITE_FOR_BROCHURE = "https://edwarddonner.com"

scraper = WebsiteScraper()

def load_provider_config(provider: str | None = None) -> dict:
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)

    llm_provider = provider or os.getenv("LLM_PROVIDER", config["default_provider"])
    llm_settings = config["providers"][llm_provider]

    api_key_env = llm_settings.get("api_key_env")
    api_key = os.getenv(api_key_env) if api_key_env else "ollama"

    return {
        "base_url": llm_settings.get("base_url"),
        "api_key": api_key,
        "model": llm_settings.get("model"),
    }

def load_prompt(filename: str, **kwargs) -> str:
    template = (PROMPTS_DIR / filename).read_text()
    return template.format(**kwargs)

def get_link_user_prompt(url):
    user_prompt = load_prompt("link_user_prompt.txt.j2", url=url)
    links_of_the_website = scraper.fetch_website_links(url)
    user_prompt += "\n".join(links_of_the_website)
    return user_prompt

def select_relevant_links(url, model, client):
    print(f"Selecting relevant links for {url} by calling {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system", "content": (PROMPTS_DIR / "link_system_prompt.txt.j2").read_text()},
            {"role":"user", "content": get_link_user_prompt(url)},
        ],
        response_format={"type":"json_object"}
    )
    results = response.choices[0].message.content
    relevant_links = json.loads(results)
    print(f"Found {len(relevant_links['links'])} relevant links")
    return relevant_links

def fetch_webpage_and_relevant_links(url, model, client):
    website_content = scraper.fetch_website_contents(url)
    relevant_links = select_relevant_links(url, model, client)
    result = f"## Landing Page:\n\n{website_content}\n## Relevant Links:\n"
    for link in relevant_links['links']:
        content = scraper.fetch_website_contents(link["url"])
        if not content:
            continue
        result += f"\n\n### Link: {link['type']}\n"
        result += scraper.fetch_website_contents(link['url'])
    return result

def get_brochure_user_prompt(company_name, url, model, client):
    user_prompt = load_prompt("brochure_user_prompt.txt.j2", company_name=company_name)
    user_prompt += fetch_webpage_and_relevant_links(url, model, client)
    user_prompt = user_prompt[:5_000]
    return user_prompt

def create_brochure(company_name, url, model, client):
    brochure_user_prompt = get_brochure_user_prompt(company_name, url, model, client)
    brochure_system_prompt = load_prompt("brochure_system_prompt.txt.j2")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system", "content": brochure_system_prompt},
            {"role":"user", "content": brochure_user_prompt},
        ],
    )
    results = response.choices[0].message.content
    with open("brochure.md", "w") as f:
        f.write(results)


if __name__ == '__main__':
    provider_config = load_provider_config("ollama")
    model = provider_config["model"]
    client = OpenAI(
        base_url=provider_config["base_url"], api_key=provider_config["api_key"]
    )

    create_brochure("HuggingFace", "https://huggingface.co", model, client)
