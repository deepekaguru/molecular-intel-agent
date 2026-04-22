import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import mlflow

_model = None

def _generate_training_data():
    np.random.seed(42)
    n = 500
    data = pd.DataFrame({
        'has_brca1': np.random.randint(0, 2, n),
        'has_tp53': np.random.randint(0, 2, n),
        'has_erbb2': np.random.randint(0, 2, n),
        'has_myc_cnv': np.random.randint(0, 2, n),
        'response_rate': np.random.uniform(0.3, 0.9, n),
        'patient_age': np.random.randint(30, 80, n),
        'prior_treatments': np.random.randint(0, 5, n),
    })
    data['responded'] = (
        (data['has_brca1'] * 0.4) +
        (data['has_erbb2'] * 0.3) +
        (data['response_rate'] * 0.8) +
        np.random.normal(0, 0.1, n)
    ) > 0.6
    data['responded'] = data['responded'].astype(int)
    return data

def _train_model():
    print("Training XGBoost treatment ranking model...")
    data = _generate_training_data()
    features = [
        'has_brca1', 'has_tp53', 'has_erbb2',
        'has_myc_cnv', 'response_rate',
        'patient_age', 'prior_treatments'
    ]
    X = data[features]
    y = data['responded']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        eval_metric='logloss',
        random_state=42
    )
    with mlflow.start_run():
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, preds)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("auc", round(auc, 4))
        print(f"Model trained — AUC: {round(auc, 4)}")
    return model

def run(state):
    global _model
    print("Agent 4 running — ranking treatments with XGBoost...")

    if _model is None:
        _model = _train_model()

    ranked = []
    for r in state['graph_results']:
        features = pd.DataFrame([{
            'has_brca1': 1 if 'BRCA1' in state['mutations'] else 0,
            'has_tp53': 1 if 'TP53' in state['mutations'] else 0,
            'has_erbb2': 1 if 'ERBB2' in state['mutations'] else 0,
            'has_myc_cnv': 1 if 'MYC' in state['mutations'] else 0,
            'response_rate': r['response_rate'],
            'patient_age': 55,
            'prior_treatments': 1,
        }])
        score = _model.predict_proba(features)[0][1]
        ranked.append({
            'drug': r['drug'],
            'gene': r['gene'],
            'response_rate': r['response_rate'],
            'ml_score': round(score, 4)
        })

    ranked.sort(key=lambda x: x['ml_score'], reverse=True)
    state['ranked_treatments'] = ranked

    print("Ranked treatments:")
    for i, t in enumerate(ranked):
        print(f"  {i+1}. {t['drug']} — ML score: {t['ml_score']} | Response rate: {t['response_rate']}")

    return state