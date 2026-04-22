from langgraph.graph import StateGraph, END
from agents.state import ClinicalState
from agents.agent1_extractor import run as run1
from agents.agent2_graph import run as run2
from agents.agent3_rag import run as run3
from agents.agent4_ranker import run as run4
from agents.agent5_rationale import run as run5

def build_graph():
    graph = StateGraph(ClinicalState)

    graph.add_node("extract", run1)
    graph.add_node("query_graph", run2)
    graph.add_node("rag", run3)
    graph.add_node("rank", run4)
    graph.add_node("rationale", run5)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "query_graph")
    graph.add_edge("query_graph", "rag")
    graph.add_edge("rag", "rank")
    graph.add_edge("rank", "rationale")
    graph.add_edge("rationale", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()

    print("\n" + "="*50)
    print("MOLECULAR INTELLIGENCE PLATFORM")
    print("Autonomous Treatment Recommendation Agent")
    print("="*50 + "\n")

    result = app.invoke({
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
    })

    print("\n" + "="*50)
    print("FINAL RECOMMENDATIONS")
    print("="*50)
    for i, t in enumerate(result['ranked_treatments']):
        print(f"{i+1}. {t['drug']} — Score: {round(t['ml_score'],3)} | Response: {t['response_rate']}")
    print("\nRATIONALE:")
    print(result['rationale'])