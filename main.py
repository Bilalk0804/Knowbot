import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_ollama.llms import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper using Selenium to collect data from web portals."""
    
    def __init__(self, headless: bool = True):
        """Initialize the web scraper."""
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def close_driver(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")
    
    def scrape_page(self, url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Scrape a single page and extract content."""
        if not self.driver:
            self.setup_driver()
        
        try:
            logger.info(f"Scraping page: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract page content
            page_data = {
                "url": url,
                "title": self.driver.title,
                "content": "",
                "metadata": {}
            }
            
            # Extract main content
            if selectors and "content" in selectors:
                try:
                    content_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors["content"])
                    content_text = " ".join([elem.text for elem in content_elements if elem.text.strip()])
                    page_data["content"] = content_text
                except NoSuchElementException:
                    logger.warning(f"Content selector not found: {selectors['content']}")
            else:
                # Default content extraction
                body = self.driver.find_element(By.TAG_NAME, "body")
                page_data["content"] = body.text
            
            # Extract metadata
            if selectors:
                for key, selector in selectors.items():
                    if key != "content":
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                page_data["metadata"][key] = elements[0].text.strip()
                        except NoSuchElementException:
                            logger.warning(f"Selector not found: {selector}")
            
            # Add timestamp
            page_data["metadata"]["scraped_at"] = datetime.now().isoformat()
            
            return page_data
            
        except TimeoutException:
            logger.error(f"Timeout while loading page: {url}")
            return {"url": url, "content": "", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return {"url": url, "content": "", "error": str(e)}
    
    def scrape_portal(self, base_url: str, pages: List[str], selectors: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Scrape multiple pages from a portal."""
        scraped_data = []
        
        try:
            for page in pages:
                full_url = urljoin(base_url, page)
                page_data = self.scrape_page(full_url, selectors)
                if page_data["content"]:
                    scraped_data.append(page_data)
                time.sleep(1)  # Be respectful to the server
                
        except Exception as e:
            logger.error(f"Error scraping portal: {e}")
        
        return scraped_data

class KnowledgeGraphBot:
    def __init__(self):
        """Initialize the AI-based helping bot with knowledge graph capabilities."""
        # Initialize models
        self.llm = OllamaLLM(model="deepseek-r1")
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        
        # Initialize vector store
        self.vectorstore = None
        self.retriever = None
        
        # Knowledge graph data
        self.knowledge_graph = {
            "entities": {},
            "relationships": [],
            "documents": {},
            "last_updated": None
        }
        
        # Initialize web scraper
        self.scraper = WebScraper(headless=True)
        
        # Initialize the bot
        self._setup_prompt_template()
        self._setup_chain()
        
    def _setup_prompt_template(self):
        """Setup the prompt template for the AI assistant."""
        self.prompt_template = ChatPromptTemplate.from_template("""
You are an AI assistant for a web portal named "PortalHelper". Your task is to answer user queries by retrieving information from a structured knowledge graph. Follow these rules:

1. **Response Strategy**:
   - Always base answers ONLY on context from the knowledge graph.
   - If context is insufficient, say: "I couldn't find information on this. Try rephrasing or ask about [related topic]."
   - NEVER hallucinate or invent details.

2. **Knowledge Graph Context**:
   - The graph contains entities (people, features, articles) and relationships (e.g., "Article X explains Feature Y").
   - Dynamic content (e.g., user comments) is updated daily.

3. **Output Rules**:
   - Be concise, friendly, and professional.
   - For multi-part queries, break responses into bullet points.
   - Cite sources using [Document ID:123] when available.

4. **Special Commands**:
   - If asked "debug mode", explain your retrieval steps.
   - If asked "sources", list all referenced document IDs.

**Context Information:**
{context}

**User Question:**
{question}

**Knowledge Graph Entities:**
{entities}

**Knowledge Graph Relationships:**
{relationships}

Please provide a helpful response based on the available information.
""")
    
    def _setup_chain(self):
        """Setup the LangChain processing chain."""
        def get_context(input_dict):
            question = input_dict["question"]
            if self.retriever:
                docs = self.retriever.get_relevant_documents(question)
                return "\n".join([doc.page_content for doc in docs])
            return "No documents available"
        
        def get_entities(input_dict):
            return self._get_relevant_entities(input_dict["question"])
        
        def get_relationships(input_dict):
            return self._get_relevant_relationships(input_dict["question"])
        
        self.chain = (
            {
                "context": get_context,
                "question": RunnablePassthrough(),
                "entities": get_entities,
                "relationships": get_relationships
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def scrape_and_add_data(self, base_url: str, pages: List[str], selectors: Dict[str, str] = None):
        """Scrape data from a web portal and add it to the knowledge base."""
        try:
            logger.info(f"Starting web scraping from {base_url}")
            
            # Scrape the portal
            scraped_data = self.scraper.scrape_portal(base_url, pages, selectors)
            
            if not scraped_data:
                logger.warning("No data was scraped")
                return
            
            # Convert scraped data to documents format
            documents = []
            for i, data in enumerate(scraped_data):
                if data.get("content"):
                    doc = {
                        "id": f"scraped_{i}_{urlparse(data['url']).path.replace('/', '_')}",
                        "content": data["content"],
                        "metadata": {
                            "url": data["url"],
                            "title": data.get("title", ""),
                            "source": "web_scraping",
                            **data.get("metadata", {})
                        }
                    }
                    documents.append(doc)
            
            # Add documents to knowledge base
            if documents:
                self.add_documents(documents)
                logger.info(f"Added {len(documents)} scraped documents to knowledge base")
            
            # Extract entities and relationships from scraped content
            self._extract_entities_from_content(scraped_data)
            
        except Exception as e:
            logger.error(f"Error in scrape_and_add_data: {e}")
            raise
        finally:
            self.scraper.close_driver()
    
    def _extract_entities_from_content(self, scraped_data: List[Dict[str, Any]]):
        """Extract entities and relationships from scraped content."""
        entities = []
        relationships = []
        
        for data in scraped_data:
            content = data.get("content", "")
            url = data.get("url", "")
            
            # Extract potential entities (simple approach)
            # This is a basic implementation - you might want to use NER models
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
            unique_entities = list(set(words))[:10]  # Limit to 10 entities per page
            
            for i, entity in enumerate(unique_entities):
                entity_id = f"entity_{len(entities)}"
                entities.append({
                    "id": entity_id,
                    "name": entity,
                    "type": "concept",
                    "source": url
                })
                
                # Create simple relationships
                if i > 0:
                    relationships.append({
                        "source": entities[-2]["id"],
                        "target": entity_id,
                        "type": "related_to",
                        "source_url": url
                    })
        
        if entities:
            self.add_entities(entities)
        if relationships:
            self.add_relationships(relationships)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base."""
        try:
            # Process documents
            processed_docs = []
            for doc in documents:
                doc_id = doc.get("id", f"doc_{len(processed_docs)}")
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                # Split content into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_text(content)
                
                # Create Document objects
                for i, chunk in enumerate(chunks):
                    doc_obj = Document(
                        page_content=chunk,
                        metadata={
                            "doc_id": doc_id,
                            "chunk_id": i,
                            **metadata
                        }
                    )
                    processed_docs.append(doc_obj)
                
                # Store in knowledge graph
                self.knowledge_graph["documents"][doc_id] = {
                    "content": content,
                    "metadata": metadata,
                    "chunks": len(chunks)
                }
            
            # Create vector store
            if processed_docs:
                self.vectorstore = Chroma.from_documents(
                    documents=processed_docs,
                    embedding=self.embeddings
                )
                self.retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
                
            self.knowledge_graph["last_updated"] = datetime.now().isoformat()
            logger.info(f"Added {len(documents)} documents to knowledge base")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def add_entities(self, entities: List[Dict[str, Any]]):
        """Add entities to the knowledge graph."""
        if "entities" not in self.knowledge_graph:
            self.knowledge_graph["entities"] = {}
        count = 0
        for entity in entities:
            entity_id = entity.get("id")
            if entity_id:
                self.knowledge_graph["entities"][entity_id] = entity
                count += 1
        logger.info(f"Added {count} entities to knowledge graph")
    
    def add_relationships(self, relationships: List[Dict[str, Any]]):
        """Add relationships to the knowledge graph."""
        if "relationships" not in self.knowledge_graph:
            self.knowledge_graph["relationships"] = []
        count = len(relationships)
        self.knowledge_graph["relationships"].extend(relationships)
        logger.info(f"Added {count} relationships to knowledge graph")
    
    def _get_relevant_entities(self, question: str) -> str:
        """Get relevant entities based on the question."""
        relevant_entities = []
        question_lower = question.lower()
        entities = self.knowledge_graph.get("entities", {})
        for entity_id, entity in entities.items():
            entity_name = entity.get("name", "").lower()
            entity_type = entity.get("type", "").lower()
            if entity_name in question_lower or entity_type in question_lower:
                relevant_entities.append(f"{entity_id}: {entity.get('name', 'Unknown')} ({entity.get('type', 'Unknown')})")
        return "\n".join(relevant_entities) if relevant_entities else "No relevant entities found"
    
    def _get_relevant_relationships(self, question: str) -> str:
        """Get relevant relationships based on the question."""
        relevant_relationships = []
        question_lower = question.lower()
        relationships = self.knowledge_graph.get("relationships", [])
        for rel in relationships:
            source = rel.get("source", "").lower()
            target = rel.get("target", "").lower()
            rel_type = rel.get("type", "").lower()
            if any(term in question_lower for term in [source, target, rel_type]):
                relevant_relationships.append(
                    f"{rel.get('source', 'Unknown')} --{rel.get('type', 'related')}--> {rel.get('target', 'Unknown')}"
                )
        return "\n".join(relevant_relationships) if relevant_relationships else "No relevant relationships found"
    
    def query(self, question: str, debug_mode: bool = False) -> str:
        """Query the knowledge base with a question."""
        try:
            if debug_mode:
                # Debug mode - show retrieval steps
                if self.retriever:
                    docs = self.retriever.get_relevant_documents(question)
                    debug_info = f"Retrieved {len(docs)} documents:\n"
                    for i, doc in enumerate(docs):
                        debug_info += f"Doc {i+1}: {doc.metadata.get('doc_id', 'Unknown')} - {doc.page_content[:100]}...\n"
                    
                    entities = self._get_relevant_entities(question)
                    relationships = self._get_relevant_relationships(question)
                    
                    debug_info += f"\nRelevant entities:\n{entities}\n"
                    debug_info += f"\nRelevant relationships:\n{relationships}\n"
                    
                    return debug_info
                else:
                    return "No documents available for retrieval"
            
            # Normal query
            response = self.chain.invoke({"question": question})
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def get_sources(self, question: str) -> str:
        """Get source documents for a question."""
        if not self.retriever:
            return "No documents available"
        
        try:
            docs = self.retriever.get_relevant_documents(question)
            sources = []
            
            for doc in docs:
                doc_id = doc.metadata.get("doc_id", "Unknown")
                chunk_id = doc.metadata.get("chunk_id", "Unknown")
                sources.append(f"Document ID: {doc_id}, Chunk: {chunk_id}")
            
            return "\n".join(sources) if sources else "No relevant sources found"
            
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return f"Error retrieving sources: {str(e)}"
    
    def save_knowledge_graph(self, filepath: str):
        """Save the knowledge graph to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.knowledge_graph, f, indent=2)
            logger.info(f"Knowledge graph saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")
    
    def load_knowledge_graph(self, filepath: str):
        """Load the knowledge graph from a file."""
        try:
            with open(filepath, 'r') as f:
                self.knowledge_graph = json.load(f)
            logger.info(f"Knowledge graph loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")


def create_sample_data():
    """Create sample data for testing the bot."""
    # Sample documents
    documents = [
        {
            "id": "doc_001",
            "content": """
            PortalHelper is a comprehensive web portal that provides various services to users.
            Users can reset their passwords using the "Forgot Password" link on the login page.
            For technical support, contact support@portal.com or call 1-800-HELP.
            The portal features include user authentication, document management, and real-time notifications.
            """,
            "metadata": {"category": "general", "author": "admin"}
        },
        {
            "id": "doc_002", 
            "content": """
            User authentication in PortalHelper supports multiple methods including email/password,
            two-factor authentication, and social login options. The system automatically locks
            accounts after 5 failed login attempts. Password requirements include at least 8 characters
            with uppercase, lowercase, numbers, and special characters.
            """,
            "metadata": {"category": "security", "author": "security_team"}
        },
        {
            "id": "doc_003",
            "content": """
            Document management features allow users to upload, organize, and share files.
            Supported file types include PDF, DOC, DOCX, TXT, and images. File size limit is 50MB.
            Users can create folders, set permissions, and collaborate on documents in real-time.
            """,
            "metadata": {"category": "features", "author": "dev_team"}
        }
    ]
    
    # Sample entities
    entities = [
        {"id": "user_auth", "name": "User Authentication", "type": "feature"},
        {"id": "doc_mgmt", "name": "Document Management", "type": "feature"},
        {"id": "support", "name": "Technical Support", "type": "service"},
        {"id": "admin", "name": "Administrator", "type": "role"}
    ]
    
    # Sample relationships
    relationships = [
        {"source": "user_auth", "target": "support", "type": "requires"},
        {"source": "doc_mgmt", "target": "user_auth", "type": "depends_on"},
        {"source": "admin", "target": "user_auth", "type": "manages"}
    ]
    
    return documents, entities, relationships


def main():
    """Main function to demonstrate the Knowledge Graph Bot."""
    print("🤖 Initializing PortalHelper AI Assistant...")
    
    # Initialize the bot
    bot = KnowledgeGraphBot()
    
    # Load sample data
    print("📚 Loading sample knowledge base...")
    documents, entities, relationships = create_sample_data()
    
    # Add data to the bot
    bot.add_documents(documents)
    bot.add_entities(entities)
    bot.add_relationships(relationships)
    
    print("✅ Knowledge Graph Bot is ready!")
    print("\n" + "="*50)
    print("PortalHelper AI Assistant")
    print("="*50)
    print("Commands:")
    print("- Ask any question about the portal")
    print("- Type 'debug mode' to see retrieval steps")
    print("- Type 'sources' to see document sources")
    print("- Type 'scrape' to scrape a web portal")
    print("- Type 'quit' to exit")
    print("="*50)
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'debug mode':
                response = bot.query("How do I reset my password?", debug_mode=True)
                print(f"\n🤖 Assistant (Debug Mode):\n{response}")
            elif user_input.lower() == 'sources':
                sources = bot.get_sources("How do I reset my password?")
                print(f"\n📚 Sources:\n{sources}")
            elif user_input.lower() == 'scrape':
                print("\n🌐 Web Scraping Mode")
                base_url = input("Enter base URL: ").strip()
                pages = input("Enter pages to scrape (comma-separated, e.g., /about, /help): ").strip().split(',')
                pages = [p.strip() for p in pages if p.strip()]
                
                if base_url and pages:
                    print(f"Scraping {len(pages)} pages from {base_url}...")
                    bot.scrape_and_add_data(base_url, pages)
                    print("✅ Scraping completed!")
                else:
                    print("❌ Invalid input")
            else:
                response = bot.query(user_input)
                print(f"\n🤖 Assistant: {response}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

