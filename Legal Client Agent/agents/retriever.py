from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import AzureChatOpenAI
import os

retriever = FAISS.load_local("data/indian_law_vector_db", OpenAIEmbeddings())
qa_chain = RetrievalQA.from_chain_type(
    llm=AzureChatOpenAI(
        deployment_name="gpt-4",
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        temperature=0
    ),
    retriever=retriever,
)
