import semantic_kernel as sk
import chainlit as cl
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel import KernelArguments
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

import google.generativeai as genai
import os
import dotenv

dotenv.load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# LEGAL ADVISOR PLUGIN USING GEMINI
class LegalAdvisoryPlugin:
    @kernel_function(name="legal_advise", description="Provides legal guidance and explains legal concepts")
    async def get_advise(self, query: str) -> str:
        model = genai.GenerativeModel("gemma-3-1b-it")
        prompt = f"""As a legal expert, provide detailed advice on:
{query}

1. Explain relevant legal concepts  
2. Cite applicable laws/regulations  
3. Suggest potential courses of action  
4. Note important limitations  
"""
        response = model.generate_content(prompt)
        return response.text


# MAIN ORCHESTRATOR AGENT
class MainOrchestrator:
    def __init__(self, kernel: sk.Kernel):
        self.kernel = kernel
        self.model = genai.GenerativeModel("gemma-3-1b-it")

    async def route_message(self, message: str) -> str:
        lowered = message.lower()

        if any(keyword in lowered for keyword in ["legal", "law", "court", "divorce", "contract"]):
            result = await self.kernel.invoke(
                plugin_name="LegalExpert",
                function_name="legal_advise",
                arguments=KernelArguments(query=message)
            )
            return str(result)  # Convert FunctionResult to string to avoid JSON serialization issues
        else:
            return await self._general_chat_response(message)

    async def _general_chat_response(self, message: str) -> str:
        prompt = f"You are a helpful assistant. Respond to the user's message:\n\nUser: {message}\nAssistant:"
        response = self.model.generate_content(prompt)
        return response.text


# Load user context on chat start
@cl.on_chat_start
async def on_chat_start():
    kernel = sk.Kernel()
    kernel.add_plugin(LegalAdvisoryPlugin(), plugin_name="LegalExpert")
    cl.user_session.set("kernel", kernel)


# Process user messages during chat
@cl.on_message
async def on_message(message: cl.Message):
    kernel: sk.Kernel = cl.user_session.get("kernel")
    orchestrator = MainOrchestrator(kernel)
    response = cl.Message(content="")

    try:
        result = await orchestrator.route_message(message.content)
        response.content = result
    except Exception as e:
        response.content = f"⚠️ Error while processing your request:\n{e}"
    await response.send()
