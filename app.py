import semantic_kernel as sk
import chainlit as cl
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
)
from semantic_kernel.functions import kernel_function
from semantic_kernel.contents import ChatHistory
from semantic_kernel.kernel import KernelArguments
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

import os
import dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

dotenv.load_dotenv()


# Legal Advisor
class LegalAdvisoryPlugin:
    @kernel_function(name="legal_advise", description="Provides legal guidance and explains legal concepts")
    async def get_advise(self, query: str) -> str:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""As a legal expert, provide detailed advice on:
{query}

1. Explain relevant legal concepts  
2. Cite applicable laws/regulations  
3. Suggest potential courses of action  
4. Note important limitations  
"""
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        result = await chain.apredict(query=query)
        return result


# MAIN ORCHESTRATOR AGENT 
class MainOrchestrator:
    def __init__(self, kernel: sk.Kernel):
        self.kernel = kernel
        self.chat_llm = ChatOpenAI(model="gpt-4o", temperature=0.7) 

    async def route_message(self, message: str) -> str:
        lowered = message.lower()

        if any(keyword in lowered for keyword in ["legal", "law", "court", "divorce", "contract"]):
            return await self.kernel.invoke(
                plugin_name="LegalExpert",
                function_name="legal_advise",
                arguments=KernelArguments(query=message)
            )
        else:
        
            return await self._general_chat_response(message)

    async def _general_chat_response(self, message: str) -> str:
        prompt = PromptTemplate(
            input_variables=["query"],
            template="You are a helpful assistant. Respond to the user's message:\n\nUser: {query}\nAssistant:"
        )
        chain = LLMChain(llm=self.chat_llm, prompt=prompt)
        return await chain.apredict(query=message)


# Before beginning the chat , load the data of the user(like chat history)
@cl.on_chat_start
async def on_chat_start():
    kernel = sk.Kernel()

    ai_service = OpenAIChatCompletion(
        service_id="multi_agent_service",
        ai_model_id="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    kernel.add_service(ai_service)

    kernel.add_plugin(LegalAdvisoryPlugin(), plugin_name="LegalExpert")

    cl.user_session.set("chat_history", ChatHistory())
    cl.user_session.set("kernel", kernel)


# This is for normal interaction between user and the system
@cl.on_message
async def on_message(message: cl.Message):
    kernel: sk.Kernel = cl.user_session.get("kernel")
    chat_history: ChatHistory = cl.user_session.get("chat_history")
    orchestrator = MainOrchestrator(kernel)

    chat_history.add_user_message(message.content)
    response = cl.Message(content="")

    try:
        result = await orchestrator.route_message(message.content)
        response.content = result
    except Exception as e:
        response.content = f" Error while processing your request:\n{e}"

    chat_history.add_assistant_message(response.content)
    await response.send()
