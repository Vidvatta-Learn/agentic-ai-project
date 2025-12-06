"""
FastAPI Application for Supervisor Agent

This module provides REST API endpoints for:
1. POST /query - Query the supervisor agent
2. POST /feedback - Resume interrupted conversations with human feedback
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from supervisor_agent import initialize_supervisor

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Supervisor API",
    description="API for interacting with the multi-agent customer support system",
    version="1.0.0"
)

# Initialize supervisor agent globally
supervisor = None


@app.on_event("startup")
async def startup_event():
    """Initialize supervisor agent on startup"""
    global supervisor
    supervisor = initialize_supervisor(use_opik=False)
    print("Supervisor agent initialized successfully")


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    thread_id: Optional[str] = "default"

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the technical specifications of the product?",
                "thread_id": "user123"
            }
        }


class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint"""
    feedback: str
    thread_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "feedback": "We do not support this query",
                "thread_id": "user123"
            }
        }


class QueryResponse(BaseModel):
    """Response model for query and feedback endpoints"""
    response: str
    thread_id: str
    interrupted: bool
    interrupt_details: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "response": "The product features a 10.3-inch display...",
                "thread_id": "user123",
                "interrupted": False,
                "interrupt_details": None
            }
        }


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Query the supervisor agent with a user question.

    The supervisor will route the query to the appropriate agent:
    - RAG Agent: For product-related queries
    - SQL Agent: For database/transaction queries
    - Human Feedback: For out-of-scope queries

    Args:
        request: QueryRequest with query text and thread_id

    Returns:
        QueryResponse with the agent's response or interrupt details
    """
    try:
        response = supervisor.query(request.query, thread_id=request.thread_id)

        # Check if interrupted for human feedback
        if '__interrupt__' in response:
            interrupt_info = response['__interrupt__'][0].value if response['__interrupt__'] else {}
            return QueryResponse(
                response="Query requires human feedback",
                thread_id=request.thread_id,
                interrupted=True,
                interrupt_details=interrupt_info
            )

        # Extract response content
        content = supervisor.get_response_content(response)

        return QueryResponse(
            response=content,
            thread_id=request.thread_id,
            interrupted=False,
            interrupt_details=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/feedback", response_model=QueryResponse)
async def provide_feedback(request: FeedbackRequest):
    """
    Resume an interrupted conversation by providing human feedback.

    Use this endpoint when a query was interrupted and requires human input.

    Args:
        request: FeedbackRequest with feedback text and thread_id

    Returns:
        QueryResponse with the final agent response
    """
    try:
        response = supervisor.resume_with_feedback(
            request.feedback,
            thread_id=request.thread_id
        )

        # Extract response content
        content = supervisor.get_response_content(response)

        return QueryResponse(
            response=content,
            thread_id=request.thread_id,
            interrupted=False,
            interrupt_details=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "supervisor_initialized": supervisor is not None
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Customer Support Supervisor API",
        "endpoints": {
            "POST /query": "Query the supervisor agent",
            "POST /feedback": "Provide human feedback for interrupted queries",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }


def main():
    """Run the FastAPI application"""
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()