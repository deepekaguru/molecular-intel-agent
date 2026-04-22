from agents.agent1_extractor import run as run_agent1
from agents.agent2_graph import run as run_agent2
from agents.agent3_rag import run as run_agent3

test_state = {
    "patient_id": "TCGA-BH-A0B3",
    "raw_profile": {
        "notes": "Patient has BRCA1 and TP53 mutations. ERBB2 overexpression detected. Copy number variant in MYC gene."
    },
    "mutations": [],
    "cnvs": [],
    "expression": {},
    "graph_results": [],
    "rag_evidence": "",
    "ranked_treatments": [],
    "rationale": "",
    "human_decision": "",
    "approved_drug": None,
    "outcome": None,
    "feedback_logged": False
}

state = run_agent1(test_state)
state = run_agent2(state)
state = run_agent3(state)

print("\nRAG Evidence:")
print(state['rag_evidence'])