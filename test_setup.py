"""
Test Setup Script

This script verifies that the Azure LLM wrapper and Opik integration
are configured correctly and working as expected.
"""

import sys
import os


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)


def check_imports():
    """Check if all required packages are installed"""
    print_section("1. Checking Dependencies")

    required_packages = {
        "dotenv": "python-dotenv",
        "langchain": "langchain",
        "langchain_openai": "langchain-openai",
        "opik": "opik (optional for tracing)"
    }

    all_installed = True
    for package, display_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} - NOT INSTALLED")
            if package != "opik":
                all_installed = False

    return all_installed


def check_env_file():
    """Check if .env file exists and has required variables"""
    print_section("2. Checking Environment Configuration")

    if not os.path.exists(".env"):
        print("  ✗ .env file not found!")
        print("    Please copy .env.example to .env and configure it")
        return False

    print("  ✓ .env file exists")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = {
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI Endpoint",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API Key",
    }

    optional_vars = {
        "OPIK_URL_OVERRIDE": "Opik URL",
        "OPIK_ENABLED": "Opik Tracing Enabled",
    }

    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if "KEY" in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✓ {description}: {display_value}")
        else:
            print(f"  ✗ {description}: NOT SET")
            all_present = False

    print("\n  Optional Configuration:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {description}: {value}")
        else:
            print(f"  - {description}: not set (using defaults)")

    return all_present


def test_wrapper_initialization():
    """Test wrapper initialization"""
    print_section("3. Testing Wrapper Initialization")

    try:
        from src.llm_wrapper import AzureLLMWrapper

        wrapper = AzureLLMWrapper()

        print(f"  ✓ Wrapper initialized successfully")
        print(f"    Endpoint: {wrapper.config.endpoint[:50]}...")
        print(f"    Chat Model: {wrapper.config.chat_model}")
        print(f"    Embeddings Model: {wrapper.config.embeddings_model}")

        # Check Opik status
        if wrapper.is_tracing_enabled():
            print(f"  ✓ Opik tracing is ENABLED")
            print(f"    Project: {wrapper.config.opik_project_name}")
            print(f"    URL: {wrapper.config.opik_url}")
        else:
            print(f"  - Opik tracing is DISABLED")

        return True
    except Exception as e:
        print(f"  ✗ Wrapper initialization failed: {e}")
        return False


def test_chat_llm():
    """Test chat LLM"""
    print_section("4. Testing Chat LLM")

    try:
        from src.llm_wrapper import get_chat_llm

        print("  Creating LLM instance...")
        llm = get_chat_llm(temperature=0.7, max_tokens=100)
        print("  ✓ LLM instance created")

        print("  Invoking LLM with test query...")
        response = llm.invoke("What is AI in one sentence?")
        print(f"  ✓ LLM invocation successful")
        print(f"\n  Response: {response.content}\n")

        return True
    except Exception as e:
        print(f"  ✗ Chat LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embeddings():
    """Test embeddings"""
    print_section("5. Testing Embeddings")

    try:
        from src.llm_wrapper import get_embeddings

        print("  Creating embeddings instance...")
        embeddings = get_embeddings()
        print("  ✓ Embeddings instance created")

        print("  Generating embedding for test query...")
        query = "What is machine learning?"
        embedding = embeddings.embed_query(query)
        print(f"  ✓ Embedding generated successfully")
        print(f"    Dimension: {len(embedding)}")
        print(f"    First 5 values: {embedding[:5]}")

        return True
    except Exception as e:
        print(f"  ✗ Embeddings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_opik_server():
    """Check if Opik server is running"""
    print_section("6. Checking Opik Server")

    try:
        import requests
        from src.llm_wrapper import AzureLLMWrapper

        wrapper = AzureLLMWrapper()

        if not wrapper.config.opik_enabled:
            print("  - Opik is disabled in configuration")
            return True

        opik_ui_url = wrapper.config.opik_url.replace('/api', '')
        print(f"  Checking Opik server at: {opik_ui_url}")

        try:
            response = requests.get(opik_ui_url, timeout=5)
            if response.status_code == 200:
                print(f"  ✓ Opik server is RUNNING")
                print(f"    Access dashboard at: {opik_ui_url}")
                return True
            else:
                print(f"  ⚠ Opik server responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Cannot connect to Opik server")
            print(f"    Please start Opik with:")
            print(f"    cd opik")
            print(f"    powershell -ExecutionPolicy ByPass -c \".\\opik.ps1\"")
            return False
        except Exception as e:
            print(f"  ⚠ Error checking Opik server: {e}")
            return False

    except ImportError:
        print("  - requests package not installed (skipping Opik server check)")
        return True


def print_summary(results: dict):
    """Print test summary"""
    print_section("Test Summary")

    all_passed = all(results.values())

    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test}")

    print()
    if all_passed:
        print("  🎉 All tests passed! Setup is complete.")
        print("\n  Next steps:")
        print("  1. Run examples: python src/example_llm_usage.py")
        print("  2. Try RAG: python src/example_rag_with_opik.py")
        print("  3. Read docs: src/README_LLM_WRAPPER.md")
    else:
        print("  ⚠ Some tests failed. Please review the errors above.")
        print("\n  Common fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env file (copy from .env.example)")
        print("  3. Start Opik: cd opik && .\\opik.ps1")


def main():
    """Run all tests"""
    print("="*60)
    print("Azure LLM Wrapper - Setup Verification")
    print("="*60)

    results = {}

    # Run tests
    results["Dependencies"] = check_imports()

    if not results["Dependencies"]:
        print("\n⚠ Please install dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    results["Environment Configuration"] = check_env_file()

    if not results["Environment Configuration"]:
        print("\n⚠ Please configure .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Azure OpenAI credentials")
        sys.exit(1)

    results["Wrapper Initialization"] = test_wrapper_initialization()
    results["Chat LLM"] = test_chat_llm()
    results["Embeddings"] = test_embeddings()
    results["Opik Server"] = check_opik_server()

    # Print summary
    print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
