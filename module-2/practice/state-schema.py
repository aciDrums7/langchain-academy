from typing import Literal
from pydantic import BaseModel, field_validator, ValidationError
from dataclasses import dataclass
import random
from langgraph.graph import StateGraph, START, END
from typing import TypedDict


class TypedDictState(TypedDict):
    name: str
    mood: Literal["happy", "sad"]


@dataclass
class DataclassState:
    name: str
    mood: Literal["happy", "sad"]


#! The pydantic state is the only one capable of runtime validation error throwing!
class PydanticState(BaseModel):
    name: str
    mood: Literal["happy", "sad"]

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, mood):
        if mood not in ["happy", "sad"]:
            raise ValidationError("mood must be 'happy' or 'sad'")
        return mood


def node_1(state):
    print("---Node 1---")
    # return {"name": state["name"] + " is ... "}
    return {"name": state.name + " is ... "}


def node_2(state):
    print("---Node 2---")
    return {"mood": "happy"}


def node_3(state):
    print("---Node 3---")
    return {"mood": "sad"}


def decide_mood(state) -> Literal["node_2", "node_3"]:

    # Here, let's just do a 50 / 50 split between nodes 2, 3
    if random.random() < 0.5:

        # 50% of the time, we return Node 2
        return "node_2"

    # 50% of the time, we return Node 3
    return "node_3"


# Build graph
# builder = StateGraph(TypedDictState)
# builder = StateGraph(DataclassState)
builder = StateGraph(PydanticState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

if __name__ == "__main__":
    # ? Not throwing error
    # result = graph.invoke(TypedDictState(name="Arfio", mood="mad"))
    # ? Not throwing error
    # result = graph.invoke(DataclassState(name="Arfio", mood="mad"))
    # ! This throws error!
    result = graph.invoke(PydanticState(name="Arfio", mood="angry"))
    print(result)
