from operator import add
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, RemoveMessage
from langchain_core.messages import AIMessage, HumanMessage


def reduce_list(left: list | None, right: list | None) -> list:
    """Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
                If an input is None, it's treated as an empty list.
    """

    if not left:
        left = []
    if not right:
        right = []
    return left + right


class DefaultState(TypedDict):
    # ? We can specify the reducer function like this
    # ? In this case, the values returned from nodes will be appended instead of replacing the previous ones
    foo: Annotated[list[int], add]


class CustomReducerState(TypedDict):
    foo: Annotated[list[int], reduce_list]


def node_1(state):
    print("---Node 1---")
    return {"foo": [state["foo"][-1] + 1]}


def custom_node_1(state):
    print("---Custom Node 1---")
    return {"foo": [2]}


def node_2(state):
    print("---Node 2---")
    return {"foo": [state["foo"][-1] + 1]}


def node_3(state):
    print("---Node 3---")
    return {"foo": [state["foo"][-1] + 1]}


# Build graph
# builder = StateGraph(DefaultState)
builder = StateGraph(CustomReducerState)
builder.add_node("custom_node_1", custom_node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "custom_node_1")
builder.add_edge("custom_node_1", "node_2")
builder.add_edge("custom_node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# ? This calls fails because the defalt add reducer function can't handle None values
# result = graph.invoke(State(foo=[None]))
# result = graph.invoke(CustomReducerState(foo=None))
# print(result)


""" 
MESSAGES 
"""
# * Rewriting

# Initial state
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model", id="1"),
    HumanMessage(
        content="I'm looking for information on marine biology.", name="Lance", id="2"
    ),
]

# New message to add
new_message = HumanMessage(
    content="I'm looking for information on whales, specifically", name="Lance", id="2"
)

# Test
# initial_messages = add_messages(initial_messages, new_message)
# for msg in initial_messages:
#     msg.pretty_print()

# * Removing

# Message list
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Lance", id="2"))
messages.append(
    AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3")
)
messages.append(
    HumanMessage(
        "Yes, I know about whales. But what others should I learn about?",
        name="Lance",
        id="4",
    )
)

# Isolate messages to delete
delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
print(delete_messages)

# Test
# ? We use the add_messages reducer function to remove messages
messages = add_messages(messages, delete_messages)
for msg in messages:
    msg.pretty_print()
