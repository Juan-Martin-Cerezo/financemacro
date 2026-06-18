"""
Hermes AI Agent — ReAct loop using LangChain + LangGraph.

Tools:
  - get_financial_context: GET /api/v1/hermes/financial-context
  - allocate_funds:       POST /api/v1/hermes/execute-action

Auth: Bearer token from HERMES_API_KEY env var.
"""

import os
from typing import Annotated, Any

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from typing_extensions import TypedDict

load_dotenv()

BASE_URL = os.getenv("HERMES_BASE_URL", "http://localhost:8000/api/v1/hermes")
API_KEY = os.getenv("HERMES_API_KEY")
if not API_KEY:
    raise RuntimeError("HERMES_API_KEY not set in environment")

HEADERS = {"Authorization": f"Bearer {API_KEY}"}


# ── Tools ────────────────────────────────────────────────────────────────────


@tool
def get_financial_context() -> dict[str, Any]:
    """Fetch financial summary (totals + recent transactions) from the backend."""
    resp = httpx.get(f"{BASE_URL}/financial-context", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


@tool
def allocate_funds(envelope_id: str, amount: float) -> dict[str, Any]:
    """Allocate a positive amount of funds to a specific envelope by its UUID."""
    payload = {
        "action": "allocate_funds",
        "params": {"envelope_id": envelope_id, "amount": str(amount)},
    }
    resp = httpx.post(
        f"{BASE_URL}/execute-action",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


tools = [get_financial_context, allocate_funds]
tool_executor = ToolExecutor(tools)


# ── Graph state ──────────────────────────────────────────────────────────────


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ── Nodes ────────────────────────────────────────────────────────────────────


def should_continue(state: AgentState) -> str:
    """Decide whether to run another tool or return the final answer."""
    last = state["messages"][-1]
    return "continue" if last.tool_calls else "end"


def call_model(state: AgentState):
    llm = ChatOpenAI(
        model=os.getenv("HERMES_LLM_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
    ).bind_tools(tools)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


async def call_tool(state: AgentState):
    last = state["messages"][-1]
    tool_invocations = []
    for tc in last.tool_calls:
        tool_invocations.append(
            ToolInvocation(tool=tc["name"], tool_input=tc["args"])
        )
    results = await tool_executor.abulk(tool_invocations)
    return {
        "messages": [
            {"role": "tool", "content": str(r), "tool_call_id": tc["id"]}
            for r, tc in zip(results, last.tool_calls)
        ]
    }


# ── Build graph ──────────────────────────────────────────────────────────────


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")

app = workflow.compile()


# ── CLI entrypoint ───────────────────────────────────────────────────────────


def main():
    import sys

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How is my financial status?"
    print(f"🤖 Hermes Agent — question: {question}\n")

    inputs = {"messages": [{"role": "user", "content": question}]}

    for chunk in app.stream(inputs):
        for node, values in chunk.items():
            if node == "agent" and values.get("messages"):
                msg = values["messages"][-1]
                if msg.content:
                    print(f"\n  {msg.content}\n")


if __name__ == "__main__":
    main()
