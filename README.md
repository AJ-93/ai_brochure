# AI Brochure Generator

Generates a short marketing brochure (in Markdown) for a company, given its website URL. It scrapes the site's landing page, asks an LLM to pick out the most relevant links (About, Careers, etc.), scrapes those too, then asks the LLM to write a brochure from the combined content.

Works with either OpenAI or a local Ollama model — configurable, no code changes needed to switch.

## How it works

1. `scraper.py` fetches the landing page and extracts its text + all links.
2. The LLM is given the link list and picks out the relevant ones (About/Careers/Company pages), returned as JSON.
3. Each relevant link is scraped too; broken/unreachable links are skipped rather than failing the whole run.
4. All scraped content is combined into a prompt and sent to the LLM to write the brochure.
5. The result is written to `brochure.md`.

## Project structure

```
main.py                  # orchestration: prompt loading, LLM calls, brochure generation
scraper.py                # WebsiteScraper: fetches page text and links via requests + BeautifulSoup
config/llm_config.yaml    # provider config (OpenAI vs Ollama), model names, base URLs
prompts/                  # prompt templates (.txt.j2, filled with str.format())
  link_system_prompt.txt.j2
  link_user_prompt.txt.j2
  brochure_system_prompt.txt.j2
  brochure_user_prompt.txt.j2
.env.example               # template for required environment variables
brochure.md                 # output file (generated on each run)
```

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Copy `.env.example` to `.env` and fill in your OpenAI API key if you plan to use OpenAI:

```
OPENAI_API_KEY=sk-...
```

To use Ollama instead, install it and pull a model:

```bash
ollama pull llama3.2
ollama serve
```

## Configuration

Provider and model are set in `config/llm_config.yaml`:

```yaml
default_provider: openai

providers:
  openai:
    base_url: null
    api_key_env: OPENAI_API_KEY
    model: gpt-5-nano

  ollama:
    base_url: http://localhost:11434/v1
    api_key_env: null
    model: llama3.2
```

Add more providers/models by adding entries here — no code changes required.

## Usage

Edit the company name, URL, and provider at the bottom of `main.py`:

```python
if __name__ == '__main__':
    provider_config = load_provider_config("ollama")  # or "openai", or None to use default_provider
    model = provider_config["model"]
    client = OpenAI(base_url=provider_config["base_url"], api_key=provider_config["api_key"])

    create_brochure("HuggingFace", "https://huggingface.co", model, client)
```

Then run:

```bash
uv run main.py
```

The generated brochure is written to `brochure.md` in the project root.

## Notes

- Local models (e.g. Ollama's llama3.2) are more prone to hallucinating or mangling URLs than larger hosted models — the scraper silently skips any link it can't fetch rather than crashing.
- Scraped content is truncated (2,000 chars per page, 5,000 chars total for the brochure prompt) to keep prompts within reasonable size.
