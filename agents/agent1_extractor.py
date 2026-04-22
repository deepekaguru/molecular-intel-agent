from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

from security.guardrails import validate_input, scrub_pii

def run(state):
    print("Agent 1 running — extracting genomic features...")

    raw_text = state['raw_profile'].get('notes', '')

    # Validate input
    is_valid, error = validate_input(raw_text)
    if not is_valid:
        print(f"Input validation failed: {error}")
        state['mutations'] = []
        state['cnvs'] = []
        state['expression'] = {}
        return state

    # Scrub PII before sending to LLM
    clean_text = scrub_pii(raw_text)
    state['raw_profile']['notes'] = clean_text

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)


def run(state):
    print("Agent 1 running — extracting genomic features...")

    prompt = f"""
    You are a clinical genomics AI assistant.
    Extract all gene mutations, copy number variants (CNVs),
    and expression levels from this patient profile.

    Return ONLY a JSON object with exactly these keys:
    - mutations: list of gene names with mutations
    - cnvs: list of genes with copy number variants  
    - expression: dict of gene name to expression level (float)

    Patient profile: {state['raw_profile']}

    Return only valid JSON, no extra text.
    """

    result = llm.invoke(prompt)

    try:
        extracted = json.loads(result.content)
        state['mutations'] = extracted.get('mutations', [])
        state['cnvs'] = extracted.get('cnvs', [])
        state['expression'] = extracted.get('expression', {})
    except json.JSONDecodeError:
        state['mutations'] = []
        state['cnvs'] = []
        state['expression'] = {}

    print(f"Mutations found: {state['mutations']}")
    return state