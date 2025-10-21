# eCommerce Customer Service AI Agent System

An intelligent, automated customer service system for eCommerce that handles product return and refund queries using CrewAI, RAG (Retrieval-Augmented Generation), and OpenAI.

## Problem Statement

Customer service is a critical pain point for eCommerce businesses:

- **High Volume**: Large eCommerce platforms receive thousands of return/refund queries daily
- **Repetitive Questions**: 70-80% of queries are about standard policies that could be automated
- **Response Time**: Customers expect instant answers, but human agents can only handle a few queries simultaneously
- **Consistency**: Human agents may provide inconsistent information about policies
- **Cost**: Customer service teams are expensive to scale, especially for 24/7 support

This system automates the handling of common customer service queries while maintaining accuracy, empathy, and policy compliance through AI agents specialized in understanding queries, retrieving policy information, and generating helpful responses.

## Architecture Overview

The system consists of four main components:

### 1. RAG (Retrieval-Augmented Generation) System
- **Document Ingestion**: Loads and processes policy documents (PDF, TXT, MD)
- **Vector Database**: ChromaDB stores document embeddings for semantic search
- **Semantic Retrieval**: Finds relevant policy information based on query similarity

### 2. Custom Tools
- **Policy Search Tool**: Retrieves relevant documents from the knowledge base
- **Return Eligibility Calculator**: Determines if returns are within policy timeframes
- **Policy Summarizer**: Condenses lengthy policies into actionable key points

### 3. CrewAI Agent Orchestration
Three specialized agents work together:
- **Query Analyzer**: Understands customer intent and extracts key information
- **Policy Retrieval Agent**: Searches policies and calculates eligibility
- **Response Generator**: Crafts empathetic, accurate customer responses

### 4. CLI Interface
- **Interactive Mode**: Chat-like interface for testing queries
- **Single Query Mode**: Process one query and exit
- **Verbose Mode**: Shows agent reasoning and tool usage for debugging

## System Flow

```
Customer Query
    ↓
Query Analyzer Agent
    ↓
Policy Retrieval Agent → [RAG Search Tool, Calculator Tool, Summarizer Tool]
    ↓
Response Generator Agent
    ↓
Customer Response
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- 4GB+ RAM recommended for vector database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/2squirrelsai/seekr-demo
   cd ecom-crewai-cs-workflow
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

5. **Verify installation**
   ```bash
   python main.py --help
   ```

### First Run

On first run, the system will automatically:
1. Ingest policy documents from `data/sample_policies/`
2. Generate embeddings using OpenAI
3. Create a ChromaDB vector database
4. Initialize the agent crew

This process takes 30-60 seconds and only happens once.

## Usage

### Interactive Mode (Recommended for Testing)

Start an interactive session:
```bash
python main.py
```

Or with verbose logging to see agent reasoning:
```bash
python main.py -v
```

Example session:
```
Customer Query: Can I return a laptop I bought 10 days ago?

[System processes query through agents...]

Agent Response:
Yes, you can return your laptop! Electronics have a 15-day return window...
```

Type `quit` or `exit` to end the session.

### Single Query Mode

Process one query and exit:
```bash
python main.py --query "How long does a refund take?"
```

With verbose output:
```bash
python main.py -v --query "I received a damaged product"
```

### Demo Scenarios

Run pre-configured demo queries:
```bash
python tests/demo_queries.py
```

With verbose output:
```bash
python tests/demo_queries.py -v
```

### Force Re-ingestion

If you update policy documents:
```bash
python main.py --reingest
```

## Example Queries

### 1. Damaged Product
**Query**: "I received a damaged laptop yesterday. How do I get a refund?"

**Expected Response**: Information about reporting damage within 48 hours, free return shipping, immediate replacement or refund options.

### 2. Return Window
**Query**: "What is the return window for electronics?"

**Expected Response**: 15-day return window for electronics, requirements for returns, restocking fees for opened items.

### 3. Missing Packaging
**Query**: "Can I return an item without the original packaging?"

**Expected Response**: Explanation of packaging requirements, potential 15% deduction, alternatives if packaging is missing.

### 4. Outside Return Window
**Query**: "I bought something 45 days ago, can I still return it?"

**Expected Response**: Return eligibility calculation based on product category, explanation of policy, possible exceptions.

### 5. Refund Processing
**Query**: "How long does a refund take to process?"

**Expected Response**: Step-by-step timeline (return shipping, inspection, refund issuance, bank processing), total expected time.

## Project Structure

```
ecom-crewai-cs-workflow/
├── README.md                    # This file
├── ARCHITECTURE.md              # Detailed architecture documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── main.py                      # Main entry point
│
├── data/
│   └── sample_policies/         # Policy documents (5 files)
│       ├── general_return_policy.txt
│       ├── electronics_return_policy.txt
│       ├── clothing_returns.txt
│       ├── refund_processing.txt
│       └── damaged_defective_items.txt
│
├── logs/
│   └── app.log                  # Application logs
│
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── logger.py                # Logging setup
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── crew_agents.py       # CrewAI agent definitions
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── rag_tool.py          # Policy search tool
│   │   ├── calculator_tool.py   # Return eligibility calculator
│   │   └── summarizer_tool.py   # Policy summarizer
│   │
│   └── rag/
│       ├── __init__.py
│       ├── ingestion.py         # Document loading and chunking
│       └── retrieval.py         # Vector database queries
│
├── tests/
│   ├── __init__.py
│   └── demo_queries.py          # Demo query script
│
└── chroma_db/                   # Vector database (generated)
```

## Logging

### Log Files
All activity is logged to `logs/app.log` with detailed DEBUG information for troubleshooting.

### Console Output

**Normal Mode** (default):
- Shows only final responses
- Clean, user-friendly output
- Suitable for production use

**Verbose Mode** (`-v` flag):
- Shows agent reasoning process
- Displays tool calls and results
- Shows document retrieval details
- Useful for debugging and understanding system behavior

Example verbose output:
```
[INFO] Query Analyzer Agent: Analyzing customer query...
[DEBUG] Identified query type: return_eligibility
[INFO] Policy Retrieval Agent: Searching knowledge base...
[DEBUG] Retrieved 3 documents with scores: 0.89, 0.85, 0.82
[INFO] Return eligibility calculator: Checking 2024-01-15...
[DEBUG] Result: NOT ELIGIBLE - 15 days overdue
[INFO] Response Generator Agent: Crafting customer response...
```

## Configuration

Configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | **Required** |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, etc.) | INFO |
| `VECTOR_DB_PATH` | ChromaDB storage path | ./chroma_db |
| `COLLECTION_NAME` | Vector DB collection name | ecommerce_policies |
| `CHUNK_SIZE` | Document chunk size | 1000 |
| `CHUNK_OVERLAP` | Chunk overlap for context | 200 |
| `TOP_K_RESULTS` | Number of docs to retrieve | 3 |
| `EMBEDDING_MODEL` | OpenAI embedding model | text-embedding-3-small |
| `LLM_MODEL` | OpenAI language model | gpt-4o-mini |

## System Requirements

- **Python**: 3.10+
- **Memory**: 4GB+ RAM
- **Disk**: 100MB for dependencies, 50MB for vector database
- **Network**: Internet connection for OpenAI API

## Cost Estimation

Using `gpt-4o-mini` and `text-embedding-3-small`:

- **Document Ingestion** (one-time): ~$0.01-0.02 for 5 sample documents
- **Per Query**: ~$0.002-0.005 depending on complexity
- **100 queries/day**: ~$0.20-0.50/day

For production, consider using `gpt-3.5-turbo` or implementing caching for common queries.

## Troubleshooting

### "OpenAI API key not set" Error
1. Ensure `.env` file exists (copy from `.env.example`)
2. Add your actual API key: `OPENAI_API_KEY=sk-...`
3. Restart the application

### "No documents found" Error
1. Verify `data/sample_policies/` contains policy files
2. Check file permissions
3. Try `--reingest` flag to force re-processing

### Slow First Run
- First run ingests documents and creates embeddings (30-60 seconds)
- Subsequent runs use cached vector database (starts in 5-10 seconds)

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

## Development

### Adding New Policy Documents
1. Add files to `data/sample_policies/`
2. Supported formats: PDF, TXT, MD
3. Run with `--reingest` flag

### Customizing Agents
Edit `src/agents/crew_agents.py` to modify:
- Agent roles and goals
- Task descriptions
- Agent backstories

### Adding New Tools
1. Create tool in `src/tools/`
2. Inherit from `crewai.tools.BaseTool`
3. Add to tools list in `main.py`

## Next Steps for Production

See `ARCHITECTURE.md` for detailed recommendations on:
- Scaling on GCP (Cloud Run, Vertex AI, Cloud Storage)
- Adding authentication and rate limiting
- Implementing caching for common queries
- Adding conversation memory
- Monitoring and analytics
- A/B testing different agent configurations

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check `logs/app.log` for detailed error information
- Run with `-v` flag to see detailed execution flow
- Review `ARCHITECTURE.md` for system design details

## Acknowledgments

Built with:
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - Language models and embeddings
# seekr-demo
