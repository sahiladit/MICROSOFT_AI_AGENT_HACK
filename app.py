import os
import chainlit as cl
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemma-3-1b-it")

@cl.step(type="tool")
async def tool():
    await cl.sleep(4)
    return "The tools response!!!"

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("counter",0)

@cl.set_starters
async def set_starters():
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
    print(cl.chat_context.to_openai())
    counter = cl.user_session.get("counter")
    counter += 1
    cl.user_session.set("counter", counter)
    tool_res = await tool()
    response = model.generate_content(message.content)
    await cl.Message(response.text).send()
    await cl.Message(content=f"You sent {counter} . messages").send()

@cl.on_chat_end
async def on_chat_end():
   print("session expired")
