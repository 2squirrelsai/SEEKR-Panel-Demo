Build an agentic AI customer service system for eCommerce (Amazon-style) that handles product return/refund queries using CrewAI, RAG, and OpenAI. This is for a 4-6 hour AI Solutions Architect interview assignment.

REQUIREMENTS:

1. PROJECT STRUCTURE:
   - Create a clean GitHub-ready repository with proper .gitignore
   - Use Python 3.10+
   - Include requirements.txt with all dependencies
   - Add comprehensive README.md with:
     * Problem statement (why customer service automation matters for eCommerce)
     * Architecture overview
     * Setup instructions (including OpenAI API key configuration)
     * Run instructions with examples
     * Architecture diagram description (I'll create the actual diagram separately)

2. CORE COMPONENTS:

   A. DATA INGESTION:
      - Scrape or use Amazon's public help documentation about returns/refunds
      - Alternative: Use publicly available eCommerce return policy documents (Amazon Help pages, return FAQs)
      - Store in a /data directory
      - Support PDF and/or text file ingestion
      - Include at least 5-10 sample documents about returns, refunds, policies

   B. RAG IMPLEMENTATION:
      - Use ChromaDB (or simplest vector DB option) for vector storage
      - Implement document chunking with appropriate overlap
      - Use OpenAI embeddings (text-embedding-3-small or similar)
      - Create a retrieval tool that searches relevant policy documents

   C. CREWAI AGENT ORCHESTRATION:
      - Create 2-3 specialized agents:
        * Customer Query Analyzer (classifies query type)
        * Policy Retrieval Agent (searches RAG system)
        * Response Generator Agent (crafts helpful responses)
      - Define clear roles, goals, and backstories for each agent
      - Implement proper task flow and delegation

   D. CUSTOM TOOLS:
      - RAG search tool (retrieves relevant policy documents)
      - Return eligibility calculator (checks if return window is valid based on date)
      - Policy summarizer tool (condenses long policies)

3. LOGGING & VERBOSITY:
   - Implement Python logging framework (logging module)
   - Add '-v' or '--verbose' CLI parameter for detailed output
   - When -v enabled: show agent reasoning, tool calls, retrieval results
   - When -v disabled: show only final responses
   - Log to both console and file (logs/app.log)
   - Use appropriate log levels (INFO, DEBUG, WARNING, ERROR)

4. CLI INTERFACE:
   - Main entry point: python main.py or python -m src.main
   - Support interactive mode for testing queries
   - Example: python main.py -v --query "Can I return an item after 45 days?"
   - Include 3-5 sample queries in README for demo purposes

5. DEMO SCENARIOS:
   Create examples that showcase:
   - "I received a damaged product, how do I get a refund?"
   - "What is the return window for electronics?"
   - "Can I return an item without the original packaging?"
   - "I bought something 45 days ago, can I still return it?"
   - "How long does a refund take to process?"

6. ARCHITECTURE CONSIDERATIONS:
   - Add a ARCHITECTURE.md file explaining:
     * System design (components and data flow)
     * Why CrewAI was chosen for orchestration
     * RAG pipeline explanation
     * How this could scale on GCP (Cloud Run, Vertex AI, Cloud Storage, etc.)
     * Trade-offs made for the 4-6 hour time constraint

7. CODE QUALITY:
   - Type hints where appropriate
   - Docstrings for main functions/classes
   - Modular structure (separate files for agents, tools, RAG, utils)
   - Error handling for API failures, missing documents, etc.
   - Configuration management (use .env for API keys)

8. CONFIGURATION:
   - Use python-dotenv for environment variables
   - Create .env.example template with:
     * OPENAI_API_KEY=your_key_here
     * LOG_LEVEL=INFO
     * VECTOR_DB_PATH=./chroma_db
   - Add configuration validation on startup

9. TESTING:
   - Include a test script or notebook that runs the demo scenarios
   - Ensure it works on a fresh clone with minimal setup

STRUCTURE EXAMPLE:
```
project-root/
├── README.md
├── ARCHITECTURE.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py
├── data/
│   └── sample_policies/
├── logs/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── crew_agents.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── rag_tool.py
│   │   └── calculator_tool.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   └── retrieval.py
│   ├── config.py
│   └── logger.py
└── tests/
    └── demo_queries.py
```

IMPORTANT:
- Keep it simple but professional - this is a 4-6 hour assignment
- Focus on clear architecture over complex features
- Make sure everything runs locally with just "pip install -r requirements.txt" and setting OpenAI API key
- The demo should be impressive but the code should be readable and well-organized
- Comments should explain WHY not WHAT

Build this now, ensuring all files are created and the system is ready to run.