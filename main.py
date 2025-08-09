"""
FastAPI wrapper for Observee SDK functions.
Provides endpoints for tool filtering, information retrieval, and execution.
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uvicorn

# Import Observee SDK functions
try:
    from observee_agents import filter_tools, get_tool_info, execute_tool
except ImportError:
    raise ImportError(
        "observee_agents package not found. Please install with: "
        "pip install mcp-agents[embedding]"
    )

app = FastAPI(
    title="Observee SDK API",
    description="FastAPI wrapper for Observee SDK tool management functions",
    version="1.0.0"
)

# Pydantic models for request/response validation
class FilterToolsRequest(BaseModel):
    query: str = Field(..., description="Query to filter tools by")
    max_tools: int = Field(default=10, ge=1, le=100, description="Maximum number of tools to return")
    filter_type: str = Field(default="local_embedding", description="Filter type (local_embedding, bm25, cloud)")
    observee_api_key: Optional[str] = Field(default=None, description="Observee API key (optional if set in env)")

class FilterToolsResponse(BaseModel):
    tools: List[Dict[str, Any]]
    count: int

class GetToolInfoRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to get information for")
    observee_api_key: Optional[str] = Field(default=None, description="Observee API key (optional if set in env)")

class GetToolInfoResponse(BaseModel):
    tool_info: Optional[Dict[str, Any]]
    found: bool

class ExecuteToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    tool_input: Dict[str, Any] = Field(..., description="Input parameters for the tool")
    observee_api_key: Optional[str] = Field(default=None, description="Observee API key (optional if set in env)")

class ExecuteToolResponse(BaseModel):
    result: Any
    success: bool
    error: Optional[str] = None

# Helper function to get API key
def get_api_key(provided_key: Optional[str] = None) -> str:
    """Get API key from request or environment variables."""
    if provided_key:
        return provided_key
    
    api_key = os.getenv("OBSERVEE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="No API key provided. Set OBSERVEE_API_KEY environment variable or provide in request."
        )
    return api_key

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Observee SDK API",
        "version": "1.0.0",
        "endpoints": {
            "filter_tools": "/filter-tools",
            "get_tool_info": "/tool-info",
            "execute_tool": "/execute-tool"
        }
    }

@app.post("/filter-tools", response_model=FilterToolsResponse)
async def filter_tools_endpoint(request: FilterToolsRequest):
    """
    Filter and find relevant tools based on a query.
    Uses local embedding filter by default for semantic search.
    """
    try:
        api_key = get_api_key(request.observee_api_key)
        
        tools = filter_tools(
            query=request.query,
            max_tools=request.max_tools,
            filter_type=request.filter_type,
            observee_api_key=api_key
        )
        
        return FilterToolsResponse(
            tools=tools,
            count=len(tools)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering tools: {str(e)}")

@app.get("/filter-tools")
async def filter_tools_get_endpoint(
    query: str = Query(..., description="Query to filter tools by"),
    max_tools: int = Query(default=10, ge=1, le=100, description="Maximum number of tools to return"),
    filter_type: str = Query(default="local_embedding", description="Filter type"),
    observee_api_key: Optional[str] = Query(default=None, description="Observee API key")
):
    """
    Filter tools using GET method for easy testing.
    """
    request = FilterToolsRequest(
        query=query,
        max_tools=max_tools,
        filter_type=filter_type,
        observee_api_key=observee_api_key
    )
    return await filter_tools_endpoint(request)

@app.post("/tool-info", response_model=GetToolInfoResponse)
async def get_tool_info_endpoint(request: GetToolInfoRequest):
    """
    Get detailed information about a specific tool.
    """
    try:
        api_key = get_api_key(request.observee_api_key)
        
        tool_info = get_tool_info(
            tool_name=request.tool_name,
            observee_api_key=api_key
        )
        
        return GetToolInfoResponse(
            tool_info=tool_info,
            found=tool_info is not None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tool info: {str(e)}")

@app.get("/tool-info/{tool_name}", response_model=GetToolInfoResponse)
async def get_tool_info_get_endpoint(
    tool_name: str,
    observee_api_key: Optional[str] = Query(default=None, description="Observee API key")
):
    """
    Get tool information using GET method.
    """
    request = GetToolInfoRequest(
        tool_name=tool_name,
        observee_api_key=observee_api_key
    )
    return await get_tool_info_endpoint(request)

@app.post("/execute-tool", response_model=ExecuteToolResponse)
async def execute_tool_endpoint(request: ExecuteToolRequest):
    """
    Execute a tool directly with provided input parameters.
    """
    try:
        api_key = get_api_key(request.observee_api_key)
        
        result = execute_tool(
            tool_name=request.tool_name,
            tool_input=request.tool_input,
            observee_api_key=api_key
        )
        
        return ExecuteToolResponse(
            result=result,
            success=True
        )
        
    except Exception as e:
        return ExecuteToolResponse(
            result=None,
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Observee SDK API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
