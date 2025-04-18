"""
PUBLIC AND PRIVATE SCHEMAS
"""

from langgraph.graph import StateGraph, START, END

from pydantic import BaseModel


class PrivateState(BaseModel):
    baz: int


class PublicState(BaseModel):
    foo: int


def node_1(public_state: PublicState) -> PrivateState:
    print("---Node 1---")
    return PrivateState(baz=public_state.foo + 1)


def node_2(private_state: PrivateState) -> PublicState:
    print("---Node 2---")
    return PublicState(foo=private_state.baz + 1)


builder = StateGraph(PublicState)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

graph = builder.compile()

# if __name__ == "__main__":
#     result = graph.invoke(PublicState(foo=1))
#     print(result)

""" 
SCHEMA FILTERS (INPUT/OUTPUT AND OVERALL SCHEMAS) 
"""


class OverallState(BaseModel):
    question: str
    answer: str
    notes: str


class InputState(BaseModel):
    question: str


class OutputState(BaseModel):
    answer: str


def node_1(input_state: InputState) -> OverallState:
    print("---Node 1---")
    return OverallState(
        question=input_state.question,
        answer="1+1 results in 2",
        notes="bho",
    )


def node_2(overall_state: OverallState) -> OutputState:
    print("---Node 2---")
    return OutputState(answer=overall_state.answer)


builder = StateGraph(OverallState, input=InputState, output=OutputState)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(InputState(question="What is 1+1?"))
    print(result)
