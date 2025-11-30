# Quick Start: Azure LLM Wrapper with Opik Tracing

Get up and running with Azure OpenAI and Opik observability in 5 minutes.

## Prerequisites

- Python 3.8+
- Docker (for Opik)
- Azure OpenAI account with API key

## Step 1: Start Opik Server

```bash
# Navigate to opik directory
cd opik

# Start Opik (Windows)
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"

# Wait for services to start, then access UI at:
# http://localhost:5173
```

## Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This installs:
- `langchain` and `langchain-openai` for LLM integration
- `opik` for tracing
- `python-dotenv` for configuration
- Other dependencies

## Step 3: Configure Environment

Your `.env` file is already configured with:

```env
# Azure OpenAI (Already configured ✓)
AZURE_OPENAI_ENDPOINT=https://rushi-m9xyt0et-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=02oCvRekc2bvzlYWHVhKHNGEyxcMyHyBblbGPD3AMVlslt1XWPfHJQQJ99BDACHYHv6XJ3w3AAAAACOGXc0e
AZURE_OPENAI_API_VERSION=2024-02-01

# Deployment Names
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1-mini
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME=text-embedding-3-large

# Opik (Already configured ✓)
OPIK_URL_OVERRIDE=http://localhost:5173/api
OPIK_WORKSPACE=default
OPIK_PROJECT_NAME=customer-support
OPIK_ENABLED=true
```

## Step 4: Test Basic Usage

Create a test file `test_setup.py`:

```python
from llm_wrapper import get_chat_llm, AzureLLMWrapper

# Check setup
wrapper = AzureLLMWrapper()

print("Azure OpenAI Configuration:")
print(f"  ✓ Endpoint: {wrapper.config.endpoint}")
print(f"  ✓ Model: {wrapper.config.chat_model}")

print("\nOpik Configuration:")
print(f"  ✓ Tracing Enabled: {wrapper.is_tracing_enabled()}")
print(f"  ✓ Project: {wrapper.config.opik_project_name}")
print(f"  ✓ URL: {wrapper.config.opik_url}")

# Test LLM
print("\nTesting LLM...")
llm = get_chat_llm(temperature=0.7)
response = llm.invoke("What is AI in one sentence?")
print(f"Response: {response.content}")

print("\n✓ Setup complete!")
print(f"\nView traces at: http://localhost:5173")
```

Run it:

```bash
python test_setup.py
```

Expected output:
```
✓ Opik tracing configured for project: customer-support
✓ Opik tracer initialized for project: customer-support

Azure OpenAI Configuration:
  ✓ Endpoint: https://rushi-m9xyt0et-eastus2.cognitiveservices.azure.com/
  ✓ Model: gpt-4.1-mini

Opik Configuration:
  ✓ Tracing Enabled: True
  ✓ Project: customer-support
  ✓ URL: http://localhost:5173/api

Testing LLM...
Response: Artificial Intelligence (AI) is the simulation of human intelligence...

✓ Setup complete!

View traces at: http://localhost:5173
```

## Step 5: View Traces in Opik

1. Open browser: [http://localhost:5173](http://localhost:5173)
2. Navigate to Projects → "customer-support"
3. You'll see:
   - All LLM calls traced
   - Input/output logged
   - Token usage tracked
   - Execution time measured

## Step 6: Run Example RAG Pipeline

```bash
cd src
python example_rag_with_opik.py
```

Choose a demo to run and see full RAG pipeline tracing!

## Common Usage Patterns

### Simple Chat

```python
from llm_wrapper import get_chat_llm

llm = get_chat_llm(temperature=0.7)
response = llm.invoke("Your question here")
print(response.content)

# Automatically traced to Opik!
```

### RAG Pipeline

```python
import opik
from llm_wrapper import get_chat_llm, get_embeddings

@opik.track()
def rag_pipeline(query: str):
    # Retrieve context (your vector store logic)
    context = retrieve_context(query)

    # Generate answer
    llm = get_chat_llm()
    response = llm.invoke(f"Context: {context}\n\nQuery: {query}")

    return response.content

# Fully traced!
answer = rag_pipeline("What are the specs?")
```

### Embeddings

```python
from llm_wrapper import get_embeddings

embeddings = get_embeddings()
vector = embeddings.embed_query("Sample text")
```

## Next Steps

1. **Read Full Documentation**
   - [src/README_LLM_WRAPPER.md](src/README_LLM_WRAPPER.md) - Complete LLM wrapper guide
   - [src/OPIK_INTEGRATION.md](src/OPIK_INTEGRATION.md) - Opik integration details

2. **Try Examples**
   - [src/example_llm_usage.py](src/example_llm_usage.py) - Basic LLM examples
   - [src/example_rag_with_opik.py](src/example_rag_with_opik.py) - RAG with tracing
   - [src/notebooks/llm_wrapper_example.ipynb](src/notebooks/llm_wrapper_example.ipynb) - Jupyter notebook

3. **Explore Features**
   - Custom tracing with `@opik.track()`
   - Feedback scoring
   - LLM-as-a-judge metrics
   - Production monitoring

## Troubleshooting

### Opik not connecting?

```bash
# Check Opik is running
docker ps | grep opik

# Restart Opik
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"
```

### No traces appearing?

Check configuration:
```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper()
print(f"Tracing enabled: {wrapper.is_tracing_enabled()}")
```

Verify `.env` has:
```env
OPIK_ENABLED=true
```

### Import errors?

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Disable Tracing (Optional)

To disable tracing temporarily:

**In `.env`:**
```env
OPIK_ENABLED=false
```

**Or in code:**
```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper(enable_tracing=False)
llm = wrapper.get_chat_llm()
```

## Resources

- **Opik Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Project**: customer-support
- **Documentation**: [Opik Docs](https://www.comet.com/docs/opik/)

---

**You're ready to go!** 🚀

All LLM calls are now automatically traced and observable through Opik.
