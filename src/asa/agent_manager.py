import os
import asyncio
import shutil
import subprocess
import time
from typing import Any

from dataclasses import dataclass
from agents import (
    Agent,
    Model,
    RunContextWrapper,
    Runner,
    function_tool,
    gen_trace_id,
    trace,
)
from dotenv import load_dotenv
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings

# get the API key from the .env file
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
NOTI_PROMPT = os.getenv("NOTI_PROMPT")
NOTI_DESCRIPTION = os.getenv("NOTI_DESCRIPTION")

# holds the conversation history to provide Asa with past context
@dataclass
class ChatContext:
    history: list[str]


#### Base Asa tools ####
# get the run context
@function_tool
async def fetch_conversation_history(
    wrapper: RunContextWrapper[ChatContext],
) -> list[str]:
    print("getting conversation history")
    return wrapper.context.history


#### Noti asa tools ####
# send discord noti, most likely have to take a credential as its parameter
# and return a success or failure boolean; or a HTTP status message
@function_tool
async def send_discord_noti():
    print("Send discord tool has been invoked!")
    pass

# send a gmail noti; will also most likely take a credential as its parameter
# and return a success or failure boolean; or a HTTP status message
@function_tool
async def send_gmail_noti():
    print("Send gmail tool has been invoked!")


# Going to create my own MCP server to expose required APIs
# like google calendar, slack,
async def run(mcp_server: MCPServer):
    # send notifications to the user through email and SMS
    notification_agent = Agent(
        name="noti_asa", 
        instructions=NOTI_PROMPT, 
        tools=[
            send_discord_noti,
            send_gmail_noti
        ],
        model="gpt-4.1-nano"
    )

    base_agent = Agent(
        name="Asa",
        instructions=SYSTEM_PROMPT,
        model="gpt-4.1-nano",
        tools=[
            fetch_conversation_history,
        ],
        handoffs=[notification_agent],
        handoff_description=NOTI_DESCRIPTION,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    chat_history_list = []

    while True:
        print("=" * 150)
        user_input = input("Schedule anything...\n")
        if user_input in ("exit", "goodbye"):
            print("Goodbye!")
            break
        chat_history_list.append(user_input)

        chat_context = ChatContext(history=chat_history_list)

        result = await Runner.run(
            starting_agent=base_agent,
            input=user_input,
            context=chat_context,
        )

        print(result.final_output)
        result.to_input_list()


async def main():
    async with MCPServerStreamableHttp(
        name="Asa MCP (Streamable HTTP)",
        params={
            "url": "http://localhost:8000/mcp",
            "headers": {
                "Accept": "application/json, text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Streamable HTTP Example", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={
                    trace_id
                }\n"
            )
            await run(server)


if __name__ == "__main__":
    if not shutil.which("uv"):
        raise RuntimeError("uv not installed.")

    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "mcp/server.py")

        print("Starting Streamable HTTP server at http://localhost:8000/mcp/ ...")

        process = subprocess.Popen(["uv", "run", server_file])
        # give it 3 seconds to Start
        time.sleep(3)

        print("Streamable HTTP server started.")
    except Exception as e:
        print(f"Error starting streamable HTTP server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
