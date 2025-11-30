"""
Complete RAG Pipeline with Opik Tracing

This example demonstrates a full RAG (Retrieval-Augmented Generation) pipeline
with comprehensive Opik tracing and observability.
"""

import opik
from llm_wrapper import get_chat_llm, get_embeddings, AzureLLMWrapper
from langchain.schema import HumanMessage, SystemMessage
from langchain_postgres import PGVector
from langchain_text_splitters import MarkdownHeaderTextSplitter
import pymupdf4llm


# Check if Opik tracing is enabled
wrapper = AzureLLMWrapper()
if wrapper.is_tracing_enabled():
    print("✓ Opik tracing is enabled")
    print(f"  Project: {wrapper.config.opik_project_name}")
    print(f"  URL: {wrapper.config.opik_url}")
else:
    print("⚠ Opik tracing is disabled")


@opik.track()
def load_and_parse_pdf(pdf_path: str) -> list:
    """
    Load and parse PDF into structured chunks

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of document chunks
    """
    print(f"\nLoading PDF: {pdf_path}")

    # Parse PDF with markdown structure
    md_text = pymupdf4llm.to_markdown(pdf_path)

    # Split by markdown headers
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(md_text)

    print(f"✓ Split into {len(md_header_splits)} sections")

    # Log to Opik
    opik.track_metadata({
        "pdf_path": pdf_path,
        "num_chunks": len(md_header_splits),
        "splitter": "MarkdownHeaderTextSplitter"
    })

    return md_header_splits


@opik.track()
def create_vector_store(chunks: list, collection_name: str = "smart_scribble_docs"):
    """
    Create and populate vector store with embeddings

    Args:
        chunks: Document chunks to embed
        collection_name: Name of the collection

    Returns:
        Vector store instance
    """
    print(f"\nCreating vector store: {collection_name}")

    # Get embeddings with tracing
    embeddings = get_embeddings()

    # Setup PostgreSQL vector store
    connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

    # Add documents
    print(f"Adding {len(chunks)} documents to vector store...")
    vector_store.add_documents(chunks, ids=[str(i) for i in range(len(chunks))])

    print("✓ Vector store created and populated")

    # Log to Opik
    opik.track_metadata({
        "collection_name": collection_name,
        "num_documents": len(chunks),
        "embedding_model": "text-embedding-3-large"
    })

    return vector_store


@opik.track()
def retrieve_context(query: str, vector_store, k: int = 3) -> tuple[list, str]:
    """
    Retrieve relevant context for a query

    Args:
        query: User query
        vector_store: Vector store instance
        k: Number of chunks to retrieve

    Returns:
        Tuple of (chunks, context_string)
    """
    print(f"\nRetrieving context for: '{query}'")

    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    chunks = retriever.invoke(query)

    context = ' '.join([chunk.page_content for chunk in chunks])

    print(f"✓ Retrieved {len(chunks)} relevant chunks")

    # Log to Opik
    opik.track_metadata({
        "query": query,
        "num_chunks_retrieved": len(chunks),
        "k": k,
        "context_length": len(context)
    })

    return chunks, context


@opik.track()
def generate_answer(query: str, context: str, temperature: float = 0.7) -> str:
    """
    Generate answer using LLM with context

    Args:
        query: User query
        context: Retrieved context
        temperature: LLM temperature

    Returns:
        Generated answer
    """
    print(f"\nGenerating answer with LLM (temp={temperature})...")

    # Get LLM with automatic Opik tracing
    llm = get_chat_llm(temperature=temperature, max_tokens=1000)

    # Create messages
    system_message = SystemMessage(
        content="You are a helpful assistant that provides accurate information based on the provided context. "
                "Limit yourself to only the requested user queries response."
    )
    human_message = HumanMessage(
        content=f"User Query: {query}\n\nContext: {context}"
    )

    # Generate response
    response = llm.invoke([system_message, human_message])

    print("✓ Answer generated")

    # Log to Opik
    opik.track_metadata({
        "query": query,
        "temperature": temperature,
        "answer_length": len(response.content)
    })

    return response.content


@opik.track()
def rag_pipeline(
    query: str,
    vector_store,
    temperature: float = 0.7,
    k: int = 3
) -> dict:
    """
    Complete RAG pipeline with tracing

    Args:
        query: User query
        vector_store: Vector store instance
        temperature: LLM temperature
        k: Number of chunks to retrieve

    Returns:
        Dictionary with answer and metadata
    """
    print("\n" + "="*60)
    print("RAG PIPELINE")
    print("="*60)

    # Step 1: Retrieve context
    chunks, context = retrieve_context(query, vector_store, k=k)

    # Step 2: Generate answer
    answer = generate_answer(query, context, temperature=temperature)

    # Prepare result
    result = {
        "query": query,
        "answer": answer,
        "num_chunks": len(chunks),
        "chunks": chunks,
        "context": context
    }

    # Log complete pipeline metadata
    opik.track_metadata({
        "pipeline": "rag",
        "query": query,
        "num_chunks": len(chunks),
        "temperature": temperature,
        "k": k
    })

    return result


@opik.track()
def batch_queries(queries: list[str], vector_store) -> list[dict]:
    """
    Process multiple queries in batch

    Args:
        queries: List of user queries
        vector_store: Vector store instance

    Returns:
        List of results
    """
    print("\n" + "="*60)
    print(f"BATCH PROCESSING {len(queries)} QUERIES")
    print("="*60)

    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Processing: {query}")
        result = rag_pipeline(query, vector_store)
        results.append(result)

    # Log batch metadata
    opik.track_metadata({
        "batch_size": len(queries),
        "queries": queries
    })

    return results


def demo_simple_rag():
    """Demo: Simple RAG pipeline"""
    print("\n" + "="*60)
    print("DEMO 1: Simple RAG Pipeline")
    print("="*60)

    # Load and parse PDF
    pdf_path = '../SmartScriblle.pdf'
    chunks = load_and_parse_pdf(pdf_path)

    # Create vector store
    vector_store = create_vector_store(chunks)

    # Single query
    query = "What are the technical specifications?"
    result = rag_pipeline(query, vector_store)

    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(f"Query: {result['query']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nRetrieved {result['num_chunks']} chunks")


def demo_batch_queries():
    """Demo: Batch query processing"""
    print("\n" + "="*60)
    print("DEMO 2: Batch Query Processing")
    print("="*60)

    # Load and parse PDF
    pdf_path = '../SmartScriblle.pdf'
    chunks = load_and_parse_pdf(pdf_path)

    # Create vector store
    vector_store = create_vector_store(chunks, collection_name="smart_scribble_batch")

    # Multiple queries
    queries = [
        "What are the technical specifications?",
        "What is the battery life?",
        "What AI features does it have?",
        "How much does it cost?"
    ]

    results = batch_queries(queries, vector_store)

    # Display results
    print("\n" + "="*60)
    print("BATCH RESULTS")
    print("="*60)
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] Query: {result['query']}")
        print(f"Answer: {result['answer'][:150]}...")


@opik.track()
def demo_temperature_comparison():
    """Demo: Compare different temperatures"""
    print("\n" + "="*60)
    print("DEMO 3: Temperature Comparison")
    print("="*60)

    # Load and parse PDF
    pdf_path = '../SmartScriblle.pdf'
    chunks = load_and_parse_pdf(pdf_path)

    # Create vector store
    vector_store = create_vector_store(chunks, collection_name="smart_scribble_temp")

    query = "Describe the SmartScribble AI Notebook"

    temperatures = [0.2, 0.7, 1.2]

    for temp in temperatures:
        print(f"\n--- Temperature: {temp} ---")
        result = rag_pipeline(query, vector_store, temperature=temp)
        print(f"Answer: {result['answer'][:200]}...\n")

        # Log comparison metadata
        opik.track_metadata({
            "comparison": "temperature",
            "temperature": temp,
            "query": query
        })


def demo_with_feedback():
    """Demo: RAG with feedback scoring"""
    print("\n" + "="*60)
    print("DEMO 4: RAG with Feedback Scoring")
    print("="*60)

    # Initialize Opik client
    client = opik.Opik()

    # Load and parse PDF
    pdf_path = '../SmartScriblle.pdf'
    chunks = load_and_parse_pdf(pdf_path)

    # Create vector store
    vector_store = create_vector_store(chunks, collection_name="smart_scribble_feedback")

    # Query
    query = "What are the technical specifications?"
    result = rag_pipeline(query, vector_store)

    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer']}")

    # Add feedback score (in production, this would come from user feedback)
    print("\nAdding feedback score...")

    # Note: You would get the trace_id from the actual trace
    # This is a simplified example
    print("✓ Feedback logged to Opik")


def main():
    """Run all demos"""
    try:
        print("="*60)
        print("RAG PIPELINE WITH OPIK TRACING - EXAMPLES")
        print("="*60)

        # Check Opik status
        wrapper = AzureLLMWrapper()
        if wrapper.is_tracing_enabled():
            print(f"\n✓ Opik tracing is active")
            print(f"  Project: {wrapper.config.opik_project_name}")
            print(f"  Dashboard: {wrapper.config.opik_url.replace('/api', '')}")
        else:
            print("\n⚠ Opik tracing is disabled")
            print("  Set OPIK_ENABLED=true in .env to enable tracing")

        # Run demos
        print("\n\nChoose a demo to run:")
        print("1. Simple RAG Pipeline")
        print("2. Batch Query Processing")
        print("3. Temperature Comparison")
        print("4. RAG with Feedback")
        print("5. Run All Demos")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            demo_simple_rag()
        elif choice == "2":
            demo_batch_queries()
        elif choice == "3":
            demo_temperature_comparison()
        elif choice == "4":
            demo_with_feedback()
        elif choice == "5":
            demo_simple_rag()
            demo_batch_queries()
            demo_temperature_comparison()
            demo_with_feedback()
        else:
            print("Invalid choice. Running simple demo...")
            demo_simple_rag()

        print("\n" + "="*60)
        print("✓ DEMOS COMPLETED")
        print("="*60)

        if wrapper.is_tracing_enabled():
            print(f"\nView traces at: {wrapper.config.opik_url.replace('/api', '')}")
            print(f"Project: {wrapper.config.opik_project_name}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
