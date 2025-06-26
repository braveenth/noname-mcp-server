import uvicorn
from fastapi import FastAPI
from typing import List
from langgraph.graph import END
from product_search.agent import abot
from product_search.schema import MCPRequest, MCPResponse, SearchResponse, ToolDefinition
from product_search.tools import tool_definitions
import json
from pydantic import ValidationError

app = FastAPI()

@app.get("/tools/list", response_model=List[ToolDefinition])
async def list_tools():
    return tool_definitions

@app.post("/mcp", response_model=MCPResponse)
async def run_agent(request: MCPRequest):
    messages = [("user", request.query)]
    result = abot.graph.invoke({"messages": messages})
    
    # Extract the response from the agent's final state
    agent_response = result['messages'][-1].content
    
    # The agent's response is now expected to be a JSON string that maps directly
    # to the SearchResponse schema.
    try:
        # Parse the JSON string from the agent's response
        search_response_data = json.loads(agent_response)

        # If the agent returns a list of products, it's from a direct tool call.
        # We'll construct the SearchResponse with a default summary.
        if isinstance(search_response_data, list):
            search_response = SearchResponse(
                products=search_response_data,
                summary="Found products."
            )
        # If the agent returns a dictionary, it should match the SearchResponse schema.
        elif isinstance(search_response_data, dict):
            # If 'products' is not in the response, set it to None
            if 'products' not in search_response_data:
                search_response_data['products'] = None
            
            # If 'summary' is not in the response, create a default one
            if 'summary' not in search_response_data:
                search_response_data['summary'] = "No summary provided."
            
            search_response = SearchResponse(**search_response_data)
        else:
            # If the response is neither a list nor a dict, treat it as a summary.
            search_response = SearchResponse(summary=str(agent_response))

    except (json.JSONDecodeError, TypeError, ValidationError) as e:
        # If parsing or validation fails, treat the entire response as a summary
        search_response = SearchResponse(summary=f"Error parsing agent response: {agent_response}")

    return MCPResponse(data=search_response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)