from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, GenerationConfig
from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
import torch, re, os
from helpers.utils import create_template
from dotenv import load_dotenv

load_dotenv()

class Generator():

    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )


    def create_chain(self):
        template = create_template()
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        # memory = ConversationBufferMemory(
        #     memory_key="chat_history",
        #     human_prefix="### Humain",
        #     ai_prefix="### ChatBJ",
        #     input_key="question",
        #     output_key="output_text",
        #     return_messages=False,
        # )
        # memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
        chain = load_qa_chain(llm=self.llm, chain_type="stuff", prompt=prompt, verbose=False)

        return chain

    def generate(self, chain, question, documents):

        res = chain.run({"input_documents": documents, "question": question})

        return question, res