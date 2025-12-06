"""
Example usage of the Azure LLM Wrapper

This script demonstrates various ways to use the Azure LLM wrapper
for different use cases.
"""

from llm_wrapper import get_chat_llm, get_embeddings, AzureLLMWrapper
from langchain.schema import HumanMessage, SystemMessage


def example_basic_chat():
    """Basic chat example"""
    print("=" * 50)
    print("Example 1: Basic Chat")
    print("=" * 50)

    llm = get_chat_llm(temperature=0.7, max_tokens=500)
    response = llm.invoke("What is artificial intelligence in one sentence?")
    print(f"Response: {response.content}\n")


def example_chat_with_messages():
    """Chat with system and user messages"""
    print("=" * 50)
    print("Example 2: Chat with System Message")
    print("=" * 50)

    llm = get_chat_llm(temperature=0.7)

    messages = [
        SystemMessage(content="You are a helpful technical assistant specializing in AI."),
        HumanMessage(content="Explain embeddings in simple terms.")
    ]

    response = llm.invoke(messages)
    print(f"Response: {response.content}\n")


def example_embeddings():
    """Generate embeddings"""
    print("=" * 50)
    print("Example 3: Text Embeddings")
    print("=" * 50)

    embeddings = get_embeddings()

    # Embed a single query
    query = "What is machine learning?"
    query_embedding = embeddings.embed_query(query)
    print(f"Query: {query}")
    print(f"Embedding dimension: {len(query_embedding)}")
    print(f"First 5 values: {query_embedding[:5]}\n")

    # Embed multiple documents
    documents = [
        "Machine learning is a subset of AI.",
        "Deep learning uses neural networks.",
        "Natural language processing handles text."
    ]
    doc_embeddings = embeddings.embed_documents(documents)
    print(f"Embedded {len(doc_embeddings)} documents")
    print(f"Each embedding has {len(doc_embeddings[0])} dimensions\n")


def example_rag_simulation():
    """Simulate a RAG (Retrieval-Augmented Generation) workflow"""
    print("=" * 50)
    print("Example 4: RAG Simulation")
    print("=" * 50)

    # Simulate retrieved context
    context = """
    The SmartScribble AI Notebook features:
    - 10.3-inch CanvasInk E-Ink Display
    - Resolution: 1872 × 1404 (227 DPI)
    - Processor: Quad-Core 1.8GHz ARM Cortex
    - Battery: 3000mAh Li-ion (up to 2 weeks standby)
    """

    user_query = "What is the battery life of SmartScribble?"

    llm = get_chat_llm(temperature=0.7)

    messages = [
        SystemMessage(content="You are a helpful assistant. Answer based only on the provided context."),
        HumanMessage(content=f"Context: {context}\n\nQuestion: {user_query}")
    ]

    response = llm.invoke(messages)
    print(f"User Query: {user_query}")
    print(f"Response: {response.content}\n")


def example_wrapper_class():
    """Using the wrapper class directly"""
    print("=" * 50)
    print("Example 5: Using Wrapper Class")
    print("=" * 50)

    # Initialize wrapper
    wrapper = AzureLLMWrapper()

    # Get different LLM configurations
    creative_llm = wrapper.get_chat_llm(temperature=1.0, max_tokens=300)
    factual_llm = wrapper.get_chat_llm(temperature=0.2, max_tokens=200)

    prompt = "Write a tagline for an AI notebook."

    print("Creative response (temp=1.0):")
    creative_response = creative_llm.invoke(prompt)
    print(creative_response.content)

    print("\nFactual response (temp=0.2):")
    factual_response = factual_llm.invoke(prompt)
    print(factual_response.content)
    print()


def example_conversation():
    """Multi-turn conversation"""
    print("=" * 50)
    print("Example 6: Multi-turn Conversation")
    print("=" * 50)

    llm = get_chat_llm(temperature=0.7)

    conversation = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is the capital of France?"),
    ]

    # First turn
    response1 = llm.invoke(conversation)
    print(f"User: What is the capital of France?")
    print(f"Assistant: {response1.content}\n")

    # Add to conversation history
    conversation.append(response1)
    conversation.append(HumanMessage(content="What is its population?"))

    # Second turn
    response2 = llm.invoke(conversation)
    print(f"User: What is its population?")
    print(f"Assistant: {response2.content}\n")


def example_streaming():
    """Streaming response example"""
    print("=" * 50)
    print("Example 7: Streaming Response")
    print("=" * 50)

    llm = get_chat_llm(temperature=0.7, streaming=True)

    print("Question: Explain quantum computing in 3 sentences.")
    print("Streaming response: ", end="", flush=True)

    for chunk in llm.stream("Explain quantum computing in 3 sentences."):
        print(chunk.content, end="", flush=True)

    print("\n")


def main():
    """Run all examples"""
    try:
        example_basic_chat()
        example_chat_with_messages()
        example_embeddings()
        example_rag_simulation()
        example_wrapper_class()
        example_conversation()
        example_streaming()

        print("=" * 50)
        print("All examples completed successfully!")
        print("=" * 50)

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nPlease ensure:")
        print("1. You have created a .env file (copy from .env.example)")
        print("2. You have set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
        print("3. Your Azure OpenAI resource is properly configured")

    except Exception as e:
        print(f"\nError: {e}")
        print(f"Error type: {type(e).__name__}")


if __name__ == "__main__":
    main()
