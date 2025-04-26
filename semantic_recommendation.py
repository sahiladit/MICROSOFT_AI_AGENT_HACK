import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_arguments import KernelArguments
import googlemaps
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize services
kernel = Kernel()
kernel.add_service(
    AzureChatCompletion(
        service_id="legal_advisor",
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
)

# Initialize Google Maps client
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

async def get_lawyer_recommendations(location: str, practice_area: str = "labor lawyer") -> Optional[list]:
    """Get top 5 labor lawyers near location"""
    try:
        places = gmaps.places_nearby(
            location=location,
            keyword=practice_area,
            rank_by="distance",
            type="lawyer"
        )
        return sorted(
            places.get("results", []),
            key=lambda x: x.get("rating", 0),
            reverse=True
        )[:5]
    except Exception as e:
        print(f"Error fetching lawyers: {e}")
        return None

# Load plugin
legal_plugin = kernel.add_plugin(
    plugin_name="LegalPlugin",
    parent_directory="plugins"  # Contains LegalPlugin folder with needs_lawyer_decider subfolder
)

async def handle_legal_query(user_query: str, user_location: str):
    # Get initial legal advice
    advice = await kernel.invoke(
        legal_plugin["legal_advisor"],
        arguments=KernelArguments(query=user_query)
    )
    
    # Check if lawyer needed
    decision = await kernel.invoke(
        legal_plugin["needs_lawyer_decider"],
        arguments=KernelArguments(
            legal_advice=str(advice),
            user_query=user_query
        )
    )
    
    # Process decision
    if decision and "YES" in str(decision).strip().upper():
        lawyers = await get_lawyer_recommendations(user_location)
        if lawyers:
            print("\nRecommended Labor Lawyers:")
            for idx, lawyer in enumerate(lawyers, 1):
                print(f"{idx}. {lawyer['name']} (Rating: {lawyer.get('rating', 'N/A')})")
                print(f"   📍 {lawyer['vicinity']}")
                print(f"   📞 {lawyer.get('international_phone_number', 'Contact not available')}\n")
        else:
            print("Couldn't find lawyers in your area. Please try a broader search.")
    
    return str(advice)

# Example execution
if __name__ == "__main__":
    import asyncio
    query = "what could be the legal actions against a company that is not paying its employees?"
    location = "40.7128,-74.0060"  # NYC coordinates
    
    advice = asyncio.run(handle_legal_query(query, location))
    print("\nLegal Advice:", advice)