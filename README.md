# AI Brochure Generator

Generates a short marketing brochure (in Markdown) for a company, given its website URL. It scrapes the site's landing page, asks an LLM to pick out the most relevant links (About, Careers, etc.), scrapes those too, then asks the LLM to write a brochure from the combined content.

Works with either OpenAI or a local Ollama model — configurable, no code changes needed to switch.

## How it works

1. `scraper.py` fetches the landing page and extracts its text + all links.
2. The LLM is given the link list and picks out the relevant ones (About/Careers/Company pages), returned as JSON.
3. Each relevant link is scraped too; broken/unreachable links are skipped rather than failing the whole run.
4. All scraped content is combined into a prompt and sent to the LLM to write the brochure.
5. The result is written to `brochure.md`.

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


The generated brochure is written to `brochure.md` in the project root.
