"""RAG tool for policy and FAQ document search."""

from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.documents import Document


# Module-level cache for vector store
_vector_store = None


def load_policy_documents():
    """Load policy documents from the policies folder."""
    # Resolve policies folder at project root
    root = Path(__file__).resolve().parents[2]
    policies_dir = root / "policies"
    
    documents = []
    
    # Load all .txt files in policies folder
    for policy_file in policies_dir.glob("*.txt"):
        loader = TextLoader(str(policy_file), encoding="utf-8")
        docs = loader.load()
        
        # Set metadata for each document
        for doc in docs:
            doc.metadata["source"] = policy_file.name
        
        documents.extend(docs)
    
    return documents


def split_documents(documents):
    """Split documents into chunks for better retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_documents(documents)


def get_vector_store():
    """Get or create the ChromaDB vector store for policies."""
    global _vector_store
    
    if _vector_store is not None:
        return _vector_store
    
    # Resolve persist directory
    root = Path(__file__).resolve().parents[2]
    persist_dir = root / "chroma_db"
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Check if Chroma DB already exists
    if persist_dir.exists() and any(persist_dir.iterdir()):
        print("📚 Loading existing Chroma vector store...")
        _vector_store = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings
        )
    else:
        print("📚 Creating new Chroma vector store from policy documents...")
        documents = load_policy_documents()
        split_docs = split_documents(documents)
        
        _vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=str(persist_dir)
        )
        print(f"✅ Created Chroma DB with {len(split_docs)} document chunks")
    
    return _vector_store


@tool
def search_policies(query: str) -> str:
    """
    Search policy documents for answers about returns, shipping, and FAQs.
    
    Use this tool for policy and FAQ questions like:
    - "What is your returns policy?"
    - "How long does shipping take?"
    - "When can I return an item?"
    
    Do NOT use this for user-specific order queries.
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=4)
    
    # Format results with source information
    output_lines = []
    for doc in results:
        source = doc.metadata.get("source", "Unknown")
        content = doc.page_content[:500]  # Limit content length
        output_lines.append(f"**Source: {source}**\n{content}\n")
    
    if output_lines:
        return "\n---\n".join(output_lines)
    else:
        return "No relevant policy information found."


def initialize_vector_store():
    """Initialize the vector store on app startup."""
    get_vector_store()


__all__ = ["search_policies", "initialize_vector_store"]
