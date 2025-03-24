import os

from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def AsaCLI():
    messages = []

    print("Asa, the groq-powered assistant.")
    print("================================")

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
            print(f"/nAsa: {response}")

            messages.append({"role": "assitant", "content": response})

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    AsaCLI()

