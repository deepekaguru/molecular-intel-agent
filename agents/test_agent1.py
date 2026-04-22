from agents.agent1_extractor import run

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

result = run(test_state)
print("\nMutations:", result['mutations'])
print("CNVs:", result['cnvs'])
print("Expression:", result['expression'])