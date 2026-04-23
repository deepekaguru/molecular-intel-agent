from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print(f"Username: {user}")
print(f"Password: {password[:10]}...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        print("✅ SUCCESS! Connected to Neo4j Aura!")
        for record in result:
            print(f"Test query returned: {record['test']}")
    driver.close()
except Exception as e:
    print(f"❌ FAILED! Error: {e}")
