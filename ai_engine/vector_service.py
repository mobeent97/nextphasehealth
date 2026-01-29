# Placeholder for LangChain/ChromaDB logic
import os
from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


class VectorService:
    def __init__(self, collection_name="regulatory_rules_2026"):
        # 1. Initialize the Embedding Function (uses your API Key)
        self.embedding_fn = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

        # 2. Configure ChromaDB using the path from settings.py
        self.persist_directory = settings.CHROMA_DB_PATH

        # 3. Initialize the Vector Store Client
        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_fn,
            collection_name=collection_name
        )

    def search_rules(self, query, k=4):
        """
        Searches the ChromaDB for relevant medical rules.
        """
        return self.vector_db.similarity_search(query, k=k)

    def add_documents(self, documents):
        """
        Ingests new chunks of PDF text into ChromaDB.
        """
        self.vector_db.add_documents(documents)
        self.vector_db.persist()