"""
RAG search tool for retrieving relevant policy documents.

This tool enables agents to search the vector database for policy information.
"""

import logging
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.rag.retrieval import PolicyRetriever

logger = logging.getLogger("ecom_cs_agent.tools")


class RAGSearchInput(BaseModel):
    """Input schema for RAG search tool."""
    query: str = Field(..., description="The customer query or question to search for in policy documents")
    num_results: Optional[int] = Field(
        default=3,
        description="Number of relevant documents to retrieve (default: 3)"
    )


class RAGSearchTool(BaseTool):
    """
    Tool for searching policy documents using semantic similarity.

    This tool retrieves relevant policy documents from the vector database
    based on the customer's query, enabling agents to access accurate
    policy information.
    """

    name: str = "policy_document_search"
    description: str = (
        "Search for relevant policy documents in the knowledge base. "
        "Use this tool to find information about return policies, refund procedures, "
        "eligibility criteria, timeframes, and other policy-related questions. "
        "Input should be a clear question or query about eCommerce policies."
    )
    args_schema: Type[BaseModel] = RAGSearchInput
    retriever: Optional[PolicyRetriever] = None

    def __init__(self, retriever: PolicyRetriever, **kwargs):
        """
        Initialize the RAG search tool.

        Args:
            retriever: PolicyRetriever instance for document search
        """
        super().__init__(**kwargs)
        self.retriever = retriever

    def _run(self, query: str, num_results: int = 3) -> str:
        """
        Execute the RAG search.

        Args:
            query: Customer query or question
            num_results: Number of documents to retrieve

        Returns:
            Formatted string containing relevant policy documents
        """
        logger.info(f"RAG search initiated for: '{query[:50]}...'")
        logger.debug(f"Retrieving {num_results} documents")

        try:
            # Retrieve documents with scores
            results = self.retriever.retrieve_with_scores(query=query, k=num_results)

            if not results:
                logger.warning("No relevant documents found")
                return "No relevant policy documents found for this query."

            # Format results
            formatted_output = []
            for i, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get('filename', 'Unknown')
                content = doc.page_content.strip()
                formatted_output.append(
                    f"[Document {i} - Relevance: {score:.2f} - Source: {source}]\n{content}\n"
                )

            result_text = "\n---\n".join(formatted_output)
            logger.info(f"Retrieved {len(results)} relevant documents")
            return result_text

        except Exception as e:
            error_msg = f"Error during policy search: {str(e)}"
            logger.error(error_msg)
            return error_msg


def create_rag_tool(retriever: PolicyRetriever) -> RAGSearchTool:
    """
    Factory function to create a RAG search tool.

    Args:
        retriever: PolicyRetriever instance

    Returns:
        Configured RAGSearchTool instance
    """
    return RAGSearchTool(retriever=retriever)
