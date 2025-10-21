"""
Document ingestion module for loading and processing policy documents.

Handles PDF and text file loading, chunking, and embedding generation.
"""

import logging
from pathlib import Path
from typing import List, Optional
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

logger = logging.getLogger("ecom_cs_agent.rag")


class DocumentIngestion:
    """
    Handles document loading, chunking, and ingestion into vector database.

    This class processes policy documents and stores them in ChromaDB
    for efficient retrieval.
    """

    def __init__(
        self,
        embedding_model: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        api_key: str = None
    ):
        """
        Initialize document ingestion.

        Args:
            embedding_model: Name of OpenAI embedding model
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            api_key: OpenAI API key
        """
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info(
            f"Initialized ingestion with chunk_size={chunk_size}, "
            f"overlap={chunk_overlap}"
        )

    def load_pdf(self, file_path: Path) -> str:
        """
        Load text content from a PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        logger.debug(f"Loading PDF: {file_path}")
        text_content = []

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
                logger.debug(f"Extracted {len(pdf_reader.pages)} pages from {file_path.name}")
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise

        return "\n\n".join(text_content)

    def load_text_file(self, file_path: Path) -> str:
        """
        Load text content from a text file.

        Args:
            file_path: Path to text file

        Returns:
            File content as string
        """
        logger.debug(f"Loading text file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logger.debug(f"Loaded {len(content)} characters from {file_path.name}")
            return content
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise

    def load_documents_from_directory(self, directory: Path) -> List[Document]:
        """
        Load all supported documents from a directory.

        Args:
            directory: Directory containing policy documents

        Returns:
            List of Document objects
        """
        logger.info(f"Loading documents from: {directory}")
        documents = []
        supported_extensions = {'.pdf', '.txt', '.md'}

        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return documents

        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    if file_path.suffix.lower() == '.pdf':
                        content = self.load_pdf(file_path)
                    else:
                        content = self.load_text_file(file_path)

                    # Create Document object with metadata
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "filename": file_path.name,
                            "type": "policy_document"
                        }
                    )
                    documents.append(doc)
                    logger.info(f"Loaded document: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path.name}: {str(e)}")

        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for better retrieval.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects
        """
        logger.info(f"Chunking {len(documents)} documents")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")
        return chunks

    def ingest_to_vectordb(
        self,
        documents: List[Document],
        persist_directory: str,
        collection_name: str
    ) -> Chroma:
        """
        Ingest chunked documents into ChromaDB vector store.

        Args:
            documents: List of Document objects to ingest
            persist_directory: Directory to persist ChromaDB
            collection_name: Name of the collection

        Returns:
            Chroma vector store instance
        """
        logger.info(f"Ingesting {len(documents)} chunks into ChromaDB")
        logger.debug(f"Persist directory: {persist_directory}")
        logger.debug(f"Collection name: {collection_name}")

        try:
            # Create vector store with documents
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=persist_directory,
                collection_name=collection_name
            )
            logger.info("Successfully created vector store")
            return vectorstore
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise


def ingest_policy_documents(
    data_directory: str,
    persist_directory: str,
    collection_name: str,
    embedding_model: str,
    chunk_size: int,
    chunk_overlap: int,
    api_key: str
) -> Chroma:
    """
    Complete ingestion pipeline for policy documents.

    Args:
        data_directory: Directory containing policy documents
        persist_directory: Directory to persist vector database
        collection_name: ChromaDB collection name
        embedding_model: OpenAI embedding model name
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        api_key: OpenAI API key

    Returns:
        Chroma vector store instance
    """
    logger.info("Starting document ingestion pipeline")

    ingestion = DocumentIngestion(
        embedding_model=embedding_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        api_key=api_key
    )

    # Load documents
    documents = ingestion.load_documents_from_directory(Path(data_directory))

    if not documents:
        raise ValueError(f"No documents found in {data_directory}")

    # Chunk documents
    chunks = ingestion.chunk_documents(documents)

    # Ingest into vector database
    vectorstore = ingestion.ingest_to_vectordb(
        documents=chunks,
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    logger.info("Document ingestion pipeline completed successfully")
    return vectorstore
