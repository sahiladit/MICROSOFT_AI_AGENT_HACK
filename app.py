import requests
import os
import chainlit as cl
import openai

# Ensure that API keys and Azure endpoint are available
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
INDIAN_KANOON_API_KEY = os.environ.get("INDIAN_KANOON_API_KEY")

# Configure OpenAI (Azure) API
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT

def query_openai(user_query):
    try:
        # Generate a summary using Azure OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can choose a different model if necessary
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please assist with the following query: {user_query}. Provide a concise summary with key points and relevant sections of the law."}
            ]
        )

        # Extract the response text from the chat response
        summary = response['choices'][0]['message']['content']
        
        return {"summary": summary}

    except Exception as e:
        print(f"Error querying OpenAI API: {str(e)}")
        return {"error": f"An exception occurred: {str(e)}"}

def get_kanoon_info(query):
    try:
        # Kanoon API endpoint
        kanoon_api_endpoint = "https://kanoonapi.com/v1/search"
        headers = {
            "Authorization": f"Bearer {INDIAN_KANOON_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {"query": query}
        response = requests.post(kanoon_api_endpoint, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for any non-2xx responses
        
        return {"result": response.json()}  # Return JSON data from Kanoon API
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Kanoon information: {str(e)}")
        return {"error": f"An exception occurred: {str(e)}"}

@cl.on_message
async def on_message(message: cl.Message):
    # Extract the message content
    message_content = message.content

    # Generate a summary of the query using OpenAI (Azure) API
    openai_response = query_openai(message_content)
    
    # Check if there was an error in OpenAI response
    if "error" in openai_response:
        await cl.Message(content="Sorry, there was an issue processing your request.").send()
        return

    # Use the summarized query to fetch legal information from Kanoon
    kanoon_info = get_kanoon_info(openai_response["summary"])

    # Check if Kanoon API returned an error
    if "error" in kanoon_info:
        await cl.Message(content="Sorry, there was an issue retrieving legal information.").send()
        return
    
    # Send the legal information back to the user
    await cl.Message(content=f"Here is the information from Kanoon: {kanoon_info['result']}").send()

if __name__ == "__main__":
    # Run the Chainlit bot
    cl.run()
