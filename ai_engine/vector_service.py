from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os

class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.persist_directory = getattr(settings, 'CHROMA_DB_PATH', './chroma_db')
        
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents):
        """
        Adds a list of document chunks to the vector store.
        """
        if documents:
            self.vector_store.add_documents(documents)

    def search_rules(self, query, k=4):
        """
        Searches for the top k most similar rule chunks.
        """
        return self.vector_store.similarity_search(query, k=k)
