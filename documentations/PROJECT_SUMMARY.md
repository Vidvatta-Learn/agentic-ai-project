# Project Summary: Azure LLM Wrapper with Opik Tracing

## Overview

This project provides a production-ready, reusable wrapper for Azure OpenAI services with built-in Opik observability and tracing. The wrapper simplifies LLM integration across your project while providing comprehensive monitoring capabilities.

## Key Features

### 1. Azure OpenAI Integration
- ✅ LangChain-based wrapper for Azure OpenAI
- ✅ Support for Chat models (GPT-4.1-mini)
- ✅ Support for Embeddings (text-embedding-3-large)
- ✅ Azure Document Intelligence integration
- ✅ Environment-based configuration

### 2. Opik Observability
- ✅ Automatic tracing of all LLM calls
- ✅ Self-hosted Opik instance (Docker)
- ✅ Token usage and cost tracking
- ✅ Latency monitoring
- ✅ Input/output logging
- ✅ Custom metadata and tags

### 3. Developer Experience
- ✅ Simple, clean API
- ✅ Type hints for IDE support
- ✅ Comprehensive error handling
- ✅ Singleton pattern for efficiency
- ✅ Easy enable/disable tracing

## Project Structure

```
customer-support-project/
├── .env                          # Environment configuration (configured ✓)
├── .env.example                  # Template for .env
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── QUICKSTART_OPIK.md           # Quick start guide
├── PROJECT_SUMMARY.md           # This file
│
├── src/
│   ├── llm_wrapper.py           # Main wrapper module ⭐
│   ├── README_LLM_WRAPPER.md    # Complete documentation
│   ├── OPIK_INTEGRATION.md      # Opik integration guide
│   ├── example_llm_usage.py     # Basic examples
│   ├── example_rag_with_opik.py # RAG pipeline examples ⭐
│   │
│   └── notebooks/
│       ├── pdf_parsing.ipynb              # Original notebook
│       └── llm_wrapper_example.ipynb      # New example notebook
│
└── opik/                         # Self-hosted Opik (already present)
    └── deployment/docker-compose/
```

## What's New

### Created Files

1. **Core Wrapper**
   - [src/llm_wrapper.py](src/llm_wrapper.py) - Main wrapper with Opik integration

2. **Configuration**
   - [.env.example](.env.example) - Configuration template
   - [.env](.env) - Your configured environment (✓)
   - [.gitignore](.gitignore) - Git ignore rules

3. **Documentation**
   - [src/README_LLM_WRAPPER.md](src/README_LLM_WRAPPER.md) - Complete wrapper guide
   - [src/OPIK_INTEGRATION.md](src/OPIK_INTEGRATION.md) - Opik integration details
   - [QUICKSTART_OPIK.md](QUICKSTART_OPIK.md) - 5-minute quick start
   - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - This summary

4. **Examples**
   - [src/example_llm_usage.py](src/example_llm_usage.py) - 7 basic examples
   - [src/example_rag_with_opik.py](src/example_rag_with_opik.py) - Complete RAG with tracing
   - [src/notebooks/llm_wrapper_example.ipynb](src/notebooks/llm_wrapper_example.ipynb) - Jupyter examples

5. **Dependencies**
   - [requirements.txt](requirements.txt) - All required packages

## Configuration Status

### Azure OpenAI ✅
```
Endpoint: https://rushi-m9xyt0et-eastus2.cognitiveservices.azure.com/
Model: gpt-4.1-mini
Embeddings: text-embedding-3-large
Status: Configured and ready
```

### Opik Tracing ✅
```
URL: http://localhost:5173/api
Workspace: default
Project: customer-support
Status: Configured (requires Opik to be running)
```

### Azure Document Intelligence ✅
```
Endpoint: https://test-vidvatta.cognitiveservices.azure.com/
Status: Configured
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Opik (Optional but Recommended)
```bash
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"

# Access at: http://localhost:5173
```

### 3. Use the Wrapper
```python
from llm_wrapper import get_chat_llm

# Automatic tracing enabled!
llm = get_chat_llm(temperature=0.7)
response = llm.invoke("What is AI?")
print(response.content)

# View traces at: http://localhost:5173
```

## Usage Patterns

### 1. Simple Chat
```python
from llm_wrapper import get_chat_llm

llm = get_chat_llm()
response = llm.invoke("Your question")
```

### 2. Embeddings
```python
from llm_wrapper import get_embeddings

embeddings = get_embeddings()
vector = embeddings.embed_query("Sample text")
```

### 3. RAG Pipeline
```python
import opik
from llm_wrapper import get_chat_llm, get_embeddings

@opik.track()
def rag_pipeline(query: str):
    # Retrieve context
    context = retrieve_context(query)

    # Generate answer
    llm = get_chat_llm()
    response = llm.invoke(f"Context: {context}\n\nQuery: {query}")

    return response.content
```

### 4. Custom Tracing
```python
import opik
from llm_wrapper import get_chat_llm

@opik.track()
def custom_function(input_text: str):
    llm = get_chat_llm()
    result = llm.invoke(input_text)

    # Add metadata
    opik.track_metadata({"custom_field": "value"})

    return result.content
```

## What Gets Traced

When Opik tracing is enabled, the system automatically logs:

1. **LLM Calls**
   - Input prompts
   - Output responses
   - Model parameters (temperature, max_tokens)
   - Token counts (prompt, completion, total)
   - Execution time

2. **Function Calls** (with `@opik.track()`)
   - Function inputs and outputs
   - Execution time
   - Custom metadata
   - Nested function calls

3. **RAG Pipelines**
   - Retrieval steps
   - Context used
   - Generation steps
   - End-to-end latency

## Viewing Observability Data

### Opik Dashboard: http://localhost:5173

**Features:**
- Real-time trace viewing
- Token usage tracking
- Cost estimation
- Latency monitoring
- Search and filter traces
- Custom dashboards
- Feedback scoring

**Navigation:**
1. Open http://localhost:5173
2. Go to Projects → "customer-support"
3. View all traces with detailed metrics

## Examples

### Run Basic Examples
```bash
cd src
python example_llm_usage.py
```

**Includes:**
1. Basic chat
2. Chat with system messages
3. Embeddings generation
4. RAG simulation
5. Wrapper class usage
6. Multi-turn conversations
7. Streaming responses

### Run RAG Examples
```bash
cd src
python example_rag_with_opik.py
```

**Choose from:**
1. Simple RAG pipeline
2. Batch query processing
3. Temperature comparison
4. RAG with feedback scoring

### Jupyter Notebooks
```bash
jupyter notebook src/notebooks/llm_wrapper_example.ipynb
```

## Benefits

### Before (Manual Configuration)
```python
import os
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://...'
os.environ['AZURE_OPENAI_API_KEY'] = 'key...'
os.environ['OPENAI_API_VERSION'] = '2024-02-01'

from langchain_openai import AzureChatOpenAI
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1-mini",
    model="gpt-4.1-mini",
    temperature=0.7
)
```

### After (Using Wrapper)
```python
from llm_wrapper import get_chat_llm

llm = get_chat_llm(temperature=0.7)
# Automatic configuration + tracing!
```

**Improvements:**
- ✅ 90% less boilerplate code
- ✅ Automatic Opik tracing
- ✅ Centralized configuration
- ✅ Type safety and validation
- ✅ Reusable across modules
- ✅ Production-ready monitoring

## Disabling Features

### Disable Tracing Globally
In `.env`:
```env
OPIK_ENABLED=false
```

### Disable Tracing Per Instance
```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper(enable_tracing=False)
llm = wrapper.get_chat_llm()
```

### Use Without Opik
The wrapper works fine without Opik installed:
```bash
pip install langchain-openai python-dotenv
# Skip: pip install opik
```

Tracing will be automatically disabled.

## Production Considerations

### 1. Environment Variables
- Store `.env` securely
- Use different configs for dev/staging/prod
- Never commit `.env` to git (already in `.gitignore`)

### 2. Opik in Production
- Use separate Opik instance for production
- Configure retention policies
- Set up alerts for anomalies
- Monitor token costs

### 3. Error Handling
```python
try:
    llm = get_chat_llm()
    response = llm.invoke(query)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Runtime error: {e}")
```

### 4. Rate Limiting
```python
from llm_wrapper import get_chat_llm
import time

def rate_limited_call(query: str):
    llm = get_chat_llm()
    response = llm.invoke(query)
    time.sleep(0.1)  # Rate limiting
    return response
```

## Troubleshooting

### Issue: Import errors
```bash
pip install -r requirements.txt
```

### Issue: Azure authentication fails
Check `.env` has correct:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`

### Issue: Opik not connecting
```bash
# Check Opik is running
docker ps | grep opik

# Start Opik
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"
```

### Issue: No traces appearing
1. Verify `OPIK_ENABLED=true` in `.env`
2. Check Opik URL is correct
3. Wait a few seconds for sync
4. Refresh Opik dashboard

## Next Steps

1. **Try Basic Examples**
   ```bash
   python src/example_llm_usage.py
   ```

2. **Run RAG Pipeline**
   ```bash
   python src/example_rag_with_opik.py
   ```

3. **Refactor Existing Code**
   - Update [src/notebooks/pdf_parsing.ipynb](src/notebooks/pdf_parsing.ipynb)
   - Replace manual config with wrapper
   - Add `@opik.track()` to functions

4. **Explore Opik Dashboard**
   - View traces at http://localhost:5173
   - Analyze token usage
   - Monitor latency
   - Set up custom dashboards

5. **Add Custom Tracing**
   - Use `@opik.track()` decorator
   - Add metadata with `opik.track_metadata()`
   - Implement feedback scoring

## Resources

### Documentation
- [Complete Wrapper Guide](src/README_LLM_WRAPPER.md)
- [Opik Integration](src/OPIK_INTEGRATION.md)
- [Quick Start](QUICKSTART_OPIK.md)

### Examples
- [Basic Usage](src/example_llm_usage.py)
- [RAG with Opik](src/example_rag_with_opik.py)
- [Jupyter Notebook](src/notebooks/llm_wrapper_example.ipynb)

### External Links
- [Opik Documentation](https://www.comet.com/docs/opik/)
- [LangChain Documentation](https://python.langchain.com/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## Support

For issues or questions:
1. Check documentation in `src/README_LLM_WRAPPER.md`
2. Review examples in `src/example_*.py`
3. Check Opik documentation
4. Verify Azure OpenAI configuration

## Summary

You now have a **production-ready LLM wrapper** with:

✅ Azure OpenAI integration
✅ Automatic Opik tracing
✅ Simple, clean API
✅ Comprehensive documentation
✅ Working examples
✅ Full observability

**Get started in 5 minutes**: See [QUICKSTART_OPIK.md](QUICKSTART_OPIK.md)

---

**All LLM calls are now automatically traced and observable!** 🚀
