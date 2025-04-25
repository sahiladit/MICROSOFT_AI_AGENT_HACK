import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, AzureCliCredential
from langdetect import detect
import googlemaps
from typing import List, Dict, Optional
import json
from semantic_kernel_utils import LegalAssistantKernel

# Load environment variables
load_dotenv()

# Initialize Semantic Kernel
legal_kernel = LegalAssistantKernel()

# Azure OpenAI setup
endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

if not all([endpoint, deployment, api_key]):
    print("Missing environment variables. Please check .env file.")

# Google Maps setup
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=google_api_key)

# Initialize Azure OpenAI client
try:
    # First try Azure CLI authentication
    azure_credential = DefaultAzureCredential()
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_version="2025-01-01-preview",
        azure_ad_token_provider=azure_credential,
    )
except Exception as e:
    # Fall back to API key authentication if CLI auth fails
    print(f"Azure CLI authentication failed, falling back to API key: {str(e)}")
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2025-01-01-preview",
    )

# Load prompts
with open("prompts/contract_analysis.txt", "r") as f:
    contract_prompt = f.read()

with open("prompts/form_guidance.txt", "r") as f:
    form_prompt = f.read()

with open("prompts/lawyer_recommendation.txt", "r") as f:
    lawyer_prompt = f.read()

with open("prompt.txt", "r") as f:
    general_prompt = f.read()

# Lawyer specialization mapping
LAWYER_TYPES = {
    "contract": ["contract lawyer", "business lawyer", "commercial lawyer"],
    "family": ["family lawyer", "divorce lawyer"],
    "criminal": ["criminal defense lawyer", "criminal lawyer"],
    "property": ["real estate lawyer", "property lawyer"],
    "corporate": ["corporate lawyer", "business lawyer"],
    "immigration": ["immigration lawyer"],
    "employment": ["employment lawyer", "labor lawyer"],
    "intellectual_property": ["intellectual property lawyer", "patent lawyer"],
    "tax": ["tax lawyer"],
    "general": ["general practice lawyer", "attorney"]
}

def translate_text(text: str, to_lang: str = "en") -> str:
    """Translate text using OpenAI"""
    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": f"You are a translator. Translate the following text to {to_lang}. Only return the translation, nothing else."},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def detect_language(text: str) -> str:
    """Detect the language of input text"""
    return detect(text)

async def get_available_forms() -> List[Dict]:
    """Get list of available forms using prompt-based approach"""
    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a legal assistant. List the most common legal forms that users might need help with."},
                {"role": "user", "content": "What are the most common legal forms that people need help with?"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        forms_list = completion.choices[0].message.content
        return [{"name": form.strip(), "description": "Common legal form"} for form in forms_list.split("\n") if form.strip()]
    except Exception as e:
        print(f"Error getting forms: {str(e)}")
        return []

async def find_lawyers(location: str, lawyer_type: str, radius: int = 50000) -> List[Dict]:
    """Find lawyers using Google Places API"""
    lawyers = []
    search_terms = LAWYER_TYPES.get(lawyer_type, ["lawyer"])
    
    for term in search_terms:
        try:
            # Geocode the location
            geocode_result = gmaps.geocode(location)
            if not geocode_result:
                continue
                
            # Perform nearby search
            places_result = gmaps.places_nearby(
                location=geocode_result[0]['geometry']['location'],
                radius=radius,
                keyword=term,
                type='lawyer'
            )
            
            # Process each result
            for place in places_result.get('results', []):
                # Get detailed information
                details = gmaps.place(place['place_id'], 
                    fields=['name', 'rating', 'formatted_address', 
                           'formatted_phone_number', 'opening_hours', 
                           'reviews', 'website', 'price_level'])['result']
                
                # Extract reviews if available
                reviews = details.get('reviews', [])
                top_review = reviews[0] if reviews else None
                
                lawyers.append({
                    'name': details.get('name', ''),
                    'address': details.get('formatted_address', ''),
                    'phone': details.get('formatted_phone_number', ''),
                    'rating': details.get('rating', 'No rating'),
                    'total_ratings': place.get('user_ratings_total', 0),
                    'open_now': details.get('opening_hours', {}).get('open_now', None),
                    'website': details.get('website', ''),
                    'price_level': '💰' * details.get('price_level', 1) if details.get('price_level') else 'N/A',
                    'top_review': top_review['text'] if top_review else None
                })
        except Exception as e:
            print(f"Error in lawyer search: {str(e)}")
            continue
    
    # Sort by rating and limit to top 4
    return sorted(lawyers, 
                 key=lambda x: (float(x['rating']) if isinstance(x['rating'], (int, float)) else 0, 
                              x['total_ratings']), 
                 reverse=True)[:4]

def determine_lawyer_type(query: str) -> str:
    """Determine type of lawyer needed based on query"""
    query = query.lower()
    
    if any(word in query for word in ['contract', 'agreement', 'business deal']):
        return 'contract'
    elif any(word in query for word in ['divorce', 'custody', 'marriage', 'child support']):
        return 'family'
    elif any(word in query for word in ['crime', 'criminal', 'arrest', 'police']):
        return 'criminal'
    elif any(word in query for word in ['property', 'real estate', 'land', 'house']):
        return 'property'
    elif any(word in query for word in ['company', 'corporate', 'business']):
        return 'corporate'
    elif any(word in query for word in ['visa', 'immigration', 'citizenship']):
        return 'immigration'
    elif any(word in query for word in ['job', 'workplace', 'employer', 'employee']):
        return 'employment'
    elif any(word in query for word in ['patent', 'trademark', 'copyright']):
        return 'intellectual_property'
    elif any(word in query for word in ['tax', 'taxation']):
        return 'tax'
    else:
        return 'general'

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("counter", 0)
    cl.user_session.set("context", "general")
    cl.user_session.set("lawyer_search_state", None)
    cl.user_session.set("original_language", "en")
    
    welcome_msg = """👋 Welcome to the Legal Assistant! I can help you with:
    
    1. Understanding contract terms and conditions
    2. Guidance on filling legal forms
    3. Legal procedures and requirements
    4. Document checklists
    5. Finding a suitable lawyer in your area
    
    How can I assist you today?"""
    
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def on_message(message: cl.Message):
    # Check for document attachments first
    if message.elements:
        # Process document analysis
        for element in message.elements:
            if element.type == "file":
                # Show processing message
                processing_msg = await cl.Message(content=f"Analyzing your document...").send()
                
                # Analyze document using Semantic Kernel
                analysis_result = await legal_kernel.analyze_document(
                    element.content,
                    element.name.split('.')[-1].lower()
                )
                
                if analysis_result["status"] == "error":
                    await cl.Message(content=f"Error analyzing document: {analysis_result['error']}").send()
                    continue
                
                # Get next steps using Semantic Kernel
                next_steps_result = await legal_kernel.suggest_next_steps(analysis_result["analysis"])
                
                if next_steps_result["status"] == "error":
                    await cl.Message(content=f"Error generating next steps: {next_steps_result['error']}").send()
                    continue
                
                # Send analysis and next steps
                await cl.Message(
                    content=f"""
                    **Document Analysis:**
                    {analysis_result['analysis']}
                    
                    **Next Steps:**
                    {next_steps_result['next_steps']}
                    
                    Would you like me to help you with any specific aspect of the analysis or next steps?
                    """
                ).send()
                
                # Remove processing message
                await processing_msg.remove()
                return

    # Continue with existing message handling if no documents
    # Detect language and translate if needed
    original_lang = detect_language(message.content)
    cl.user_session.set("original_language", original_lang)
    
    msg_content = message.content if original_lang == "en" else translate_text(message.content)
    msg_content_lower = msg_content.lower()
    
    # Get legal advice using Semantic Kernel
    if not message.elements:
        try:
            advice_result = await legal_kernel.get_legal_advice(msg_content)
            if advice_result["status"] == "success":
                await cl.Message(content=advice_result["advice"]).send()
                return
        except Exception as e:
            print(f"Error getting legal advice: {str(e)}")
    
    context = cl.user_session.get("context")
    lawyer_search_state = cl.user_session.get("lawyer_search_state")
    
    # Update counter
    counter = cl.user_session.get("counter", 0)
    counter += 1
    cl.user_session.set("counter", counter)

    # Handle lawyer recommendation flow
    if lawyer_search_state:
        if lawyer_search_state == "awaiting_location":
            try:
                lawyers = await find_lawyers(
                    location=message.content,
                    lawyer_type=cl.user_session.get("required_lawyer_type", "general")
                )
                
                if lawyers:
                    response = "Here are some recommended lawyers in your area:\n\n"
                    for i, lawyer in enumerate(lawyers, 1):
                        response += f"{i}. {lawyer['name']}\n"
                        response += f"   📍 {lawyer['address']}\n"
                        response += f"   📞 {lawyer['phone']}\n"
                        response += f"   ⭐ Rating: {lawyer['rating']} ({lawyer['total_ratings']} reviews)\n"
                        response += f"   💰 Price Level: {lawyer['price_level']}\n"
                        if lawyer['website']:
                            response += f"   🌐 Website: {lawyer['website']}\n"
                        response += f"   {'🟢 Currently Open' if lawyer['open_now'] else '🔴 Currently Closed'}\n"
                        if lawyer['top_review']:
                            response += f"   📝 Top Review: \"{lawyer['top_review']}\"\n"
                        response += "\n"
                else:
                    response = "I couldn't find any lawyers matching your criteria in that area. Try expanding your search or try a different location."
                
                # Translate response if needed
                if original_lang != "en":
                    response = translate_text(response, original_lang)
                
                cl.user_session.set("lawyer_search_state", None)
                await cl.Message(content=response).send()
                return
            except Exception as e:
                await cl.Message(content=f"Error finding lawyers: {str(e)}").send()
                cl.user_session.set("lawyer_search_state", None)
                return
    
    # Handle form listing request
    if "show" in msg_content_lower and "form" in msg_content_lower:
        forms = await get_available_forms()
        if forms:
            form_list = "Available Forms:\n\n"
            for form in forms:
                form_list += f"📄 {form['name']}\n"
                if form.get('description'):
                    form_list += f"   {form['description']}\n"
            
            if original_lang != "en":
                form_list = translate_text(form_list, original_lang)
            
            await cl.Message(content=form_list).send()
            return
        else:
            response = "No forms are currently available."
            if original_lang != "en":
                response = translate_text(response, original_lang)
            await cl.Message(content=response).send()
            return

    # Check if user wants lawyer recommendation
    if any(word in msg_content_lower for word in ['find lawyer', 'need lawyer', 'recommend lawyer', 'legal help']):
        lawyer_type = determine_lawyer_type(msg_content)
        cl.user_session.set("required_lawyer_type", lawyer_type)
        cl.user_session.set("lawyer_search_state", "awaiting_location")
        cl.user_session.set("context", "lawyer")
        
        response = "I'll help you find a suitable lawyer. Please provide your city or location:"
        if original_lang != "en":
            response = translate_text(response, original_lang)
        
        await cl.Message(content=response).send()
        return

    # Select appropriate prompt based on context
    if "contract" in msg_content_lower:
        system_prompt = contract_prompt
        cl.user_session.set("context", "contract")
    elif "form" in msg_content_lower:
        system_prompt = form_prompt
        cl.user_session.set("context", "form")
    elif context == "lawyer":
        system_prompt = lawyer_prompt
    else:
        system_prompt = general_prompt

    # Generate response using Azure OpenAI
    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg_content}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        response = completion.choices[0].message.content
        
        # Translate response if needed
        if original_lang != "en":
            response = translate_text(response, original_lang)
        
        # Add helpful buttons based on context
        elements = []
        if "contract" in msg_content_lower:
            elements.extend([
                cl.Button(name="checklist", content="Show Contract Checklist", label="📋 Contract Checklist"),
                cl.Button(name="find_lawyer", content="Find a Contract Lawyer", label="👨‍⚖️ Find Lawyer")
            ])
        elif "form" in msg_content_lower:
            elements.extend([
                cl.Button(name="forms", content="Show Available Forms", label="📄 Available Forms"),
                cl.Button(name="find_lawyer", content="Find a Lawyer", label="👨‍⚖️ Find Lawyer")
            ])
        else:
            elements.append(
                cl.Button(name="find_lawyer", content="Find a Lawyer", label="👨‍⚖️ Find Lawyer")
            )
        
        await cl.Message(content=response, elements=elements).send()

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        if original_lang != "en":
            error_msg = translate_text(error_msg, original_lang)
        await cl.Message(content=error_msg).send()

@cl.on_chat_end
async def on_chat_end():
    print("Chat session ended")
