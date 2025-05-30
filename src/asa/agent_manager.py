from dataclasses import dataclass
from agents import Agent, RunContextWrapper, Runner, function_tool
from dotenv import load_dotenv
import os
import asyncio

# get the API key from the .env file
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")


# will change this later to vector store so that it is multi conversational
@dataclass
class ChatContext:
    history: list


@function_tool
async def fetch_conversation_history(wrapper: RunContextWrapper[ChatContext]) -> list:
    return wrapper.context.history


planner_agent = Agent(
    name="Asa",
    instructions="You are a scheduling assistant. Your job is to list the"
    "tasks and events of the {{ user }} in the defined {{ date_range }}"
    "in a clear and concise manner. You should also provide insights as"
    "to how best complete said tasks. You are also responsible for"
    "adding and removing tasks from the users schedule when prompted by"
    "interacting with the provided google calendar tools.",
    model="gpt-4.1-nano",
    tools=[fetch_conversation_history],
)

# send notifications to the user through email and SMS
notification_agent = Agent(
    name="noti_asa", instructions="", model="gpt-4.1-nano")


async def main():
    context = ChatContext(history=[])
    while True:
        user_input = input("Schedule anything...\n")
        if user_input in ("exit", "goodbye"):
            print("Goodbye!")
            break
        context.history.append(user_input)

        result = await Runner.run(
            starting_agent=planner_agent, input=user_input, context=context
        )

        print(result.final_output)
        result.to_input_list()


if __name__ == "__main__":
    asyncio.run(main())
