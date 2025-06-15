import os
import json
from datetime import datetime
from fastmcp import FastMCP
from agents import RunContextWrapper
from dataclasses import dataclass


mcp = FastMCP(
    name="CalendarAssistant",
)


@dataclass
class ChatContext:
    history: list[str]


# get the run context
@mcp.tool(name="fetch_conversation_history")
async def fetch_conversation_history(
    wrapper: RunContextWrapper[ChatContext],
) -> list[str]:
    return wrapper.context.history


# get the current time in YYYY-MM-DD
@mcp.tool()
async def get_time() -> str:
    now = datetime.now()
    return now.isoformat()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
