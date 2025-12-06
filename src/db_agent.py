"""
Database Agent Module

This module provides functionality to:
1. Connect to PostgreSQL database
2. Create SQL toolkit with database tools
3. Build an agent that can query and interact with the database using natural language
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_classic import hub
from langchain.agents import create_agent

load_dotenv()


class DatabaseConfig:
    """Manage database configuration"""

    @staticmethod
    def get_db_config() -> dict:
        """Get database configuration from environment variables"""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '6024'),
            'database': os.getenv('POSTGRES_DATABASE', 'langchain'),
            'user': os.getenv('POSTGRES_USER', 'langchain'),
            'password': os.getenv('POSTGRES_PASSWORD', 'langchain')
        }

    @staticmethod
    def get_connection_string() -> str:
        """Build PostgreSQL connection string"""
        config = DatabaseConfig.get_db_config()
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"


class DatabaseEngine:
    """Handle database engine creation and management"""

    def __init__(self):
        self.connection_string = DatabaseConfig.get_connection_string()
        self.engine = create_engine(self.connection_string, echo=False)

    def get_engine(self):
        """Get SQLAlchemy engine"""
        return self.engine

    def get_session(self):
        """Get database session"""
        Session = sessionmaker(bind=self.engine)
        return Session()


class SQLAgent:
    """SQL Agent with natural language query capabilities"""

    def __init__(self, llm, dialect: str = "Postgres", top_k: int = 5):
        self.llm = llm
        self.dialect = dialect
        self.top_k = top_k
        self.db_engine = DatabaseEngine()
        self.db = SQLDatabase(self.db_engine.get_engine())
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent = self._create_agent()

    def _get_system_prompt(self) -> str:
        """Get system prompt for SQL agent"""
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        system_message = prompt_template.format(
            dialect=self.dialect,
            top_k=self.top_k
        )
        return system_message

    def _create_agent(self):
        """Create SQL agent with toolkit"""
        system_prompt = self._get_system_prompt()
        return create_agent(
            self.llm,
            self.toolkit.get_tools(),
            system_prompt=system_prompt
        )

    def query(self, user_query: str) -> dict:
        """Query the database using natural language"""
        response = self.agent.invoke({
            'messages': [user_query]
        })
        return response

    def get_response_content(self, response: dict) -> str:
        """Extract response content from agent response"""
        return response['messages'][-1].content


def main():
    """Main execution function"""
    # Import LLM wrapper
    import sys
    sys.path.append('..')
    from llm_wrapper import get_chat_llm

    # Initialize LLM
    llm = get_chat_llm()

    # Create SQL agent
    sql_agent = SQLAgent(llm, dialect="Postgres", top_k=5)

    # Example query
    query = "list all the return order reasons"
    response = sql_agent.query(query)
    answer = sql_agent.get_response_content(response)

    print(f"Query: {query}")
    print(f"Response: {answer}")


if __name__ == "__main__":
    main()
