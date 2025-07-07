#!/usr/bin/env python3
"""
Example usage of the Knowledge Graph Bot with custom data.
This script demonstrates how to create and use the bot with your own content.
"""

from main import KnowledgeGraphBot
import json

def create_custom_data():
    """Create custom data for a specific use case."""
    
    # Custom documents for a company knowledge base
    documents = [
        {
            "id": "company_overview",
            "content": """
            TechCorp is a leading technology company specializing in AI and machine learning solutions.
            Founded in 2020, we have grown to over 500 employees across 10 countries.
            Our main products include AI-powered chatbots, data analytics platforms, and cloud solutions.
            We serve clients in healthcare, finance, and retail industries.
            """,
            "metadata": {"category": "company", "author": "marketing"}
        },
        {
            "id": "hr_policies",
            "content": """
            Employee benefits include health insurance, 401k matching, and unlimited PTO.
            Remote work is supported with flexible hours. Office locations are in San Francisco,
            New York, and London. New employees get 2 weeks of onboarding training.
            Performance reviews are conducted quarterly with 360-degree feedback.
            """,
            "metadata": {"category": "hr", "author": "hr_team"}
        },
        {
            "id": "tech_stack",
            "content": """
            Our technology stack includes Python, JavaScript, React, Node.js, and AWS.
            We use Docker for containerization and Kubernetes for orchestration.
            Database systems include PostgreSQL, MongoDB, and Redis.
            CI/CD pipeline uses GitHub Actions and Jenkins.
            """,
            "metadata": {"category": "technology", "author": "engineering"}
        },
        {
            "id": "product_features",
            "content": """
            Our AI chatbot platform supports multiple languages and integrates with Slack, Teams, and Discord.
            Features include natural language processing, sentiment analysis, and automated responses.
            The platform can handle up to 10,000 concurrent conversations with 99.9% uptime.
            Custom training data can be uploaded to improve response accuracy.
            """,
            "metadata": {"category": "product", "author": "product_team"}
        }
    ]
    
    # Custom entities
    entities = [
        {"id": "techcorp", "name": "TechCorp", "type": "company"},
        {"id": "ai_chatbot", "name": "AI Chatbot Platform", "type": "product"},
        {"id": "hr_dept", "name": "Human Resources", "type": "department"},
        {"id": "eng_dept", "name": "Engineering", "type": "department"},
        {"id": "remote_work", "name": "Remote Work Policy", "type": "policy"},
        {"id": "health_insurance", "name": "Health Insurance", "type": "benefit"}
    ]
    
    # Custom relationships
    relationships = [
        {"source": "techcorp", "target": "ai_chatbot", "type": "develops"},
        {"source": "hr_dept", "target": "remote_work", "type": "manages"},
        {"source": "eng_dept", "target": "ai_chatbot", "type": "builds"},
        {"source": "remote_work", "target": "health_insurance", "type": "includes"},
        {"source": "techcorp", "target": "hr_dept", "type": "employs"},
        {"source": "techcorp", "target": "eng_dept", "type": "employs"}
    ]
    
    return documents, entities, relationships

def main():
    """Main function demonstrating the bot usage."""
    print("🚀 Initializing TechCorp Knowledge Graph Bot...")
    
    # Initialize the bot
    bot = KnowledgeGraphBot()
    
    # Load custom data
    print("📚 Loading custom company data...")
    documents, entities, relationships = create_custom_data()
    
    # Add data to the bot
    bot.add_documents(documents)
    bot.add_entities(entities)
    bot.add_relationships(relationships)
    
    print("✅ Bot is ready with TechCorp knowledge base!")
    print("\n" + "="*60)
    print("TechCorp AI Assistant - Knowledge Graph Demo")
    print("="*60)
    
    # Example queries
    example_queries = [
        "What does TechCorp do?",
        "What are the employee benefits?",
        "What technology stack does the company use?",
        "Tell me about the AI chatbot platform",
        "What are the remote work policies?",
        "How many employees does TechCorp have?"
    ]
    
    print("\n📝 Example Queries and Responses:")
    print("-" * 60)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Query: {query}")
        response = bot.query(query)
        print(f"   Response: {response}")
        print("-" * 60)
    
    # Interactive mode
    print("\n🎯 Interactive Mode - Ask your own questions!")
    print("Type 'quit' to exit, 'debug' for debug mode, 'sources' for document sources")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'debug':
                response = bot.query("What does TechCorp do?", debug_mode=True)
                print(f"\n🤖 Assistant (Debug Mode):\n{response}")
            elif user_input.lower() == 'sources':
                sources = bot.get_sources("What does TechCorp do?")
                print(f"\n📚 Sources:\n{sources}")
            else:
                response = bot.query(user_input)
                print(f"\n🤖 Assistant: {response}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    # Save knowledge graph
    print("\n💾 Saving knowledge graph...")
    bot.save_knowledge_graph("techcorp_knowledge_graph.json")
    print("✅ Knowledge graph saved to techcorp_knowledge_graph.json")

if __name__ == "__main__":
    main() 