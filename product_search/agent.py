import operator
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from .graph import tools

# The agent state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# The agent
class Agent:
    def __init__(self, model, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", ToolNode(tools))
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {"action": "action", "__end__": END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        if len(result.tool_calls) > 0:
            return "action"
        return "__end__"

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [("system", self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}


# Create the agent
prompt = """You are a smart research assistant. Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are asked to do so. \
When you receive search results, they will be in a JSON format. Your task is to interpret these results and provide a concise summary. \
If the user asks for a link, use the 'product_search_with_links' or 'similar_products_search_with_links' tool. \
If the user does not ask for a link, use the 'product_search' or 'similar_products_search' tool. \
If no products are found, you should indicate that in your summary.
Only returning the JSON data, without any additional text or explanation."""

model = ChatOpenAI(model="gpt-4")
abot = Agent(model, system=prompt)