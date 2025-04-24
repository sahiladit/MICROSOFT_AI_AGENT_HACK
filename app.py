import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AzureOpenAI

with open("prompt.txt","r") as f:
    system_prompt = f.read()



load_dotenv()
endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

if not endpoint or not deployment or not api_key:
    print("Missing keys!!!Try again")

# Set deployment model and initialize the Azure client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2025-01-01-preview",
)

@cl.step(type="tool")
async def tool():
    await cl.sleep(4)
    return "The tools response!!!"

@cl.on_chat_start
async def on_chat_start():
    # Initialize the counter at the start of a chat
    cl.user_session.set("counter", 0)

@cl.set_starters
async def set_starters():
    # Define starter buttons for the user
    return [
        cl.Starter(
            label="Public advisor agent",
            message="Seek advice about your case and learning how to approach lawyers",
            icon="/public/images.png",
        ),
        cl.Starter(
            label="Set reminder",
            message="Set reminder for upcoming hearings",
            icon="/public/reminder.png",
        ),
        cl.Starter(
            label="Documentation agent",
            message="Summarize the given legal documents please",
            icon="/public/write.svg",
        ),
        cl.Starter(
            label="Researching agent",
            message="Create a summary and report based on the input files",
            icon="/public/research.svg",
        )
    ]

@cl.on_message
async def on_message(message: cl.Message):
    print(cl.chat_context.to_openai())  # Debugging - print the current context

    # Get the counter value from the user session
    counter = cl.user_session.get("counter")
    counter += 1
    cl.user_session.set("counter", counter)

    # Call the tool (if applicable)
    tool_res = await tool()

    # Make the request to Azure OpenAI with chat-completion
    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role":"system",
                 "content":system_prompt
                },
                {'role': "user", 
                 'content': message.content
                }
            ],
        )
        # Extract the response from the completion result
        response = completion.choices[0].message.content
        # Send the response back to the user in the chat
        await cl.Message(response).send()

        # Send message about the number of messages the user has sent
        await cl.Message(content=f"You sent {counter} messages").send()
    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()

@cl.on_chat_end
async def on_chat_end():
    print("Session expired")
