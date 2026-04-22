from agents.agent1_extractor import run as run1
from agents.agent2_graph import run as run2
from agents.agent3_rag import run as run3
from agents.agent4_ranker import run as run4
from agents.agent5_rationale import run as run5

test_state = {
    "patient_id": "TCGA-BH-A0B3",
    "raw_profile": {
        "notes": "Patient has BRCA1 and TP53 mutations. ERBB2 overexpression detected. Copy number variant in MYC gene."
    },
    "mutations": [], "cnvs": [], "expression": {},
    "graph_results": [], "rag_evidence": "",
    "ranked_treatments": [], "rationale": "",
    "human_decision": "", "approved_drug": None,
    "outcome": None, "feedback_logged": False
}

state = run1(test_state)
state = run2(state)
state = run3(state)
state = run4(state)
state = run5(state)

print("\nFinal Rationale:")
print(state['rationale'])