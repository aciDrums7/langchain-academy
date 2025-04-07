from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtracts b from a.

    Args:
        a: first int
        b: second int
    """
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


def divide(a: int, b: int) -> float:
    """Divides a by b.

    Args:
        a: first int
        b: second int
    """
    return a / b


# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tools = [add, subtract, multiply, divide]

llm = llm.bind_tools(tools, parallel_tool_calls=False)


# System message
sys_msg = SystemMessage(
    content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
)


# Node - Assistant
def assistant(state: MessagesState):
    return {"messages": [llm.invoke([sys_msg] + state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
# Nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
# Edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")
builder.add_edge("assistant", END)

# Compile graph
graph = builder.compile()

# Run graph
if __name__ == "__main__":
    input = HumanMessage(content="how much is (((1 + 2) * 7) / 3) - 1?")
    result = graph.invoke({"messages": [input]})
    for m in result["messages"]:
        m.pretty_print()

# TODO: implement memory