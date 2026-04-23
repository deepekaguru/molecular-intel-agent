from neo4j import GraphDatabase

import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(username, password))

def run(state):
    print("Agent 2 running — querying knowledge graph...")

    mutations = state['mutations']
    cnvs = state['cnvs']
    all_genes = mutations + cnvs

    if not all_genes:
        print("No mutations found to query")
        state['graph_results'] = []
        return state

    with driver.session() as session:
        result = session.run("""
            MATCH (g:Gene)-[:HAS_MUTATION]->(m:Mutation)
            WHERE g.name IN $genes
            MATCH (m)-[:TARGETED_BY]->(d:Drug)
            MATCH (d)-[:HAS_OUTCOME]->(o:Outcome)
            RETURN g.name AS gene,
                   m.name AS mutation,
                   d.name AS drug,
                   o.response_rate AS response_rate
            ORDER BY o.response_rate DESC
        """, genes=all_genes)

        graph_results = [record.data() for record in result]
        state['graph_results'] = graph_results

    print(f"Graph results found: {len(graph_results)} matches")
    for r in graph_results:
        print(f"  {r['gene']} -> {r['drug']} (response rate: {r['response_rate']})")

    return state
