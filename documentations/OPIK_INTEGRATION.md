# Opik Integration Guide

This guide explains how to use Opik for tracing and observability with the Azure LLM wrapper.

## What is Opik?

Opik is an open-source LLM evaluation platform that provides:
- Comprehensive tracing of LLM calls
- Conversation logging and agent activity tracking
- Advanced evaluation metrics
- Production monitoring dashboards
- LLM-as-a-judge evaluations

## Setup

### 1. Start Opik Server (Docker)

You have Opik self-hosted in Docker. Start it with:

```bash
# Navigate to the Opik directory
cd opik

# Start Opik (Windows)
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"

# Or on Linux/Mac
./opik.sh
```

Once started, access Opik UI at: [http://localhost:5173](http://localhost:5173)

### 2. Install Opik Python SDK

```bash
pip install opik
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Your `.env` file should include:

```env
# Opik Configuration
OPIK_URL_OVERRIDE=http://localhost:5173/api
OPIK_WORKSPACE=default
OPIK_PROJECT_NAME=customer-support
OPIK_API_KEY=
OPIK_ENABLED=true
```

Configuration options:
- `OPIK_URL_OVERRIDE`: URL of your self-hosted Opik instance
- `OPIK_WORKSPACE`: Workspace name (default: "default")
- `OPIK_PROJECT_NAME`: Project name for organizing traces
- `OPIK_API_KEY`: API key (leave empty for self-hosted without auth)
- `OPIK_ENABLED`: Toggle tracing on/off (true/false)

## Usage

### Automatic Tracing (Recommended)

The LLM wrapper automatically enables Opik tracing. Just use it normally:

```python
from llm_wrapper import get_chat_llm

# Tracing is automatically enabled
llm = get_chat_llm(temperature=0.7)
response = llm.invoke("What is AI?")

# All calls are traced to Opik!
```

### Checking Tracing Status

```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper()

if wrapper.is_tracing_enabled():
    print("✓ Opik tracing is active")
else:
    print("✗ Opik tracing is disabled")
```

### Disabling Tracing Temporarily

```python
from llm_wrapper import AzureLLMWrapper

# Disable tracing for this instance
wrapper = AzureLLMWrapper(enable_tracing=False)
llm = wrapper.get_chat_llm()

# Or set in .env file
# OPIK_ENABLED=false
```

### Manual Tracing with Decorators

For custom functions, use Opik decorators:

```python
import opik
from llm_wrapper import get_chat_llm

@opik.track()
def answer_question(question: str) -> str:
    """Answer a question using the LLM"""
    llm = get_chat_llm(temperature=0.7)
    response = llm.invoke(question)
    return response.content

# This function call will be traced
answer = answer_question("What is machine learning?")
```

### Tracing RAG Pipelines

```python
import opik
from llm_wrapper import get_chat_llm, get_embeddings
from langchain_postgres import PGVector

@opik.track()
def retrieve_context(query: str, vector_store) -> list:
    """Retrieve relevant context"""
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    chunks = retriever.invoke(query)
    return chunks

@opik.track()
def generate_answer(query: str, context: str) -> str:
    """Generate answer with LLM"""
    llm = get_chat_llm(temperature=0.7)
    prompt = f"Query: {query}\n\nContext: {context}"
    response = llm.invoke(prompt)
    return response.content

@opik.track()
def rag_pipeline(query: str, vector_store):
    """Full RAG pipeline with tracing"""
    # Retrieve context
    chunks = retrieve_context(query, vector_store)
    context = ' '.join([chunk.page_content for chunk in chunks])

    # Generate answer
    answer = generate_answer(query, context)

    # Log to Opik
    opik.track_metadata({"query": query, "num_chunks": len(chunks)})

    return answer

# Setup vector store
embeddings = get_embeddings()
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="docs",
    connection="postgresql://..."
)

# Run with full tracing
answer = rag_pipeline("What are the technical specs?", vector_store)
```

### Adding Feedback Scores

```python
import opik

# Track a call and get trace
client = opik.Opik()

@opik.track()
def process_query(query: str) -> str:
    llm = get_chat_llm()
    response = llm.invoke(query)
    return response.content

# Get the trace
answer = process_query("Explain quantum computing")

# Add feedback score
client.log_traces_feedback_scores(
    name="answer_quality",
    value=0.95,
    reason="Accurate and comprehensive"
)
```

### Logging Conversations

```python
import opik
from llm_wrapper import get_chat_llm
from langchain.schema import HumanMessage, AIMessage, SystemMessage

@opik.track()
def chat_conversation(messages: list):
    """Multi-turn conversation with tracing"""
    llm = get_chat_llm(temperature=0.7)

    conversation = [SystemMessage(content="You are a helpful assistant.")]
    responses = []

    for user_msg in messages:
        conversation.append(HumanMessage(content=user_msg))
        response = llm.invoke(conversation)
        conversation.append(response)
        responses.append(response.content)

        # Log each turn
        opik.track_metadata({
            "turn": len(responses),
            "user_message": user_msg,
            "ai_response": response.content
        })

    return responses

# Multi-turn conversation
messages = [
    "What is AI?",
    "What are its applications?",
    "What about ethical concerns?"
]

responses = chat_conversation(messages)
```

## Advanced Features

### Custom Tags

```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper()

# Get tracer with custom tags
tracer = wrapper.get_opik_tracer()
if tracer:
    tracer.tags.extend(["production", "v1.0"])

llm = wrapper.get_chat_llm()
```

### Experiments and Evaluation

```python
import opik
from llm_wrapper import get_chat_llm

# Create a dataset
client = opik.Opik()
dataset = client.create_dataset(name="test_queries")

# Add items to dataset
dataset.insert([
    {"input": "What is AI?", "expected_output": "AI is..."},
    {"input": "What is ML?", "expected_output": "ML is..."},
])

# Run evaluation
@opik.track()
def evaluate_model(input_text: str) -> str:
    llm = get_chat_llm(temperature=0.7)
    return llm.invoke(input_text).content

# Evaluate on dataset
for item in dataset:
    result = evaluate_model(item["input"])
    # Compare with expected_output
    # Log metrics to Opik
```

### LLM-as-a-Judge Metrics

```python
import opik
from opik.evaluation.metrics import Hallucination, AnswerRelevance

@opik.track()
def evaluated_rag(query: str, context: str):
    llm = get_chat_llm()
    response = llm.invoke(f"Context: {context}\n\nQuery: {query}")

    # Evaluate for hallucination
    hallucination_metric = Hallucination()
    hallucination_score = hallucination_metric.score(
        input=query,
        output=response.content,
        context=context
    )

    # Evaluate answer relevance
    relevance_metric = AnswerRelevance()
    relevance_score = relevance_metric.score(
        input=query,
        output=response.content
    )

    # Log scores
    opik.track_metadata({
        "hallucination_score": hallucination_score,
        "relevance_score": relevance_score
    })

    return response.content
```

## Viewing Traces

1. **Web UI**: Visit [http://localhost:5173](http://localhost:5173)
2. Navigate to your project: "customer-support"
3. View traces with:
   - Input/output logs
   - Execution time
   - Token usage
   - Custom metadata
   - Feedback scores

## Monitoring Dashboard

The Opik dashboard provides:
- **Trace counts** over time
- **Token usage** tracking
- **Cost estimation**
- **Latency metrics**
- **Error rates**
- **Feedback score** trends

## Best Practices

### 1. Use Descriptive Project Names
```python
# In .env
OPIK_PROJECT_NAME=customer-support-rag-v2
```

### 2. Add Context with Metadata
```python
import opik

opik.track_metadata({
    "user_id": "user123",
    "session_id": "sess456",
    "model_version": "v1.0",
    "environment": "production"
})
```

### 3. Tag Production vs Development
```python
# Development
OPIK_PROJECT_NAME=customer-support-dev

# Production
OPIK_PROJECT_NAME=customer-support-prod
```

### 4. Organize with Tags
```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper()
tracer = wrapper.get_opik_tracer()

if tracer:
    tracer.tags = ["rag", "technical-support", "production"]
```

### 5. Monitor Token Usage
```python
import opik

@opik.track()
def monitored_call(query: str):
    llm = get_chat_llm(max_tokens=500)
    response = llm.invoke(query)

    # Opik automatically tracks token usage
    return response.content
```

## Troubleshooting

### Issue: "Opik not available"
**Solution**: Install Opik SDK
```bash
pip install opik
```

### Issue: "Cannot connect to Opik server"
**Solution**: Ensure Opik Docker is running
```bash
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"
```

Check [http://localhost:5173](http://localhost:5173)

### Issue: "Tracing not working"
**Solution**: Check configuration
```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper()
print(f"Tracing enabled: {wrapper.is_tracing_enabled()}")
print(f"Tracer: {wrapper.get_opik_tracer()}")
```

Verify `.env`:
```env
OPIK_ENABLED=true
OPIK_URL_OVERRIDE=http://localhost:5173/api
```

### Issue: "No traces appearing in UI"
**Solution**:
1. Check Opik server is running
2. Verify URL in .env matches server
3. Check project name matches
4. Wait a few seconds for traces to sync

## Disabling Opik

To disable Opik without removing the package:

**Option 1**: Set in `.env`
```env
OPIK_ENABLED=false
```

**Option 2**: Disable in code
```python
wrapper = AzureLLMWrapper(enable_tracing=False)
```

The wrapper will work normally without tracing.

## Integration with CI/CD

```python
import os
import opik

# In CI/CD, disable tracing or use test project
if os.getenv("CI") == "true":
    os.environ["OPIK_ENABLED"] = "false"
    # Or use test project
    os.environ["OPIK_PROJECT_NAME"] = "ci-tests"
```

## Resources

- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Opik GitHub](https://github.com/comet-ml/opik)
- [LangChain Integration](https://www.comet.com/docs/opik/integrations/langchain)
- [Local Deployment Guide](https://www.comet.com/docs/opik/self-host/local_deployment)

## Example: Complete RAG with Tracing

See [src/example_rag_with_opik.py](example_rag_with_opik.py) for a complete example integrating:
- Document loading
- Vector store
- RAG pipeline
- Opik tracing
- Evaluation metrics
