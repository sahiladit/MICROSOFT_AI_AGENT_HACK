from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
from semantic_kernel.prompt_template import PromptTemplate
from semantic_kernel.functions.kernel_function import KernelFunction
from semantic_kernel.skills.kernel_arguments import KernelArguments
import os

# 1. Create the Kernel
kernel = Kernel()

# 2. Create AzureChatCompletion service
azure_chat = AzureChatCompletion(
    deployment_name="gpt-35-turbo",
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY")
)

# 3. Register the service
kernel.add_service(azure_chat)

# 4. Define the prompt
prompt_text = """
You're a legal advisor. Simplify the following legal question or statement for a layperson:
{{$input}}
"""

prompt_config = PromptTemplateConfig(
    template=prompt_text,
    name="LegalSimplifier",
    description="Simplifies legal queries",
    input_variables=["input"]
)

# 5. Create the PromptTemplate and wrap it as a KernelFunction
prompt_template = PromptTemplate(prompt_config, kernel.prompt_template_engine)
simplify_skill = KernelFunction.from_prompt(prompt_template, azure_chat)

# 6. (Optional test)
if __name__ == "__main__":
    result = simplify_skill.invoke(KernelArguments(input="What is an FIR?"))
    print(result)
