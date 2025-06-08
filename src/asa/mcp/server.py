import os
import json
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP(
    name="CalendarAssistant",
)

# get the current time in YYYY-MM-DD


@mcp.tool()
async def get_time() -> str:
    now = datetime.now()
    return now.isoformat()


# get the day's events
@mcp.tool()
async def get_events() -> str:
    return "poop"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
