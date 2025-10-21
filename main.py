#!/usr/bin/env python3
"""
eCommerce Customer Service AI Agent System - Main Entry Point

A CrewAI-powered customer service automation system with RAG capabilities
for handling product return and refund queries.
"""

import sys
import argparse
from pathlib import Path

from src.config import load_config, ensure_directories
from src.logger import setup_logger
from src.rag.ingestion import ingest_policy_documents
from src.rag.retrieval import create_retriever
from src.tools.rag_tool import create_rag_tool
from src.tools.calculator_tool import create_return_calculator
from src.tools.summarizer_tool import create_policy_summarizer
from src.agents.crew_agents import create_customer_service_crew


def setup_system(verbose: bool = False):
    """
    Initialize the complete customer service system.

    Args:
        verbose: Enable verbose logging

    Returns:
        Tuple of (config, logger, crew)
    """
    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Set your OPENAI_API_KEY in the .env file")
        sys.exit(1)

    # Setup logging
    logger = setup_logger(verbose=verbose, log_level=config.log_level)

    # Ensure required directories exist
    ensure_directories()

    logger.info("=" * 60)
    logger.info("eCommerce Customer Service AI Agent System")
    logger.info("=" * 60)

    # Check if vector database exists
    vector_db_path = Path(config.vector_db_path)
    needs_ingestion = not vector_db_path.exists()

    if needs_ingestion:
        logger.info("Vector database not found. Starting document ingestion...")
        data_dir = Path("data/sample_policies")

        if not data_dir.exists() or not list(data_dir.iterdir()):
            logger.error(f"No policy documents found in {data_dir}")
            logger.error("Please ensure sample policy documents exist in data/sample_policies/")
            sys.exit(1)

        try:
            ingest_policy_documents(
                data_directory=str(data_dir),
                persist_directory=config.vector_db_path,
                collection_name=config.collection_name,
                embedding_model=config.embedding_model,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                api_key=config.openai_api_key
            )
            logger.info("Document ingestion completed successfully")
        except Exception as e:
            logger.error(f"Error during document ingestion: {str(e)}")
            sys.exit(1)
    else:
        logger.info("Using existing vector database")

    # Create retriever
    logger.info("Initializing document retriever...")
    try:
        retriever = create_retriever(
            persist_directory=config.vector_db_path,
            collection_name=config.collection_name,
            embedding_model=config.embedding_model,
            api_key=config.openai_api_key,
            top_k=config.top_k_results
        )

        # Get collection stats
        stats = retriever.get_collection_stats()
        logger.info(f"Loaded {stats.get('document_count', 'unknown')} document chunks")
    except Exception as e:
        logger.error(f"Error initializing retriever: {str(e)}")
        sys.exit(1)

    # Create tools
    logger.info("Creating agent tools...")
    rag_tool = create_rag_tool(retriever)
    calculator_tool = create_return_calculator()
    summarizer_tool = create_policy_summarizer()
    tools = [rag_tool, calculator_tool, summarizer_tool]

    # Create agent crew
    logger.info("Initializing CrewAI agent system...")
    try:
        crew = create_customer_service_crew(
            llm_model=config.llm_model,
            api_key=config.openai_api_key,
            tools=tools,
            verbose=verbose
        )
        logger.info("System initialization complete")
    except Exception as e:
        logger.error(f"Error creating agent crew: {str(e)}")
        sys.exit(1)

    return config, logger, crew


def process_query(crew, query: str, logger):
    """
    Process a customer service query.

    Args:
        crew: CustomerServiceCrew instance
        query: Customer query string
        logger: Logger instance
    """
    logger.info("-" * 60)
    logger.info(f"Customer Query: {query}")
    logger.info("-" * 60)

    try:
        response = crew.process_query(query)
        logger.info("-" * 60)
        logger.info("Agent Response:")
        logger.info("-" * 60)
        print(response)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return None


def interactive_mode(crew, logger):
    """
    Run in interactive mode for testing queries.

    Args:
        crew: CustomerServiceCrew instance
        logger: Logger instance
    """
    logger.info("\n" + "=" * 60)
    logger.info("INTERACTIVE MODE")
    logger.info("Type 'quit' or 'exit' to end session")
    logger.info("=" * 60 + "\n")

    while True:
        try:
            query = input("\nCustomer Query: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                logger.info("Ending session. Goodbye!")
                break

            if not query:
                continue

            process_query(crew, query, logger)

        except KeyboardInterrupt:
            logger.info("\n\nSession interrupted. Goodbye!")
            break
        except EOFError:
            break


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="eCommerce Customer Service AI Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with verbose logging
  python main.py -v

  # Process single query
  python main.py --query "Can I return an item after 45 days?"

  # Single query with verbose output
  python main.py -v --query "I received a damaged laptop"

  # Interactive mode (default)
  python main.py
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (shows agent reasoning and tool calls)'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Process a single query and exit'
    )

    parser.add_argument(
        '--reingest',
        action='store_true',
        help='Force re-ingestion of policy documents'
    )

    args = parser.parse_args()

    # Handle re-ingestion if requested
    if args.reingest:
        import shutil
        from src.config import load_config as _load_config
        cfg = _load_config()
        vector_db_path = Path(cfg.vector_db_path)
        if vector_db_path.exists():
            print(f"Removing existing vector database at {vector_db_path}")
            shutil.rmtree(vector_db_path)

    # Initialize system
    config, logger, crew = setup_system(verbose=args.verbose)

    # Process query or run interactive mode
    if args.query:
        # Single query mode
        process_query(crew, args.query, logger)
    else:
        # Interactive mode
        interactive_mode(crew, logger)


if __name__ == "__main__":
    main()
