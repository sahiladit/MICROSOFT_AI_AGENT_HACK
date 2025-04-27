import chainlit as cl
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import googlemaps
import requests
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize global variables
kernel = None
gmaps = None

@cl.on_chat_start
async def initialize_chat():
    """Initializes the chat session with all agents"""
    global kernel, gmaps
    
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            service_id="legal_agents",
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
    )
    
    # Initialize plugins
    legal_plugin = kernel.add_plugin(plugin_name="LegalAgents", parent_directory="plugins")
    location_plugin = kernel.add_plugin(plugin_name="LocationAgent", parent_directory="plugins")
    
    cl.user_session.set("legal_plugin", legal_plugin)
    cl.user_session.set("location_plugin", location_plugin)
    cl.user_session.set("chat_history", [])
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

async def extract_city_from_message(message: str) -> Optional[str]:
    """Extracts standardized city name from current message"""
    try:
        location_plugin = cl.user_session.get("location_plugin")
        result = await kernel.invoke(
            location_plugin["city_validator"],
            arguments=KernelArguments(current_message=message)
        )
        city = str(result).strip()
        return city if city != "UNKNOWN" else None
    except Exception as e:
        print(f"City extraction error: {e}")
        return None

async def geocode_city(city: str) -> Optional[str]:
    """Converts city name to coordinates"""
    try:
        geocode_result = gmaps.geocode(f"{city}, India")
        if geocode_result:
            loc = geocode_result[0]['geometry']['location']
            await cl.Message(content=f"📍 Detected location: {city}").send()
            return f"{loc['lat']},{loc['lng']}"
    except Exception as e:
        print(f"Geocoding error for {city}: {e}")
    return None

async def detect_location_from_ip() -> Optional[str]:
    """Attempts location detection via IP address"""
    try:
        ip = cl.user_session.get("client").get("host")
        if ip not in ["127.0.0.1", "::1"]:
            response = requests.get(
                f"https://ipinfo.io/{ip}?token={os.getenv('IPINFO_TOKEN')}",
                timeout=3
            )
            if response.status_code == 200 and "loc" in response.json():
                data = response.json()
                await cl.Message(content=f"📍 IP detected location: {data.get('city', 'Unknown')}").send()
                return data["loc"]
    except Exception as e:
        print(f"IP detection error: {e}")
    return None

async def manual_location_fallback() -> str:
    """Handles manual city input with proper validation"""
    try:
        # Get user input with proper error handling
        res = await cl.AskUserMessage(
            content="📍 Please share your city (e.g. 'Mumbai'):",
            timeout=120
        ).send()

        if not res or not isinstance(res, dict) or 'output' not in res or not res['output'].strip():
            raise ValueError("No valid city input received")
        user_input = res['output'].strip()  # Corrected line
        print(f"DEBUG - User input: {user_input}")  # Log raw input

        # Get plugin and validate
        location_plugin = cl.user_session.get("location_plugin")
        if not location_plugin:
            raise ValueError("Location plugin not initialized")

        # Process through city validator
        validation_result = await kernel.invoke(
            location_plugin["city_validator"],
            arguments=KernelArguments(current_message=user_input)
        )

        clean_city = str(validation_result).strip()
        print(f"DEBUG - Validated city: {clean_city}")  # Log cleaned city
        if clean_city == "UNKNOWN":
            raise ValueError(f"Couldn't identify city from: {user_input}")

        # Geocode the city
        geocode_result = gmaps.geocode(f"{clean_city}, India")
        if not geocode_result:
            raise ValueError(f"Google Maps couldn't locate: {clean_city}")

        loc = geocode_result[0]['geometry']['location']
        await cl.Message(content=f"📍 Location set to: {clean_city}").send()
        return f"{loc['lat']},{loc['lng']}"

    except Exception as e:
        print(f"LOCATION ERROR: {str(e)}")
        await cl.Message(
            content=f"⚠️ Error: {str(e)}\nFalling back to Delhi"
        ).send()
        return "28.6139,77.2090"


async def get_user_location(message: str) -> str:
    """Optimized location detection flow"""
    try:
        # 1. Try extracting from current message
        if message:
            if city := await extract_city_from_message(message):
                if coords := await geocode_city(city):
                    return coords
    except Exception as e:
        print(f"Error extracting city from message: {e}")

    try:
        # 2. Try IP detection
        if coords := await detect_location_from_ip():
            return coords
    except Exception as e:
        print(f"IP detection failed: {e}")

    # 3. Manual fallback
    return await manual_location_fallback()


async def detect_location_from_ip() -> Optional[str]:
    """Attempts location detection via IP address"""
    try:
        ip = cl.user_session.get("client").get("host")
        if ip not in ["127.0.0.1", "::1"]:
            response = requests.get(
                f"https://ipinfo.io/{ip}?token={os.getenv('IPINFO_TOKEN')}",
                timeout=3
            )
            if response.status_code == 200 and "loc" in response.json():
                data = response.json()
                await cl.Message(content=f"📍 IP detected location: {data.get('city', 'Unknown')}").send()
                return data["loc"]
    except Exception as e:
        print(f"IP detection error: {e}")
    return None


async def analyze_document(file: cl.File) -> str:
    """Processes uploaded legal documents"""
    try:
        content = file.content.decode('utf-8') if file.name.endswith('.txt') else "PDF/DOCX content extraction not implemented"
        legal_plugin = cl.user_session.get("legal_plugin")
        analysis = await kernel.invoke(
            legal_plugin["document_analyzer"],
            arguments=KernelArguments(document_text=content)
        )
        action_required = await kernel.invoke(
            legal_plugin["action_required"],
            arguments=KernelArguments(document_analysis=str(analysis))
        )
        return (f"📄 Analysis:\n{analysis}\n\n" +
                ("⚠️ Action Recommended" if "YES" in str(action_required).upper()
                 else "✅ No Action Needed"))
    except Exception as e:
        return f"❌ Analysis failed: {str(e)}"


async def get_lawyer_recommendations(coords: str, lawyer_type: str) -> str:
    """Finds nearby lawyers with ranking"""
    try:
        places = gmaps.places_nearby(
            location=coords,
            keyword=f"{lawyer_type} lawyer",
            radius=50000,
            type="lawyer",
        )
        
        top_lawyers = sorted(
            places.get("results", []),
            key=lambda x: (-x.get('rating', 0), x.get('user_ratings_total', 0)),
        )[:3]

        if not top_lawyers:
            return "No nearby lawyers found for this specialty"

        return "\n\n".join(
            f"🏛 **{lawyer['name']}** (⭐ {lawyer.get('rating', 'N/A')})\n"
            f"📍 {lawyer['vicinity']}\n"
            f"📞 Contact via Google Maps"
            for lawyer in top_lawyers
        )
    except Exception as e:
        return f"⚠️ Error finding lawyers: {str(e)}"

@cl.on_message
async def handle_message(message: cl.Message):
    # Update chat history
    chat_history = cl.user_session.get("chat_history")
    chat_history.append(f"User: {message.content}")
    cl.user_session.set("chat_history", chat_history)
    
    # Handle file attachments
    if message.elements:
        processing_msg = await cl.Message(content="📄 Analyzing document...").send()
        analyses = [
            await analyze_document(element)
            for element in message.elements
            if isinstance(element, cl.File)
        ]
        if analyses:
            await processing_msg.update(content="\n\n".join(analyses))
            return
    
    # Process text query
    processing_msg = await cl.Message(content="🔍 Analyzing your query...").send()
    
    try:
        legal_plugin = cl.user_session.get("legal_plugin")
        user_query = message.content
        
        # Get location-aware legal advice
        user_location = await get_user_location(user_query)
        advice = await kernel.invoke(
            legal_plugin["legal_advisor"], 
            arguments=KernelArguments(query=user_query)
        )
        
        # Check if lawyer is needed
        needs_lawyer = await kernel.invoke(
            legal_plugin["lawyer_needed"],
            arguments=KernelArguments(
                legal_advice=str(advice),
                user_query=user_query
            )
        )
        needs_lawyer = str(needs_lawyer).strip().upper()
        
        if "YES" in needs_lawyer:
            lawyer_type = await kernel.invoke(
                legal_plugin["lawyer_type"],
                arguments=KernelArguments(legal_advice=str(advice))
            )
            lawyer_type = str(lawyer_type).strip()
            
            await processing_msg.stream_token(f"\n\n⚖️ Recommended: {lawyer_type} lawyer")
            lawyers = await get_lawyer_recommendations(user_location, lawyer_type)
            
            await cl.Message(
                content=f"## Legal Advice\n{advice}\n\n## Local {lawyer_type} Lawyers\n{lawyers}",
                elements=[
                    cl.Text(name="advice", content=str(advice)),
                    cl.Text(name="lawyers", content=lawyers)
                ]
            ).send()
        else:
            await processing_msg.update(content=f"✅ Advice:\n{advice}")
            
    except Exception as e:
        await processing_msg.update(content=f"❌ Processing error: {str(e)}")