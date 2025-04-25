import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.core_skills import TextSkill
from semantic_kernel.planning import SequentialPlanner
from semantic_kernel.planning.basic_planner import BasicPlanner
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LegalAssistantKernel:
    def __init__(self):
        # Initialize the kernel
        self.kernel = Kernel()
        
        # Configure Azure OpenAI
        self.kernel.add_chat_service(
            "legal_assistant",
            AzureChatCompletion(
                deployment_name=os.getenv("DEPLOYMENT_NAME"),
                endpoint=os.getenv("ENDPOINT_URL"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
        )
        
        # Add core skills
        self.kernel.import_skill(TextSkill())
        
        # Initialize planner
        self.planner = SequentialPlanner(self.kernel)
        
        # Define skills
        self._define_skills()
    
    def _define_skills(self):
        # Document Analysis Skill
        document_analysis_skill = """
        You are a legal document analysis assistant. Your role is to:
        1. Analyze the provided document
        2. Identify key legal points and implications
        3. Highlight important deadlines or requirements
        4. Suggest next steps
        5. Flag any potential concerns or risks
        
        Provide your analysis in a structured format with clear sections.
        """
        self.kernel.import_semantic_function_from_prompt(
            "document_analysis",
            document_analysis_skill
        )
        
        # Next Steps Skill
        next_steps_skill = """
        Based on the provided analysis, suggest specific next steps the user should take.
        Include:
        1. Immediate actions
        2. Required documentation
        3. Potential timelines
        4. Professional assistance needed
        5. Resources or references
        
        Format the response in a clear, actionable list.
        """
        self.kernel.import_semantic_function_from_prompt(
            "next_steps",
            next_steps_skill
        )
        
        # Legal Advice Skill
        legal_advice_skill = """
        You are a legal advisor. Provide clear, accurate, and practical legal advice.
        Consider:
        1. Relevant laws and regulations
        2. Potential legal implications
        3. Best practices
        4. Risk assessment
        5. Alternative solutions
        
        Format your response in a clear, structured manner.
        """
        self.kernel.import_semantic_function_from_prompt(
            "legal_advice",
            legal_advice_skill
        )
    
    async def analyze_document(self, content: str, file_type: str) -> dict:
        """Analyze a legal document using Semantic Kernel"""
        try:
            # Create context
            context = self.kernel.create_new_context()
            context["content"] = content
            context["file_type"] = file_type
            
            # Execute document analysis
            result = await self.kernel.run_async(
                context,
                self.kernel.skills.get_function("document_analysis")
            )
            
            return {
                "analysis": str(result),
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def suggest_next_steps(self, analysis: str) -> dict:
        """Generate next steps based on document analysis"""
        try:
            # Create context
            context = self.kernel.create_new_context()
            context["analysis"] = analysis
            
            # Execute next steps generation
            result = await self.kernel.run_async(
                context,
                self.kernel.skills.get_function("next_steps")
            )
            
            return {
                "next_steps": str(result),
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def get_legal_advice(self, query: str) -> dict:
        """Get legal advice using Semantic Kernel"""
        try:
            # Create context
            context = self.kernel.create_new_context()
            context["query"] = query
            
            # Execute legal advice generation
            result = await self.kernel.run_async(
                context,
                self.kernel.skills.get_function("legal_advice")
            )
            
            return {
                "advice": str(result),
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def create_plan(self, goal: str) -> dict:
        """Create a plan to achieve a legal goal"""
        try:
            # Create a plan using the planner
            plan = await self.planner.create_plan_async(goal)
            
            # Execute the plan
            result = await self.planner.execute_plan_async(plan)
            
            return {
                "plan": str(plan),
                "result": str(result),
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            } 