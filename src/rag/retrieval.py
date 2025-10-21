"""
Document retrieval module for querying the vector database.

Provides efficient similarity search over policy documents.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

logger = logging.getLogger("ecom_cs_agent.rag")


class PolicyRetriever:
    """
    Handles document retrieval from ChromaDB vector store.

    Uses semantic similarity search to find relevant policy documents
    based on customer queries.
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        embedding_model: str,
        api_key: str,
        top_k: int = 3
    ):
        """
        Initialize the policy retriever.

        Args:
            persist_directory: Directory where ChromaDB is persisted
            collection_name: Name of the ChromaDB collection
            embedding_model: OpenAI embedding model name
            api_key: OpenAI API key
            top_k: Number of documents to retrieve
        """
        self.top_k = top_k
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=api_key
        )

        try:
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
            logger.info(f"Loaded vector store from {persist_directory}")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise

    def retrieve(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Customer query or question
            k: Number of documents to retrieve (overrides default top_k)

        Returns:
            List of relevant Document objects
        """
        num_results = k if k is not None else self.top_k
        logger.debug(f"Retrieving {num_results} documents for query: '{query[:50]}...'")

        try:
            documents = self.vectorstore.similarity_search(
                query=query,
                k=num_results
            )
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return []

    def retrieve_with_scores(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[tuple[Document, float]]:
        """
        Retrieve documents with similarity scores.

        Args:
            query: Customer query or question
            k: Number of documents to retrieve

        Returns:
            List of tuples containing (Document, similarity_score)
        """
        num_results = k if k is not None else self.top_k
        logger.debug(f"Retrieving {num_results} documents with scores")

        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=num_results
            )
            logger.info(f"Retrieved {len(results)} documents with scores")

            # Log scores for debugging
            for i, (doc, score) in enumerate(results):
                logger.debug(f"Result {i+1}: score={score:.4f}, source={doc.metadata.get('filename')}")

            return results
        except Exception as e:
            logger.error(f"Error during retrieval with scores: {str(e)}")
            return []

    def format_retrieved_documents(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a readable string.

        Args:
            documents: List of retrieved Document objects

        Returns:
            Formatted string containing document contents
        """
        if not documents:
            return "No relevant policy documents found."

        formatted_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('filename', 'Unknown')
            content = doc.page_content.strip()
            formatted_parts.append(
                f"--- Document {i} (Source: {source}) ---\n{content}\n"
            )

        return "\n".join(formatted_parts)

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.

        Returns:
            Dictionary containing collection statistics
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            logger.info(f"Collection contains {count} document chunks")
            return {
                "document_count": count,
                "collection_name": collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}


def create_retriever(
    persist_directory: str,
    collection_name: str,
    embedding_model: str,
    api_key: str,
    top_k: int = 3
) -> PolicyRetriever:
    """
    Factory function to create a PolicyRetriever instance.

    Args:
        persist_directory: Directory where ChromaDB is persisted
        collection_name: ChromaDB collection name
        embedding_model: OpenAI embedding model name
        api_key: OpenAI API key
        top_k: Number of documents to retrieve

    Returns:
        Configured PolicyRetriever instance
    """
    return PolicyRetriever(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_model=embedding_model,
        api_key=api_key,
        top_k=top_k
    )
