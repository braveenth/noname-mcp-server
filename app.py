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
    
    # Since the agent's response is a JSON string, we need to parse it
    # to fit into the SearchResponse schema.
    # This is a simplified approach; a more robust solution would handle parsing errors.
    try:
        search_response_data = json.loads(agent_response)
        if isinstance(search_response_data, dict):
            # If the agent returns a message, use it as the summary
            if 'message' in search_response_data and 'summary' not in search_response_data:
                search_response_data['summary'] = search_response_data.pop('message')
            
            # If there's still no summary, the SearchResponse constructor will fail
            # and we'll fall into the except block.
            
        search_response = SearchResponse(**search_response_data)
    except (json.JSONDecodeError, TypeError, ValidationError):
        # If parsing or validation fails, treat the entire response as a summary
        search_response = SearchResponse(summary=agent_response)

    return MCPResponse(data=search_response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)