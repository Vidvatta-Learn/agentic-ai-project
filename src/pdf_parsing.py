"""
PDF Parsing and Vector Store Module

This module provides functionality to:
1. Parse PDF documents using Azure Document Intelligence or PyMuPDF
2. Split documents by markdown headers
3. Store parsed content in a PostgreSQL vector database
4. Create a RAG agent with retrieval capabilities
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_postgres import PGVector
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_core.documents.base import Document
import pymupdf4llm

load_dotenv()


class PDFParser:
    """Handle PDF parsing and document processing"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )

    def parse_with_pymupdf(self) -> list[Document]:
        """Parse PDF using PyMuPDF and split by markdown headers"""
        md_text = pymupdf4llm.to_markdown(self.pdf_path)
        md_header_splits = self.markdown_splitter.split_text(md_text)
        return md_header_splits

    def parse_with_azure(self, endpoint: str, api_key: str) -> list[Document]:
        """Parse PDF using Azure Document Intelligence"""
        loader = AzureAIDocumentIntelligenceLoader(
            api_endpoint=endpoint,
            api_key=api_key,
            file_path=self.pdf_path,
            api_model="prebuilt-layout"
        )
        documents = loader.load()

        # Split by markdown headers
        md_header_splits = self.markdown_splitter.split_text(
            documents[0].metadata['content']
        )
        return md_header_splits


class VectorStoreManager:
    """Manage vector store operations"""

    def __init__(self, embeddings, collection_name: str = "documents"):
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.connection = self._get_connection_string()
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection,
            use_jsonb=True,
        )

    def _get_connection_string(self) -> str:
        """Build PostgreSQL connection string from environment variables"""
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '6024')
        database = os.getenv('POSTGRES_DATABASE', 'langchain')
        user = os.getenv('POSTGRES_USER', 'langchain')
        password = os.getenv('POSTGRES_PASSWORD', 'langchain')

        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"

    def add_documents(self, documents: list[Document], ids: list[int] = None) -> list[int]:
        """Add documents to vector store"""
        if ids is None:
            ids = list(range(len(documents)))
        return self.vector_store.add_documents(documents, ids=ids)

    def get_retriever(self, k: int = 3):
        """Get retriever for the vector store"""
        return self.vector_store.as_retriever(search_kwargs={"k": k})


class RAGAgent:
    """RAG Agent with retrieval capabilities"""

    def __init__(self, llm, vector_store_manager: VectorStoreManager, k: int = 3):
        self.llm = llm
        self.vector_store_manager = vector_store_manager
        self.k = k
        self.agent = self._create_agent()

    def _create_retriever_tool(self):
        """Create retriever tool for the agent"""
        vector_store_manager = self.vector_store_manager
        k = self.k

        @tool
        def retriever_tool(user_query: str) -> str:
            """Retrieve relevant document chunks based on the user query.
            Context is related to information about the product like details,
            technical specifications, features, compatibility, pricing, and availability."""
            retriever = vector_store_manager.get_retriever(k=k)
            chunks = retriever.invoke(user_query)
            return ' '.join([chunk.page_content for chunk in chunks])

        return retriever_tool

    def _create_agent(self):
        """Create the agent with retriever tool"""
        retriever_tool = self._create_retriever_tool()
        return create_agent(
            self.llm,
            tools=[retriever_tool],
            system_prompt="You are a helpful assistant that provides accurate information based on retrieved context."
        )

    def query(self, user_query: str) -> str:
        """Query the agent and return the response"""
        response = self.agent.invoke({'messages': [user_query]})
        return response['messages'][-1].content


def main():
    """Main execution function"""
    # Import LLM wrapper
    import sys
    sys.path.append('..')
    from llm_wrapper import get_chat_llm, get_embeddings

    # Initialize components
    pdf_path = '../SmartScriblle.pdf'
    parser = PDFParser(pdf_path)

    # Parse PDF
    documents = parser.parse_with_pymupdf()
    print(f"Parsed {len(documents)} document sections")

    # Initialize embeddings and vector store
    embeddings = get_embeddings()
    vector_store_manager = VectorStoreManager(
        embeddings=embeddings,
        collection_name="smart_scribble_docs"
    )

    # Add documents to vector store
    doc_ids = vector_store_manager.add_documents(documents)
    print(f"Added documents with IDs: {doc_ids}")

    # Create RAG agent
    llm = get_chat_llm()
    rag_agent = RAGAgent(llm, vector_store_manager, k=3)

    # Example query
    query = "Which specific file formats does the SmartScribble support?"
    response = rag_agent.query(query)
    print(f"\nQuery: {query}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
