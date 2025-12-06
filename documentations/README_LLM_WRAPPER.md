# Azure LLM Wrapper Documentation

A reusable LangChain wrapper for Azure OpenAI services that simplifies configuration and usage across your project.

## Features

- Easy configuration through environment variables
- **Automatic Opik tracing and observability** 🆕
- Singleton pattern for efficient resource usage
- Support for both Chat LLM and Embeddings
- Azure Document Intelligence integration
- Type hints for better IDE support
- Validation of required configurations
- Production-ready with comprehensive monitoring

## Setup

### 1. Create your `.env` file

Copy the `.env.example` file to `.env` and fill in your Azure credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-api-key
AZURE_OPENAI_API_VERSION=2024-02-01

AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1-mini
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME=text-embedding-3-large
```

### 2. Install required dependencies

```bash
pip install -r requirements.txt

# Or manually:
pip install langchain-openai python-dotenv opik
```

### 3. (Optional) Start Opik for Tracing

For observability and tracing:

```bash
cd opik
powershell -ExecutionPolicy ByPass -c ".\opik.ps1"

# Access Opik UI at: http://localhost:5173
```

## Usage

> **Note**: With Opik tracing enabled, all LLM calls are automatically logged to your Opik dashboard for observability!

### Quick Start (Convenience Functions)

The simplest way to use the wrapper:

```python
from llm_wrapper import get_chat_llm, get_embeddings

# Get a chat LLM
llm = get_chat_llm(temperature=0.7, max_tokens=1000)
response = llm.invoke("What is AI?")
print(response.content)

# Get embeddings
embeddings = get_embeddings()
vector = embeddings.embed_query("Sample text")
```

### Class-Based Usage

For more control:

```python
from llm_wrapper import AzureLLMWrapper

# Initialize wrapper (loads from .env automatically)
wrapper = AzureLLMWrapper()

# Get chat LLM with custom parameters
llm = wrapper.get_chat_llm(
    temperature=0.5,
    max_tokens=500,
    top_p=0.9
)

# Get embeddings
embeddings = wrapper.get_embeddings()
```

### Using with LangChain Messages

```python
from llm_wrapper import get_chat_llm
from langchain.schema import HumanMessage, SystemMessage

llm = get_chat_llm(temperature=0.7)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is the capital of France?")
]

response = llm.invoke(messages)
print(response.content)
```

### Using with RAG (Retrieval-Augmented Generation)

```python
from llm_wrapper import get_chat_llm, get_embeddings
from langchain_postgres import PGVector

# Get embeddings
embeddings = get_embeddings()

# Create vector store
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="my_collection",
    connection="postgresql+psycopg://user:pass@localhost:5432/db",
)

# Add documents
vector_store.add_documents(documents)

# Create retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Get LLM
llm = get_chat_llm(temperature=0.7)

# Query with context
user_query = "What are the technical specifications?"
context_docs = retriever.invoke(user_query)
context = ' '.join([doc.page_content for doc in context_docs])

prompt = f"User Query: {user_query}\n\nContext: {context}"
response = llm.invoke(prompt)
print(response.content)
```

### Custom Configuration Path

```python
from llm_wrapper import AzureLLMWrapper

# Specify custom .env file location
wrapper = AzureLLMWrapper(env_file='/path/to/custom/.env')
llm = wrapper.get_chat_llm()
```

### Using with LangChain Chains

```python
from llm_wrapper import get_chat_llm
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

llm = get_chat_llm(temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

chain = prompt | llm

response = chain.invoke({"input": "Tell me about AI"})
print(response.content)
```

### Azure Document Intelligence

```python
from llm_wrapper import AzureLLMWrapper
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

wrapper = AzureLLMWrapper()
endpoint, key = wrapper.get_document_intelligence_config()

loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=endpoint,
    api_key=key,
    file_path="document.pdf",
    api_model="prebuilt-layout"
)

documents = loader.load()
```

## Configuration Options

### Chat LLM Parameters

- `temperature` (float, 0-2): Controls randomness. Lower = more deterministic
- `max_tokens` (int): Maximum tokens to generate
- `top_p` (float): Nucleus sampling parameter
- `frequency_penalty` (float): Penalize frequent tokens
- `presence_penalty` (float): Penalize tokens based on presence

### Embeddings Parameters

- `chunk_size` (int): Number of texts to embed at once
- `max_retries` (int): Maximum retry attempts

## Error Handling

```python
from llm_wrapper import AzureLLMWrapper

try:
    wrapper = AzureLLMWrapper()
    llm = wrapper.get_chat_llm()
except ValueError as e:
    print(f"Configuration error: {e}")
    # Handle missing or invalid configuration
```

## Opik Tracing and Observability

The wrapper includes **automatic Opik tracing** for comprehensive observability:

```python
from llm_wrapper import get_chat_llm, AzureLLMWrapper

# Check if tracing is enabled
wrapper = AzureLLMWrapper()
if wrapper.is_tracing_enabled():
    print("✓ Opik tracing active!")
    print(f"Dashboard: http://localhost:5173")

# All calls are automatically traced
llm = get_chat_llm()
response = llm.invoke("Your query")

# View traces in Opik dashboard!
```

### What Gets Traced

- All LLM invocations
- Input prompts and output responses
- Token usage and costs
- Execution time and latency
- Model parameters (temperature, max_tokens, etc.)
- Custom metadata and tags

### Disable Tracing

To disable tracing:

**In `.env`:**
```env
OPIK_ENABLED=false
```

**Or in code:**
```python
wrapper = AzureLLMWrapper(enable_tracing=False)
```

### Learn More

- [Complete Opik Integration Guide](OPIK_INTEGRATION.md)
- [Quick Start with Opik](../QUICKSTART_OPIK.md)
- [RAG Example with Tracing](example_rag_with_opik.py)

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Yes | API key for authentication |
| `AZURE_OPENAI_API_VERSION` | No | API version (default: 2024-02-01) |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | No | Chat model deployment name |
| `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME` | No | Embeddings deployment name |
| `AZURE_OPENAI_CHAT_MODEL_NAME` | No | Chat model name |
| `AZURE_OPENAI_EMBEDDINGS_MODEL_NAME` | No | Embeddings model name |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | No | Document Intelligence endpoint |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | No | Document Intelligence API key |
| `OPIK_URL_OVERRIDE` | No | Opik server URL (default: http://localhost:5173/api) |
| `OPIK_WORKSPACE` | No | Opik workspace (default: default) |
| `OPIK_PROJECT_NAME` | No | Opik project name (default: customer-support) |
| `OPIK_API_KEY` | No | Opik API key (empty for self-hosted) |
| `OPIK_ENABLED` | No | Enable/disable tracing (default: true) |

## Best Practices

1. **Never commit `.env` files**: Add `.env` to your `.gitignore`
2. **Use singleton pattern**: The convenience functions automatically use a singleton
3. **Set appropriate timeouts**: For production, configure request timeouts
4. **Handle rate limits**: Implement retry logic for production use
5. **Monitor costs**: Track token usage in production environments

## Integration with Existing Code

To migrate existing code to use the wrapper:

### Before:
```python
import os
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://...'
os.environ['AZURE_OPENAI_API_KEY'] = 'key'

from langchain_openai import AzureChatOpenAI
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1-mini",
    model="gpt-4.1-mini",
    temperature=0.7,
    max_tokens=1000
)
```

### After:
```python
from llm_wrapper import get_chat_llm

llm = get_chat_llm(temperature=0.7, max_tokens=1000)
```

## Troubleshooting

### Issue: "Missing required Azure OpenAI configuration"
- Ensure `.env` file exists in the project root or parent directory
- Verify `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` are set

### Issue: Authentication errors
- Check that your API key is valid and not expired
- Verify the endpoint URL is correct
- Ensure your Azure subscription is active

### Issue: Model not found
- Verify deployment names match those in Azure Portal
- Check that models are deployed in your Azure resource

## Examples Directory Structure

```
project/
├── .env                    # Your environment variables (not in git)
├── .env.example           # Template for environment variables
├── src/
│   ├── llm_wrapper.py     # The wrapper module
│   └── notebooks/
│       └── example.ipynb  # Usage examples
```

## Support

For issues or questions:
1. Check Azure OpenAI documentation
2. Review LangChain documentation
3. Check your Azure resource configuration in Azure Portal
