"""
Supervisor Agent Module

This module provides a supervisor agent that coordinates between:
1. RAG Agent - for product-related queries
2. SQL Agent - for database/transaction queries
3. Human Feedback - for queries that require human intervention

The supervisor intelligently routes queries to the appropriate agent.
"""

import sys
sys.path.append('..')

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt
from opik.integrations.langchain import OpikTracer

from llm_wrapper import get_chat_llm, get_embeddings
from pdf_parsing import VectorStoreManager, RAGAgent
from db_agent import SQLAgent


class SupervisorAgent:
    """Supervisor agent that coordinates multiple specialized agents"""

    def __init__(self, llm, rag_agent: RAGAgent, sql_agent: SQLAgent, use_opik: bool = False):
        self.llm = llm
        self.rag_agent = rag_agent
        self.sql_agent = sql_agent
        self.use_opik = use_opik
        self.agent = self._create_supervisor()
        self.tracer = None

        if self.use_opik:
            self.tracer = OpikTracer(graph=self.agent.get_graph(xray=True))

    def _create_rag_tool(self):
        """Create RAG tool for product queries"""
        rag_agent = self.rag_agent

        @tool
        def rag_tool(query: str) -> str:
            """Tool to answer product related queries using RAG agent."""
            return rag_agent.agent.invoke({'messages': [query]})['messages'][-1].content

        return rag_tool

    def _create_sql_tool(self):
        """Create SQL tool for database queries"""
        sql_agent = self.sql_agent

        @tool
        def sql_tool(query: str) -> str:
            """Tool to answer transaction questions from the user.
            This tool will generate SQL queries and respond.
            query -> str : user query ex. 'summarize the feedbacks of product with ratings less than or equal to 3.'
            """
            return sql_agent.agent.invoke({'messages': [query]})['messages'][-1].content

        return sql_tool

    def _create_human_feedback_tool(self):
        """Create human feedback tool for unhandled queries"""
        @tool
        def get_human_feedback(query: str) -> str:
            """Tool to get human feedback for queries not answered by other agents or tools."""
            response = interrupt({
                "type": "human_feedback",
                "query": query
            })
            return response

        return get_human_feedback

    def _create_supervisor(self):
        """Create supervisor agent with all tools"""
        rag_tool = self._create_rag_tool()
        sql_tool = self._create_sql_tool()
        human_feedback_tool = self._create_human_feedback_tool()

        system_prompt = (
            "You are a helpful customer support assistant. "
            "Use the available tools to answer user queries effectively. "
            "If unsure or not getting relevant response from existing tools, seek human feedback."
        )

        return create_agent(
            self.llm,
            tools=[rag_tool, sql_tool, human_feedback_tool],
            checkpointer=InMemorySaver(),
            system_prompt=system_prompt
        )

    def query(self, user_query: str, thread_id: str = "1") -> dict:
        """Query the supervisor agent"""
        config = {
            "configurable": {"thread_id": thread_id}
        }

        if self.use_opik and self.tracer:
            config["callbacks"] = [self.tracer]

        response = self.agent.invoke({
            'messages': [user_query]
        }, config=config)

        return response

    def resume_with_feedback(self, feedback: str, thread_id: str = "1") -> dict:
        """Resume interrupted conversation with human feedback"""
        config = {
            "configurable": {"thread_id": thread_id}
        }

        if self.use_opik and self.tracer:
            config["callbacks"] = [self.tracer]

        response = self.agent.invoke(
            Command(resume=feedback),
            config=config
        )

        return response

    def get_response_content(self, response: dict) -> str:
        """Extract response content from agent response"""
        if '__interrupt__' in response:
            return f"Interrupted for human feedback: {response['__interrupt__']}"
        return response['messages'][-1].content


def initialize_supervisor(use_opik: bool = False) -> SupervisorAgent:
    """Initialize supervisor agent with all components"""
    # Initialize LLM and embeddings
    llm = get_chat_llm()
    embeddings = get_embeddings()

    # Initialize RAG agent
    vector_store_manager = VectorStoreManager(
        embeddings=embeddings,
        collection_name="smart_scribble_docs"
    )
    rag_agent = RAGAgent(llm, vector_store_manager, k=3)

    # Initialize SQL agent
    sql_agent = SQLAgent(llm, dialect="Postgres", top_k=5)

    # Initialize supervisor agent
    supervisor = SupervisorAgent(llm, rag_agent, sql_agent, use_opik=use_opik)

    return supervisor


def main():
    """Main execution function"""
    # Initialize supervisor
    supervisor = initialize_supervisor(use_opik=True)

    # Example 1: Product query (uses RAG agent)
    print("\n=== Example 1: Product Query ===")
    query1 = "give me technical specifications of the product in 30 words"
    response1 = supervisor.query(query1, thread_id="1")
    print(f"Query: {query1}")
    print(f"Response: {supervisor.get_response_content(response1)}")

    # Example 2: Database query (uses SQL agent)
    print("\n=== Example 2: Database Query ===")
    query2 = "summarize the feedbacks of product with ratings less than or equal to 3"
    response2 = supervisor.query(query2, thread_id="2")
    print(f"Query: {query2}")
    print(f"Response: {supervisor.get_response_content(response2)}")

    # Example 3: Combined query (uses both agents)
    print("\n=== Example 3: Combined Query ===")
    query3 = "Provide an overview of the technical specifications and summarize customer feedback from the database"
    response3 = supervisor.query(query3, thread_id="3")
    print(f"Query: {query3}")
    print(f"Response: {supervisor.get_response_content(response3)}")

    # Example 4: Out-of-scope query (triggers human feedback)
    print("\n=== Example 4: Out-of-scope Query ===")
    query4 = "what is the weather in mumbai"
    response4 = supervisor.query(query4, thread_id="4")
    print(f"Query: {query4}")
    print(f"Response: {supervisor.get_response_content(response4)}")

    # Resume with human feedback
    if '__interrupt__' in response4:
        print("\nResuming with human feedback...")
        feedback = "We do not support this query"
        response4_resumed = supervisor.resume_with_feedback(feedback, thread_id="4")
        print(f"Final Response: {supervisor.get_response_content(response4_resumed)}")


if __name__ == "__main__":
    main()
