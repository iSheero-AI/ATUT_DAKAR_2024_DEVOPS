import uuid
import re, os
from sentence_transformers import SentenceTransformer, CrossEncoder
from pinecone_text.sparse import BM25Encoder
from langchain_community.retrievers import PineconeHybridSearchRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import AzureOpenAIEmbeddings
from helpers.utils import load_pinecone_index
from dotenv import load_dotenv
import nltk
nltk.download('punkt_tab')

load_dotenv()

class Retriever():

    def __init__(self):
        self.index = load_pinecone_index("chatbj-index", 1536)
        self.embed = AzureOpenAIEmbeddings(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME_EMBEDDINGS"),
            openai_api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )
        self.bm25_encoder = BM25Encoder().default()
        self.retriever = PineconeHybridSearchRetriever(
            embeddings=self.embed, sparse_encoder=self.bm25_encoder, index=self.index
        )
        self.ranker = CrossEncoder('amberoad/bert-multilingual-passage-reranking-msmarco', max_length=512)


    def get_relevants_documents(self, query: str, topk: int) -> list[str]:
        query = "query: "+query
        self.retriever.top_k = 20
        documents = self.retriever.get_relevant_documents(query)
        relevants_documents = []
        model_inputs = [[query, doc.page_content] for doc in documents]
        scores = self.ranker.predict(model_inputs)
        scores=[(i, s) for i, s in enumerate(scores)]
        # scores = [(documents[j[0]], j[1]) for j in scores]
        scores = [(documents[j[0]], j[1][1]) for j in scores]
        scores.sort(reverse=True, key=lambda x: x[1])
        scores=[doc[0] for doc in scores]

        return scores[:topk]
