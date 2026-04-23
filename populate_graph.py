from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(username, password))

def populate_sample_data():
    with driver.session() as session:
        # Create BRCA1 → Olaparib relationship
        session.run("""
            MERGE (g:Gene {name: 'BRCA1'})
            MERGE (d:Drug {name: 'Olaparib'})
            MERGE (g)-[r:RESPONDS_TO]->(d)
            SET r.response_rate = 0.65,
                r.evidence_level = 'Level 1',
                r.clinical_trials = 5
        """)
        
        # Create BRCA2 → Olaparib relationship
        session.run("""
            MERGE (g:Gene {name: 'BRCA2'})
            MERGE (d:Drug {name: 'Olaparib'})
            MERGE (g)-[r:RESPONDS_TO]->(d)
            SET r.response_rate = 0.60,
                r.evidence_level = 'Level 1',
                r.clinical_trials = 4
        """)
        
        # Create ERBB2 → Trastuzumab relationship
        session.run("""
            MERGE (g:Gene {name: 'ERBB2'})
            MERGE (d:Drug {name: 'Trastuzumab'})
            MERGE (g)-[r:RESPONDS_TO]->(d)
            SET r.response_rate = 0.70,
                r.evidence_level = 'Level 1',
                r.clinical_trials = 10
        """)
        
        print("✅ Sample data populated successfully!")

populate_sample_data()
driver.close()
