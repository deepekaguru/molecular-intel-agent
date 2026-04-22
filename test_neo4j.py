from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=None
)

with driver.session() as session:
    result = session.run("RETURN 'Neo4j connected from Python!' AS message")
    for record in result:
        print(record["message"])

driver.close()
print("Done!")