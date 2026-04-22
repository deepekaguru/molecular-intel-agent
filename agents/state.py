from typing import TypedDict, List, Optional

class ClinicalState(TypedDict):
    patient_id: str
    raw_profile: dict
    mutations: List[str]
    cnvs: List[str]
    expression: dict
    graph_results: List[dict]
    rag_evidence: str
    ranked_treatments: List[dict]
    rationale: str
    human_decision: str
    approved_drug: Optional[str]
    outcome: Optional[str]
    feedback_logged: bool