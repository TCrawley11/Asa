from agents import Agent, Runner
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

agent = Agent(name="Asa", instructions="You are a scheduling assistant, specializing in summarizing a user's tasks, and optimizing their schedule")
            
result = Runner.run_sync(agent, "Say hello to Tokyo.")
print(result.final_output)

