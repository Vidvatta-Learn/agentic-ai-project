"""
Azure OpenAI LangChain Wrapper Module with Opik Tracing

This module provides reusable wrappers for Azure OpenAI services using LangChain.
It handles configuration loading from environment variables and provides
easy-to-use functions for creating LLM and embedding instances.

Features:
- Azure OpenAI LLM and Embeddings
- Opik tracing and observability integration
- Automatic tracing setup with LangChain
"""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings

try:
    import opik
    from opik.integrations.langchain import OpikTracer
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    OpikTracer = None


class AzureLLMConfig:
    """Configuration class for Azure OpenAI services"""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration by loading environment variables

        Args:
            env_file: Path to .env file. If None, searches for .env in current and parent directories
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Azure OpenAI Configuration
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')

        # Deployment Names
        self.chat_deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME', 'gpt-4.1-mini')
        self.embeddings_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME', 'text-embedding-3-large')

        # Model Names
        self.chat_model = os.getenv('AZURE_OPENAI_CHAT_MODEL_NAME', 'gpt-4.1-mini')
        self.embeddings_model = os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL_NAME', 'text-embedding-3-large')

        # Document Intelligence (Optional)
        self.doc_intel_endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.doc_intel_key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')

        # Opik Configuration
        self.opik_enabled = os.getenv('OPIK_ENABLED', 'true').lower() == 'true'
        self.opik_url = os.getenv('OPIK_URL_OVERRIDE', 'http://localhost:5173/api')
        self.opik_workspace = os.getenv('OPIK_WORKSPACE', 'default')
        self.opik_project_name = os.getenv('OPIK_PROJECT_NAME', 'customer-support')
        self.opik_api_key = os.getenv('OPIK_API_KEY', '')

        # Set environment variables for LangChain
        self._set_langchain_env_vars()

        # Configure Opik
        self._configure_opik()

    def _set_langchain_env_vars(self):
        """Set environment variables expected by LangChain"""
        if self.endpoint:
            os.environ['AZURE_OPENAI_ENDPOINT'] = self.endpoint
        if self.api_key:
            os.environ['AZURE_OPENAI_API_KEY'] = self.api_key
        if self.api_version:
            os.environ['OPENAI_API_VERSION'] = self.api_version

    def _configure_opik(self):
        """Configure Opik for tracing if enabled and available"""
        if not self.opik_enabled or not OPIK_AVAILABLE:
            return

        try:
            # Set Opik environment variables
            os.environ['OPIK_URL_OVERRIDE'] = self.opik_url
            os.environ['OPIK_WORKSPACE'] = self.opik_workspace
            os.environ['OPIK_PROJECT_NAME'] = self.opik_project_name
            if self.opik_api_key:
                os.environ['OPIK_API_KEY'] = self.opik_api_key

            # Configure Opik client
            opik.configure(
                api_key=self.opik_api_key if self.opik_api_key else None,
                url=self.opik_url,
                workspace=self.opik_workspace,
            )
            print(f"✓ Opik tracing configured for project: {self.opik_project_name}")
        except Exception as e:
            print(f"Warning: Could not configure Opik tracing: {e}")

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Missing required Azure OpenAI configuration. "
                "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in your .env file"
            )
        return True


class AzureLLMWrapper:
    """Wrapper class for Azure OpenAI LangChain integrations with Opik tracing"""

    def __init__(
        self,
        config: Optional[AzureLLMConfig] = None,
        env_file: Optional[str] = None,
        enable_tracing: bool = True
    ):
        """
        Initialize the wrapper with configuration

        Args:
            config: AzureLLMConfig instance. If None, creates new config from env_file
            env_file: Path to .env file (used only if config is None)
            enable_tracing: Enable Opik tracing (default: True, controlled by config)
        """
        self.config = config if config else AzureLLMConfig(env_file)
        self.config.validate()
        self.enable_tracing = enable_tracing and self.config.opik_enabled and OPIK_AVAILABLE
        self._opik_tracer = None

        if self.enable_tracing:
            self._init_opik_tracer()

    def _init_opik_tracer(self):
        """Initialize Opik tracer for LangChain"""
        try:
            self._opik_tracer = OpikTracer(
                project_name=self.config.opik_project_name,
                tags=["azure-openai", "langchain"]
            )
            print(f"✓ Opik tracer initialized for project: {self.config.opik_project_name}")
        except Exception as e:
            print(f"Warning: Could not initialize Opik tracer: {e}")
            self._opik_tracer = None
            self.enable_tracing = False

    def get_chat_llm(
        self,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
        **kwargs
    ) -> AzureChatOpenAI:
        """
        Get an Azure OpenAI Chat LLM instance with optional Opik tracing

        Args:
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to AzureChatOpenAI

        Returns:
            AzureChatOpenAI instance configured with Opik callbacks if enabled
        """
        # Add Opik callbacks if tracing is enabled
        if self.enable_tracing and self._opik_tracer:
            if 'callbacks' not in kwargs:
                kwargs['callbacks'] = []
            kwargs['callbacks'].append(self._opik_tracer)

        return AzureChatOpenAI(
            azure_deployment=self.config.chat_deployment,
            model=self.config.chat_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def get_embeddings(self, **kwargs) -> AzureOpenAIEmbeddings:
        """
        Get an Azure OpenAI Embeddings instance

        Args:
            **kwargs: Additional parameters to pass to AzureOpenAIEmbeddings

        Returns:
            AzureOpenAIEmbeddings instance
        """
        return AzureOpenAIEmbeddings(
            azure_deployment=self.config.embeddings_deployment,
            model=self.config.embeddings_model,
            **kwargs
        )

    def get_document_intelligence_config(self) -> tuple[str, str]:
        """
        Get Azure Document Intelligence configuration

        Returns:
            Tuple of (endpoint, api_key)

        Raises:
            ValueError if Document Intelligence is not configured
        """
        if not self.config.doc_intel_endpoint or not self.config.doc_intel_key:
            raise ValueError(
                "Azure Document Intelligence not configured. "
                "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY"
            )
        return self.config.doc_intel_endpoint, self.config.doc_intel_key

    def get_opik_tracer(self):
        """
        Get the Opik tracer instance for manual tracing

        Returns:
            OpikTracer instance or None if tracing is not enabled
        """
        return self._opik_tracer if self.enable_tracing else None

    def is_tracing_enabled(self) -> bool:
        """Check if Opik tracing is enabled"""
        return self.enable_tracing


# Convenience functions for quick access
_default_wrapper: Optional[AzureLLMWrapper] = None


def get_default_wrapper(env_file: Optional[str] = None) -> AzureLLMWrapper:
    """
    Get or create the default wrapper instance (singleton pattern)

    Args:
        env_file: Path to .env file (only used on first call)

    Returns:
        AzureLLMWrapper instance
    """
    global _default_wrapper
    if _default_wrapper is None:
        _default_wrapper = AzureLLMWrapper(env_file=env_file)
    return _default_wrapper


def get_chat_llm(
    temperature: float = 0.7,
    max_tokens: Optional[int] = 1000,
    env_file: Optional[str] = None,
    **kwargs
) -> AzureChatOpenAI:
    """
    Convenience function to get a chat LLM with default configuration

    Args:
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens to generate
        env_file: Path to .env file
        **kwargs: Additional parameters

    Returns:
        AzureChatOpenAI instance
    """
    wrapper = get_default_wrapper(env_file)
    return wrapper.get_chat_llm(temperature=temperature, max_tokens=max_tokens, **kwargs)


def get_embeddings(env_file: Optional[str] = None, **kwargs) -> AzureOpenAIEmbeddings:
    """
    Convenience function to get embeddings with default configuration

    Args:
        env_file: Path to .env file
        **kwargs: Additional parameters

    Returns:
        AzureOpenAIEmbeddings instance
    """
    wrapper = get_default_wrapper(env_file)
    return wrapper.get_embeddings(**kwargs)


# Example usage
if __name__ == "__main__":
    # Example 1: Using the wrapper class
    wrapper = AzureLLMWrapper()

    # Get a chat LLM
    llm = wrapper.get_chat_llm(temperature=0.7, max_tokens=500)
    response = llm.invoke("What is the capital of France?")
    print(f"LLM Response: {response.content}")

    # Get embeddings
    embeddings = wrapper.get_embeddings()
    query_embedding = embeddings.embed_query("What is the capital of France?")
    print(f"Embedding dimension: {len(query_embedding)}")

    # Example 2: Using convenience functions
    llm = get_chat_llm(temperature=0.5)
    embeddings = get_embeddings()

    print("Azure LLM wrapper initialized successfully!")
