#!/usr/bin/env python3
"""
Simple test script to verify the core functionality works.
This version doesn't use the complex LangChain dependencies.
"""

import json
from datetime import datetime
from typing import List, Dict, Any
import re

class SimpleKnowledgeGraphBot:
    """Simplified version of the Knowledge Graph Bot for testing."""
    
    def __init__(self):
        """Initialize the simplified bot."""
        # Knowledge graph data
        self.knowledge_graph = {
            "entities": {},
            "relationships": [],
            "documents": {},
            "last_updated": None
        }
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base."""
        for doc in documents:
            doc_id = doc.get("id", f"doc_{len(self.knowledge_graph['documents'])}")
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Store in knowledge graph
            self.knowledge_graph["documents"][doc_id] = {
                "content": content,
                "metadata": metadata
            }
        
        self.knowledge_graph["last_updated"] = datetime.now().isoformat()
        print(f"Added {len(documents)} documents to knowledge base")
    
    def add_entities(self, entities: List[Dict[str, Any]]):
        """Add entities to the knowledge graph."""
        for entity in entities:
            entity_id = entity.get("id")
            if entity_id:
                self.knowledge_graph["entities"][entity_id] = entity
        print(f"Added {len(entities)} entities to knowledge graph")
    
    def add_relationships(self, relationships: List[Dict[str, Any]]):
        """Add relationships to the knowledge graph."""
        self.knowledge_graph["relationships"].extend(relationships)
        print(f"Added {len(relationships)} relationships to knowledge graph")
    
    def query(self, question: str) -> str:
        """Simple query implementation."""
        # Search through documents for relevant content
        relevant_content = []
        
        for doc_id, doc in self.knowledge_graph["documents"].items():
            content = doc["content"].lower()
            question_lower = question.lower()
            
            # Simple keyword matching
            if any(word in content for word in question_lower.split()):
                relevant_content.append(f"[{doc_id}]: {doc['content'][:200]}...")
        
        if relevant_content:
            return f"Found relevant information:\n" + "\n".join(relevant_content)
        else:
            return "I couldn't find information on this. Try rephrasing your question."
    
    def save_knowledge_graph(self, filepath: str):
        """Save the knowledge graph to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.knowledge_graph, f, indent=2)
            print(f"Knowledge graph saved to {filepath}")
        except Exception as e:
            print(f"Error saving knowledge graph: {e}")

def create_sample_data():
    """Create sample data for testing."""
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
        }
    ]
    
    entities = [
        {"id": "user_auth", "name": "User Authentication", "type": "feature"},
        {"id": "support", "name": "Technical Support", "type": "service"}
    ]
    
    relationships = [
        {"source": "user_auth", "target": "support", "type": "requires"}
    ]
    
    return documents, entities, relationships

def main():
    """Test the simplified bot."""
    print("🧪 Testing Simple Knowledge Graph Bot")
    print("="*50)
    
    # Initialize the bot
    bot = SimpleKnowledgeGraphBot()
    
    # Load sample data
    print("📚 Loading sample data...")
    documents, entities, relationships = create_sample_data()
    
    # Add data to the bot
    bot.add_documents(documents)
    bot.add_entities(entities)
    bot.add_relationships(relationships)
    
    print("✅ Bot is ready!")
    print("\n" + "="*50)
    print("Simple Knowledge Graph Bot Test")
    print("="*50)
    
    # Test queries
    test_queries = [
        "How do I reset my password?",
        "What are the password requirements?",
        "How do I contact support?",
        "What features does PortalHelper have?"
    ]
    
    for query in test_queries:
        print(f"\n👤 Query: {query}")
        response = bot.query(query)
        print(f"🤖 Response: {response}")
        print("-" * 50)
    
    # Save knowledge graph
    bot.save_knowledge_graph("test_knowledge_graph.json")
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    main() 