# Customer Support Project with Azure OpenAI & Opik

A production-ready customer support system powered by Azure OpenAI with comprehensive observability through Opik tracing.

## Features

🚀 **Azure OpenAI Integration**
- Chat models (GPT-4.1-mini)
- Text embeddings (text-embedding-3-large)
- Azure Document Intelligence
- Reusable LangChain wrapper

📊 **Opik Observability**
- Automatic tracing of all LLM calls
- Token usage and cost tracking
- Latency monitoring
- Self-hosted dashboard

🔧 **Developer Experience**
- Simple, clean API
- Type-safe with hints
- Environment-based configuration
- Comprehensive documentation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Your `.env` file is already configured! ✅

To make changes, edit `.env`:
```env
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
OPIK_ENABLED=true
```

### 3. (Optional) Start Opik

For observability and tracing:

```bash
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"
```

Access dashboard at: [http://localhost:5173](http://localhost:5173)

### 4. Test Setup

```bash
python test_setup.py
```

This will verify:
- All dependencies installed
- Environment configured correctly
- Azure OpenAI connection works
- Opik tracing functional (if enabled)

### 5. Try Examples

**Basic usage:**
```bash
python src/example_llm_usage.py
```

**RAG pipeline with tracing:**
```bash
python src/example_rag_with_opik.py
```

## Usage

### Simple Chat

```python
from llm_wrapper import get_chat_llm

llm = get_chat_llm(temperature=0.7)
response = llm.invoke("What is AI?")
print(response.content)

# Automatically traced to Opik! ✨
```

### Embeddings

```python
from llm_wrapper import get_embeddings

embeddings = get_embeddings()
vector = embeddings.embed_query("Sample text")
```

### RAG Pipeline

```python
import opik
from llm_wrapper import get_chat_llm, get_embeddings

@opik.track()
def rag_pipeline(query: str):
    # Retrieve context
    embeddings = get_embeddings()
    context = retrieve_context(query, embeddings)

    # Generate answer
    llm = get_chat_llm()
    response = llm.invoke(f"Context: {context}\n\nQuery: {query}")

    return response.content

# Fully traced with metrics!
answer = rag_pipeline("What are the technical specs?")
```

## Project Structure

```
.
├── README.md                    # This file
├── QUICKSTART_OPIK.md          # 5-minute quick start
├── PROJECT_SUMMARY.md          # Detailed project summary
├── test_setup.py               # Setup verification script
├── .env                        # Your configuration ✓
├── .env.example               # Configuration template
├── requirements.txt           # Python dependencies
│
├── src/
│   ├── llm_wrapper.py         # Main wrapper module ⭐
│   ├── README_LLM_WRAPPER.md  # Complete documentation
│   ├── OPIK_INTEGRATION.md    # Opik integration guide
│   ├── example_llm_usage.py   # Basic examples
│   ├── example_rag_with_opik.py  # RAG examples ⭐
│   │
│   └── notebooks/
│       ├── pdf_parsing.ipynb              # Original notebook
│       └── llm_wrapper_example.ipynb      # Example notebook
│
└── opik/                      # Self-hosted Opik
```

## Documentation

### Getting Started
- **[Quick Start](QUICKSTART_OPIK.md)** - Get running in 5 minutes
- **[Project Summary](PROJECT_SUMMARY.md)** - Comprehensive overview

### Detailed Guides
- **[LLM Wrapper Documentation](src/README_LLM_WRAPPER.md)** - Complete wrapper guide
- **[Opik Integration](src/OPIK_INTEGRATION.md)** - Tracing and observability

### Examples
- **[Basic Usage](src/example_llm_usage.py)** - 7 working examples
- **[RAG with Opik](src/example_rag_with_opik.py)** - Complete RAG pipeline
- **[Jupyter Notebook](src/notebooks/llm_wrapper_example.ipynb)** - Interactive examples

## What Gets Traced

With Opik enabled, every LLM call automatically logs:

✅ Input prompts and outputs
✅ Token usage (prompt, completion, total)
✅ Execution time and latency
✅ Model parameters (temperature, max_tokens)
✅ Cost estimation
✅ Custom metadata and tags

**View in dashboard:** [http://localhost:5173](http://localhost:5173)

## Configuration

### Azure OpenAI

Already configured in `.env`:
```env
AZURE_OPENAI_ENDPOINT=https://rushi-m9xyt0et-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=***
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1-mini
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME=text-embedding-3-large
```

### Opik Tracing

Already configured in `.env`:
```env
OPIK_URL_OVERRIDE=http://localhost:5173/api
OPIK_WORKSPACE=default
OPIK_PROJECT_NAME=customer-support
OPIK_ENABLED=true
```

To disable tracing:
```env
OPIK_ENABLED=false
```

## Examples

### Example 1: Simple Q&A

```python
from llm_wrapper import get_chat_llm

llm = get_chat_llm()
answer = llm.invoke("What is the capital of France?")
print(answer.content)
```

### Example 2: Conversation

```python
from llm_wrapper import get_chat_llm
from langchain.schema import HumanMessage, SystemMessage

llm = get_chat_llm()

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is AI?")
]

response = llm.invoke(messages)
print(response.content)
```

### Example 3: RAG with PDF

```python
import opik
from llm_wrapper import get_chat_llm, get_embeddings
from langchain_postgres import PGVector

# Setup
embeddings = get_embeddings()
vector_store = PGVector(embeddings=embeddings, ...)

@opik.track()
def answer_from_pdf(query: str):
    # Retrieve context
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    context = ' '.join([doc.page_content for doc in docs])

    # Generate answer
    llm = get_chat_llm()
    response = llm.invoke(f"Context: {context}\n\nQuery: {query}")

    return response.content

# Use it
answer = answer_from_pdf("What are the technical specifications?")
```

## Development Workflow

### 1. Code with Tracing

```python
import opik
from llm_wrapper import get_chat_llm

@opik.track()
def my_function(input_text: str) -> str:
    llm = get_chat_llm()
    result = llm.invoke(input_text)

    # Add metadata
    opik.track_metadata({"custom_field": "value"})

    return result.content
```

### 2. Run Your Code

```bash
python your_script.py
```

### 3. View Traces

Open [http://localhost:5173](http://localhost:5173)

Navigate to: **Projects** → **customer-support**

Analyze:
- Execution traces
- Token usage
- Latency metrics
- Cost estimates

### 4. Optimize

Based on Opik insights:
- Adjust temperature
- Optimize prompts
- Reduce token usage
- Improve latency

## Troubleshooting

### Issue: Dependencies not installed

```bash
pip install -r requirements.txt
```

### Issue: Azure authentication fails

Check `.env` file:
- `AZURE_OPENAI_ENDPOINT` is correct
- `AZURE_OPENAI_API_KEY` is valid

### Issue: Opik not connecting

```bash
# Start Opik
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"

# Check status
docker ps | grep opik
```

### Issue: No traces appearing

1. Verify `OPIK_ENABLED=true` in `.env`
2. Check Opik server is running
3. Refresh dashboard after a few seconds

## Testing

Run the setup verification:

```bash
python test_setup.py
```

This checks:
- ✅ Dependencies installed
- ✅ Environment configured
- ✅ Azure OpenAI connection
- ✅ LLM working
- ✅ Embeddings working
- ✅ Opik server running

## Production Deployment

### Environment Variables

Use different `.env` files for each environment:
- `.env.development`
- `.env.staging`
- `.env.production`

Load with:
```python
from llm_wrapper import AzureLLMWrapper

wrapper = AzureLLMWrapper(env_file='.env.production')
```

### Monitoring

Configure production monitoring:
1. Set up separate Opik instance
2. Configure retention policies
3. Set up cost alerts
4. Monitor token usage trends

### Security

- Never commit `.env` files (already in `.gitignore`)
- Rotate API keys regularly
- Use Azure Key Vault in production
- Implement rate limiting

## Performance Tips

### 1. Adjust Temperature

```python
# More deterministic (factual Q&A)
llm = get_chat_llm(temperature=0.2)

# More creative (content generation)
llm = get_chat_llm(temperature=1.0)
```

### 2. Control Token Usage

```python
# Limit response length
llm = get_chat_llm(max_tokens=500)
```

### 3. Optimize Prompts

Use Opik to analyze which prompts are most effective:
- Compare different phrasings
- Measure token efficiency
- Track response quality

### 4. Batch Requests

```python
queries = ["Query 1", "Query 2", "Query 3"]
responses = [llm.invoke(q) for q in queries]
```

## Resources

### Documentation
- [Quick Start Guide](QUICKSTART_OPIK.md)
- [Complete Wrapper Guide](src/README_LLM_WRAPPER.md)
- [Opik Integration](src/OPIK_INTEGRATION.md)
- [Project Summary](PROJECT_SUMMARY.md)

### Examples
- [Basic Examples](src/example_llm_usage.py)
- [RAG Pipeline](src/example_rag_with_opik.py)
- [Jupyter Notebook](src/notebooks/llm_wrapper_example.ipynb)

### External Resources
- [Opik Documentation](https://www.comet.com/docs/opik/)
- [LangChain Docs](https://python.langchain.com/)
- [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## Contributing

To add new features:

1. Update [src/llm_wrapper.py](src/llm_wrapper.py)
2. Add examples to [src/example_llm_usage.py](src/example_llm_usage.py)
3. Update documentation
4. Test with `python test_setup.py`

## License

[Your License Here]

## Support

For questions or issues:
1. Check documentation in `src/README_LLM_WRAPPER.md`
2. Review examples
3. Run `python test_setup.py`
4. Check Opik dashboard for traces

---

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Test setup
python test_setup.py

# Start Opik
cd opik && powershell -ExecutionPolicy ByPass -c ".\opik.ps1"

# Run basic examples
python src/example_llm_usage.py

# Run RAG examples
python src/example_rag_with_opik.py

# Access Opik dashboard
# http://localhost:5173
```

---

**Ready to build intelligent customer support!** 🚀

All LLM calls are automatically traced and observable through Opik.
