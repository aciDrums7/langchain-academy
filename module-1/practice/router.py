from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()


# Tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# LLM with bound tool
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([multiply])


# Graph State
class GraphState(MessagesState):
    pass


# Node
def tool_calling_llm(state: GraphState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(GraphState)
builder.add_node("tool_calling_llm", tool_calling_llm)

# The ToolNode is fundamental because:
# 1. It automatically handles the execution of tools called by the LLM
# 2. It maintains the conversation history by adding tool responses as messages
# 3. It abstracts away the complexity of tool execution logic
# 4. It ensures proper formatting of tool inputs/outputs in the message history
# 5. It allows the LLM to focus on decision-making rather than tool execution details
builder.add_node("tools", ToolNode([multiply]))

builder.add_edge(START, "tool_calling_llm")

# Conditional edges are fundamental because:
# 1. They enable dynamic routing based on LLM decisions (tool use vs. direct response)
# 2. They create the "agent loop" where the LLM can decide when to use tools
# 3. They eliminate the need for hard-coded logic about when to use tools
# 4. They allow the graph to adapt to different user inputs without changing structure
# 5. They create a separation between decision-making (LLM) and execution (tools)
# 6. They enable emergent agent behavior through simple routing rules
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)

# Compile graph
graph = builder.compile()

# Run graph
if __name__ == "__main__":

    # Get user input for the initial graph state
    user_prompt = input("Enter the initial graph state: ")

    # Create a human message directly instead of an LLM response
    result = graph.invoke({"messages": [HumanMessage(content=user_prompt)]})
    for m in result["messages"]:
        m.pretty_print()
