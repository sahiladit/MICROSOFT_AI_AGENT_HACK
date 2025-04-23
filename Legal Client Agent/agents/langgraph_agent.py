from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from agents.semantic_skill import simplify_skill
from agents.translator import translate
from agents.retriever import qa_chain

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    language: str

def classify_input(state: ChatState):
    input_text = state["messages"][-1]['content'].lower()
    if any(term in input_text for term in ["fir", "bail", "arrest", "petition"]):
        return "faq"
    elif any(lang in input_text for lang in ["translate", "\u0939\u093f\u0902\u0926\u0940"]):
        return "translate"
    return "rag"

def translate_node(state):
    translated = translate(state['messages'][-1]['content'], to_lang="en")
    return {"messages": [{"role": "assistant", "content": translated}]}

def faq_node(state):
    question = state['messages'][-1]['content']
    # Directly use a dictionary without KernelArguments
    simplified = simplify_skill.invoke({"input": question})
    return {"messages": [{"role": "assistant", "content": simplified}]}

def rag_node(state):
    output = qa_chain.run(state['messages'][-1]['content'])
    return {"messages": [{"role": "assistant", "content": output}]}

builder = StateGraph(ChatState)
builder.add_node("faq", faq_node)
builder.add_node("rag", rag_node)
builder.add_node("translate", translate_node)
builder.set_conditional_entry_point("faq_router", classify_input)
builder.set_entry_point("faq_router")
langgraph_agent = builder.compile()
