from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

sample_literature = [
    "BRCA1 mutations are associated with increased sensitivity to PARP inhibitors such as Olaparib. Clinical trials show 72% response rate in BRCA1 mutated breast cancer patients.",
    "TP53 mutations correlate with immunotherapy response. Pembrolizumab shows moderate efficacy in TP53 mutated tumors with 45% response rate in clinical studies.",
    "ERBB2 amplification is the primary biomarker for Trastuzumab therapy. HER2 positive patients show 81% response rate to Trastuzumab based treatment.",
    "MYC copy number variants are associated with aggressive tumor behavior. Tamoxifen shows moderate response in MYC amplified hormone receptor positive cancers.",
    "BRCA1 and BRCA2 mutations significantly increase risk of breast and ovarian cancer. Olaparib as maintenance therapy extends progression free survival.",
    "Combination of PARP inhibitors with immunotherapy shows promising results in BRCA mutated cancers with improved overall survival rates.",
]

CHROMA_DIR = "./chroma_db"

def build_vectorstore():
    docs = [Document(page_content=text) for text in sample_literature]
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY")),
        persist_directory=CHROMA_DIR
    )
    return vectorstore

def get_vectorstore():
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        print("Building vectorstore for first time...")
        return build_vectorstore()

    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    )

def run(state):
    print("Agent 3 running — retrieving literature evidence...")

    mutations = state["mutations"]
    drugs = [r["drug"] for r in state["graph_results"]]
    query = f"treatment evidence for mutations {mutations} and drugs {drugs}"

    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=3)

    if not docs:
        print("No documents found. Rebuilding vectorstore...")
        vectorstore = build_vectorstore()
        docs = vectorstore.similarity_search(query, k=3)

    evidence = "\n".join([d.page_content for d in docs])

    state["rag_evidence"] = evidence
    print(f"Evidence retrieved: {len(docs)} documents")
    if evidence:
        print(evidence[:200] + "...")
    else:
        print("No evidence text retrieved.")

    return state