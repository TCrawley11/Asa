import os
from groq import Groq
from agents import Agent, Runner
import datetime, os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from qdrant_client import QdrantClient
# Import the google calendar service and create an instance of it
from services.calendar_service import CalendarService

calendar = CalendarService()

qdrant_client = QdrantClient(
    url="https://f3bced16-fc99-456d-80d6-ca95d259c351.us-east-1-0.aws.cloud.qdrant.io:6333", 
    api_key=os.environ.get("QDRANT_API_KEY"),
)

print(qdrant_client.get_collections())

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def AsaCLI():
    messages = []

    print("Hello! I'm Asa, your personal scheduling assistant.")
    print("===========================================")

    while True:
        u_input = input("What Can I help with?").strip()

        if u_input.lower() in ['exit', 'quit', 'bye']:
            break
            
        # add the messages             
        messages.append({"role": "user", "content": u_input})

        try :
            chat_completion = client.chat.completions.create(
                messages = messages,
                model="llama-3.3-70b-versatile",
            )

            response = chat_completion.choices[0].message.content
            print(f"🤖 Asa: {response}")

            messages.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    AsaCLI()

