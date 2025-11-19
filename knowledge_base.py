"""
Knowledge Base Service - Handles vector database and document retrieval
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import os
import logging
from config import settings

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Vector database for storing and retrieving knowledge base documents"""

    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.Client(ChromaSettings(
            persist_directory="./chroma_data",
            anonymized_telemetry=False
        ))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "Business knowledge base for WhatsApp bot"}
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        logger.info("Knowledge base initialized")

    def add_documents(self, documents: List[str], metadata: Optional[List[dict]] = None):
        """
        Add documents to the knowledge base

        Args:
            documents: List of text documents to add
            metadata: Optional metadata for each document
        """
        if not documents:
            logger.warning("No documents to add")
            return

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Generate IDs
        existing_count = self.collection.count()
        ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids,
            metadatas=metadata if metadata else [{"source": "manual"} for _ in documents]
        )

        logger.info(f"Added {len(documents)} documents to knowledge base")

    def query(self, query_text: str, n_results: int = 3) -> str:
        """
        Query the knowledge base and return relevant context

        Args:
            query_text: The user's query
            n_results: Number of results to retrieve

        Returns:
            Concatenated relevant context from knowledge base
        """
        if self.collection.count() == 0:
            logger.warning("Knowledge base is empty")
            return ""

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query_text]).tolist()

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(n_results, self.collection.count())
        )

        # Combine results into context
        if results and results['documents']:
            documents = results['documents'][0]  # First query results
            context = "\n\n".join(documents)
            return context

        return ""

    def clear(self):
        """Clear all documents from the knowledge base"""
        self.client.delete_collection("knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "Business knowledge base for WhatsApp bot"}
        )
        logger.info("Knowledge base cleared")

    def count(self) -> int:
        """Return the number of documents in the knowledge base"""
        return self.collection.count()


# Global knowledge base instance
knowledge_base = KnowledgeBase()
