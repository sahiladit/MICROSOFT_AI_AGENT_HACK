import chainlit as cl
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import googlemaps
import requests
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Initialize global variables
kernel = None
gmaps = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for FastAPI (Chainlit's underlying server)"""
    # Startup
    app.trusted_hosts = ["*"]  # Allow all proxies for testing
    yield
    # Shutdown

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@cl.on_chat_start
async def initialize_chat():
    """Initializes the chat session"""
    global kernel, gmaps
    
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            service_id="legal_advisor",
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
    )
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
    legal_plugin = kernel.add_plugin(plugin_name="LegalPlugin", parent_directory="plugins")
    cl.user_session.set("legal_plugin", legal_plugin)

async def get_user_location():
    """Get user's location from IP"""
    try:
        ip = cl.user_session.get("client").get("host")
        if ip in ["127.0.0.1", "::1"]:
            await cl.Message(content="📍 Using NYC for local testing").send()
            return "40.7128,-74.0060"
        
        response = requests.get(f"https://ipinfo.io/{ip}?token={os.getenv('IPINFO_TOKEN')}")
        data = response.json()
        if "loc" in data:
            await cl.Message(content=f"📍 Detected location: {data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}").send()
            return data["loc"]
        raise Exception("No location data")
    except Exception as e:
        await cl.Message(content=f"⚠️ Location error: {str(e)}. Using NYC").send()
        return "40.7128,-74.0060"

# Rest of your existing code...

async def get_lawyer_recommendations(coords: str):
    """Get lawyers near GPS coordinates."""
    global gmaps
    try:
        places = gmaps.places_nearby(
            location=coords,
            keyword="labor lawyer",
            radius=50000,
            type="lawyer",
        )
        top_lawyers = sorted(
            places.get("results", []), key=lambda x: x.get("rating", 0), reverse=True
        )[:3]

        if not top_lawyers:
            return "No nearby lawyers found"

        return "\n\n".join(
            f"🏛 **{lawyer['name']}** (⭐ {lawyer.get('rating', 'N/A')})\n"
            f"📍 {lawyer['vicinity']}\n"
            f"📞 {lawyer.get('international_phone_number', 'Contact not available')}"
            for lawyer in top_lawyers
        )
    except Exception as e:
        return f"⚠️ Error finding lawyers: {str(e)}"

@cl.on_message
async def handle_message(message: cl.Message):
    user_query = message.content
    
    # Get user's real location (or fallback to NYC)
    user_location = await get_user_location()

    # Process legal query
    processing_msg = await cl.Message(content="🔍 Analyzing your legal question...").send()

    try:
        legal_plugin = cl.user_session.get("legal_plugin")
        advice = await kernel.invoke(
            legal_plugin["legal_advisor"], arguments=KernelArguments(query=user_query)
        )

        decision = await kernel.invoke(
            legal_plugin["needs_lawyer_decider"],
            arguments=KernelArguments(legal_advice=str(advice), user_query=user_query),
        )

        if "YES" in str(decision).strip().upper():
            await processing_msg.stream_token("\n\n🔍 Finding local labor lawyers...")
            lawyers = await get_lawyer_recommendations(user_location)

            await cl.Message(
                content=f"""## Recommended Labor Lawyers Near You\n\n{lawyers}\n\n### Legal Advice:\n{str(advice)}""",
                parent_id=processing_msg.id,
            ).send()
        else:
            await processing_msg.update(content=f"✅ Self-Service Advice:\n{str(advice)}")

    except Exception as e:
        await processing_msg.update(content=f"❌ Error processing request: {str(e)}")