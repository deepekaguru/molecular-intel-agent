from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


def run(state):
    print("Agent 5 running — generating clinical rationale...")

    treatments = state['ranked_treatments'][:3]
    evidence = state['rag_evidence']
    mutations = state['mutations']

    prompt = f"""
    You are a clinical oncology AI assistant.

    Patient mutations: {mutations}

    Top ranked treatments:
    {treatments}

    Supporting literature evidence:
    {evidence}

    For each treatment, write exactly 2 sentences of
    clinical rationale explaining why it is recommended
    for this patient based on their mutations and the evidence.

    Format your response as:
    1. [Drug name]: [2 sentence rationale]
    2. [Drug name]: [2 sentence rationale]
    3. [Drug name]: [2 sentence rationale]
    """

    result = llm.invoke(prompt)
    state['rationale'] = result.content
    print("Rationale generated.")
    print(state['rationale'])
    return state