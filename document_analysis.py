import os
import chainlit as cl
from openai import AzureOpenAI
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("ENDPOINT_URL")
)
deployment = os.getenv("DEPLOYMENT_NAME")

async def analyze_document(file_content: str, file_type: str) -> Dict:
    """
    Analyzes the uploaded document and provides insights and next steps.
    
    Args:
        file_content (str): Content of the uploaded file
        file_type (str): Type of the uploaded file (e.g., 'pdf', 'docx', 'txt')
    
    Returns:
        Dict: Analysis results containing insights and next steps
    """
    try:
        # Create a system message for document analysis
        system_message = """You are a legal document analysis assistant. Your role is to:
        1. Analyze the provided document
        2. Identify key legal points and implications
        3. Highlight important deadlines or requirements
        4. Suggest next steps
        5. Flag any potential concerns or risks
        
        Provide your analysis in a structured format with clear sections."""
        
        # Get analysis from Azure OpenAI
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Please analyze this {file_type} document:\n\n{file_content}"}
            ],
            temperature=0.3
        )
        
        # Parse the response
        analysis = completion.choices[0].message.content
        
        # Structure the response
        return {
            "analysis": analysis,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

async def suggest_next_steps(analysis: str) -> Dict:
    """
    Generates specific next steps based on the document analysis.
    
    Args:
        analysis (str): The document analysis text
    
    Returns:
        Dict: Structured next steps recommendations
    """
    try:
        system_message = """Based on the provided analysis, suggest specific next steps the user should take.
        Include:
        1. Immediate actions
        2. Required documentation
        3. Potential timelines
        4. Professional assistance needed
        5. Resources or references
        
        Format the response in a clear, actionable list."""
        
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Based on this analysis, what are the next steps?\n\n{analysis}"}
            ],
            temperature=0.3
        )
        
        next_steps = completion.choices[0].message.content
        
        return {
            "next_steps": next_steps,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

@cl.on_message
async def handle_document_analysis(message: cl.Message):
    """
    Handles document upload and analysis requests.
    """
    # Check if there are any attachments
    if not message.elements:
        await cl.Message(content="Please upload a document for analysis.").send()
        return
    
    # Process each attachment
    for element in message.elements:
        if element.type == "file":
            # Read file content
            file_content = element.content
            file_type = element.name.split('.')[-1].lower()
            
            # Show processing message
            processing_msg = await cl.Message(content=f"Analyzing your {file_type} document...").send()
            
            # Analyze document
            analysis_result = await analyze_document(file_content, file_type)
            
            if analysis_result["status"] == "error":
                await cl.Message(content=f"Error analyzing document: {analysis_result['error']}").send()
                continue
            
            # Get next steps
            next_steps_result = await suggest_next_steps(analysis_result["analysis"])
            
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