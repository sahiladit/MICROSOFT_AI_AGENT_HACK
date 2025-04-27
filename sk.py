from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AzureOpenAI
import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import kernel
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
from azure.search.documents.models import QueryType
from typing import Annotated

load_dotenv()
endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
index_name_1 = os.getenv("AZURE_SEARCH_INDEX_NAME_1")
index_name_2 = os.getenv("AZURE_SEARCH_INDEX_NAME_2")
index_name_3 = os.getenv("AZURE_SEARCH_INDEX_NAME_3")

# List of index names
SEARCH_INDEXES = [index_name_1, index_name_2, index_name_3]
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2025-01-01-preview",
)


with open("prompt.txt","r") as f:
    system_prompt = f.read()
    
class Lawyer_Agent:
    @kernel_function 
    async def lawyer(self, query: Annotated[str,"The query entered by the user in the chainlit interface !!!"])->Annotated[str,"The respone from out ai agent, telling the user about the final output"]:
        try:
            search_clients = [
                SearchClient(endpoint=SEARCH_ENDPOINT,index_name=index, credential=AzureKeyCredential(SEARCH_API_KEY))
                for index in SEARCH_INDEXES
            ]
            search_result = []
            for sclient in search_clients:
                results = sclient.search(search_text=message.content,top=5,query_type=QueryType.SIMPLE)
                for result in results:
                    search_result.append(result['content'])
            retrieved = "\n".join(search_result)

            completion = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role":"system",
                    "content":system_prompt,
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
