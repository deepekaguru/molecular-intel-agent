from models.treatment_ranker import train_model, rank_treatments

model = None

def run(state):
    global model
    print("Agent 4 running — ranking treatments with XGBoost...")

    if model is None:
        model = train_model()

    ranked = rank_treatments(
        model,
        state['graph_results'],
        state['mutations']
    )

    state['ranked_treatments'] = ranked

    print("Ranked treatments:")
    for i, t in enumerate(ranked):
        print(f"  {i+1}. {t['drug']} — ML score: {t['ml_score']} | Response rate: {t['response_rate']}")

    return state