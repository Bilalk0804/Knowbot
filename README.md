# PortalHelper AI Assistant - Knowledge Graph Bot

An intelligent AI-based helping bot for information retrieval from a knowledge graph, built with LangChain, Ollama (deepseek model), and mxbai-embed-large embeddings.

## Features

- 🤖 **AI-Powered Responses**: Uses Ollama's deepseek model for intelligent responses
- 🔍 **Semantic Search**: Leverages mxbai-embed-large embeddings for accurate document retrieval
- 📊 **Knowledge Graph**: Structured entity-relationship data for enhanced context
- 📚 **Document Management**: Automatic text chunking and vector storage with ChromaDB
- 🐛 **Debug Mode**: Detailed retrieval steps for troubleshooting
- 📖 **Source Tracking**: Track which documents were used for responses
- 💾 **Persistence**: Save and load knowledge graphs to/from files
- 🌐 **Web Scraping**: Automatically scrape data from web portals using Selenium

## Prerequisites

1. **Ollama Installation**: Make sure you have Ollama installed and running
2. **Required Models**: Ensure you have the following models pulled:
   ```bash
   ollama pull deepseek
   ollama pull mxbai-embed-large
   ```

3. **Chrome Browser**: Install Google Chrome for web scraping functionality

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Ollama models are available**:
   ```bash
   ollama list
   ```

## Usage

### Basic Usage

Run the bot with sample data:

```bash
python main.py
```

### Web Scraping Usage

Run the web scraping example:

```bash
python web_scraping_example.py
```

### Interactive Commands

- **Ask questions**: Simply type your question about the portal
- **Debug mode**: Type `debug mode` to see detailed retrieval steps
- **View sources**: Type `sources` to see which documents were used
- **Web scraping**: Type `scrape` to scrape data from a web portal
- **Quit**: Type `quit` to exit

### Example Interactions

```
👤 You: How do I reset my password?
🤖 Assistant: You can reset your password using the "Forgot Password" link on the login page. For technical support, contact support@portal.com or call 1-800-HELP.

👤 You: What are the password requirements?
🤖 Assistant: Password requirements include at least 8 characters with uppercase, lowercase, numbers, and special characters. The system automatically locks accounts after 5 failed login attempts.

👤 You: debug mode
🤖 Assistant (Debug Mode):
Retrieved 2 documents:
Doc 1: doc_001 - PortalHelper is a comprehensive web portal that provides various services to users...
Doc 2: doc_002 - User authentication in PortalHelper supports multiple methods including email/password...
```

## API Usage

### Initialize the Bot

```python
from main import KnowledgeGraphBot

bot = KnowledgeGraphBot()
```

### Add Documents

```python
documents = [
    {
        "id": "doc_001",
        "content": "Your document content here...",
        "metadata": {"category": "general", "author": "admin"}
    }
]
bot.add_documents(documents)
```

### Add Knowledge Graph Entities

```python
entities = [
    {"id": "feature_1", "name": "User Authentication", "type": "feature"},
    {"id": "service_1", "name": "Technical Support", "type": "service"}
]
bot.add_entities(entities)
```

### Add Relationships

```python
relationships = [
    {"source": "feature_1", "target": "service_1", "type": "requires"}
]
bot.add_relationships(relationships)
```

### Query the Bot

```python
# Normal query
response = bot.query("How do I reset my password?")
print(response)

# Debug mode
debug_response = bot.query("How do I reset my password?", debug_mode=True)
print(debug_response)

# Get sources
sources = bot.get_sources("How do I reset my password?")
print(sources)
```

### Save/Load Knowledge Graph

```python
# Save knowledge graph
bot.save_knowledge_graph("knowledge_graph.json")

# Load knowledge graph
bot.load_knowledge_graph("knowledge_graph.json")
```

## Knowledge Graph Structure

The bot maintains a structured knowledge graph with:

### Documents
- **Content**: The actual text content
- **Metadata**: Additional information (category, author, etc.)
- **Chunks**: Automatically split into searchable chunks

### Entities
- **ID**: Unique identifier
- **Name**: Human-readable name
- **Type**: Category (feature, service, role, etc.)

### Relationships
- **Source**: Source entity ID
- **Target**: Target entity ID
- **Type**: Relationship type (requires, depends_on, manages, etc.)

## Configuration

### Model Configuration

The bot uses:
- **LLM**: `deepseek` (via Ollama)
- **Embeddings**: `mxbai-embed-large` (via Ollama)

### Vector Store Configuration

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Retrieval**: Top 5 most similar documents

## Customization

### Adding Your Own Data

1. **Prepare your documents**:
   ```python
   documents = [
       {
           "id": "your_doc_id",
           "content": "Your content here...",
           "metadata": {"category": "your_category"}
       }
   ]
   ```

2. **Define entities and relationships**:
   ```python
   entities = [
       {"id": "entity_1", "name": "Entity Name", "type": "entity_type"}
   ]
   
   relationships = [
       {"source": "entity_1", "target": "entity_2", "type": "relationship_type"}
   ]
   ```

3. **Add to the bot**:
   ```python
   bot.add_documents(documents)
   bot.add_entities(entities)
   bot.add_relationships(relationships)
   ```

### Web Scraping Data

1. **Scrape a web portal**:
   ```python
   # Define the portal and pages to scrape
   base_url = "https://example.com"
   pages = ["/about", "/help", "/contact"]
   
   # Optional: Define CSS selectors for specific content
   selectors = {
       "content": "div.main-content",
       "title": "h1",
       "author": "span.author"
   }
   
   # Scrape and add to knowledge base
   bot.scrape_and_add_data(base_url, pages, selectors)
   ```

2. **Interactive scraping**:
   ```python
   # Run the interactive scraping session
   python web_scraping_example.py
   ```

### Modifying the Prompt Template

Edit the `_setup_prompt_template()` method in the `KnowledgeGraphBot` class to customize the AI's behavior and response style.

## Troubleshooting

### Common Issues

1. **Model not found**: Ensure you have pulled the required Ollama models
2. **Import errors**: Install all dependencies from requirements.txt
3. **Memory issues**: Reduce chunk size for large documents
4. **Slow responses**: Consider using a smaller embedding model

### Debug Mode

Use debug mode to understand how the bot processes queries:
```python
response = bot.query("Your question", debug_mode=True)
```

## Architecture

```
User Query → Embedding Search → Document Retrieval → Knowledge Graph Lookup → LLM Generation → Response
```

1. **Query Processing**: User question is processed
2. **Semantic Search**: Embeddings find relevant documents
3. **Knowledge Graph**: Entities and relationships are identified
4. **Context Assembly**: All relevant information is combined
5. **LLM Generation**: Deepseek model generates the final response

## Contributing

Feel free to contribute by:
- Adding new features
- Improving the prompt template
- Enhancing the knowledge graph structure
- Adding more sample data

## License

This project is open source and available under the MIT License. 