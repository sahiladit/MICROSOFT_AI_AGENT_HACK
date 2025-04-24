import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, MessageAttachment, FilePurpose
from azure.identity import DefaultAzureCredential
import requests

# Load environment variables
load_dotenv()

# Azure setup
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.getenv('PROJECT_CONNECTION_STRING')
)

# Lawyer recommendation via Google Places API
def find_lawyer_nearby(issue_type, location):
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return "Google Places API key not set."

    query = f"{issue_type} lawyer near {location}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={api_key}"
    
    response = requests.get(url)
    results = response.json().get("results", [])
    if not results:
        return "No nearby legal help found."

    top = results[0]
    return f"{top['name']} — {top.get('formatted_address', 'Address not available')}"

# Main execution
with project_client:
    # Step 1: Upload laws and rights file
    file = project_client.agents.upload_file_and_poll(file_path='legislative_department.pdf', purpose=FilePurpose.AGENTS)
    print(f"Uploaded document, file ID: {file.id}")

    # Step 2: Create vector store
    vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="citizen_rights_vectorstore")
    print(f"Created vector store, ID: {vector_store.id}")

    # Step 3: Create file search tool
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # Step 4: Create agent
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="LegalRightsAgent",
        instructions="You are a legal assistant AI that answers user queries based ONLY on the uploaded citizen rights document.",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    print(f"Agent created, ID: {agent.id}")

    # Step 5: Thread and user query
    thread = project_client.agents.create_thread()

    user_query = input("\nEnter your legal question: ")
    location = input("Enter your city or pincode (for lawyer suggestion): ")

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_query,
        attachments=[],
    )

    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, ID: {run.id}")

    # Step 6: Print agent response
    messages = project_client.agents.list_messages(thread_id=thread.id)["data"]
    sorted_messages = sorted(messages, key=lambda x: x["created_at"])

    print("\nAgent Response:")
    for msg in sorted_messages:
        if msg["role"] == "assistant":
            content_blocks = msg.get("content", [])
            if content_blocks and content_blocks[0]["type"] == "text":
                print(content_blocks[0]["text"]["value"])

    # Step 7: Suggest a lawyer
    print("\nLawyer Suggestion:")
    print(find_lawyer_nearby(user_query, location))

    # Step 8: Clean up (optional)
    project_client.agents.delete_vector_store(vector_store.id)
    project_client.agents.delete_agent(agent.id)