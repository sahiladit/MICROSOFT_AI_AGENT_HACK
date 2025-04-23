import chainlit as cl
from agents.langgraph_agent import langgraph_agent

@cl.on_chat_start
def start():
    cl.user_session.set("state", {"messages": [], "language": "auto"})
    return cl.Message("Hello! Ask your Indian legal questions in English or Hindi.").send()

@cl.on_message
def handle_message(msg: cl.Message):
    state = cl.user_session.get("state")
    state['messages'].append({"role": "user", "content": msg.content})
    new_state = langgraph_agent.invoke(state)
    reply = new_state['messages'][-1]['content']
    cl.user_session.set("state", new_state)
    return cl.Message(reply).send()