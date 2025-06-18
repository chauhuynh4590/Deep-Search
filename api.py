"""
api.py
--------
FastAPI application providing endpoints for research queries and health checks.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import run_research
from typing import Any

app = FastAPI(title="Deep Research API", description="API for running research queries.", version="1.0.0")

class QueryRequest(BaseModel):
    """Request model for research queries."""
    input: str

class QueryResponse(BaseModel):
    """Response model for research queries."""
    result: Any

class StatusResponse(BaseModel):
    """Response model for API status check."""
    status: str

@app.post("/query", response_model=QueryResponse, summary="Run a research query", response_description="Result of the research query")
async def query_endpoint(request: QueryRequest) -> QueryResponse:
    """
    Accepts a research query and returns the result.
    """
    try:
        result = run_research(request.input)
        return QueryResponse(result=result)
    except Exception as e:
        # Log the exception here if logging is set up
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/status", response_model=StatusResponse, summary="API Status", response_description="API health status")
def status() -> StatusResponse:
    """
    Health check endpoint to verify API is running.
    """
    return StatusResponse(status="ok")
