#!/usr/bin/env python3
"""
Example script demonstrating web scraping functionality with the Knowledge Graph Bot.
This script shows how to scrape data from web portals and add it to the knowledge base.
"""

from main import KnowledgeGraphBot
import time

def scrape_example_portal():
    """Example of scraping a web portal and adding data to the knowledge base."""
    
    print("🌐 Web Scraping Example")
    print("="*50)
    
    # Initialize the bot
    bot = KnowledgeGraphBot()
    
    # Example: Scrape a documentation site
    base_url = "https://docs.python.org"
    pages = [
        "/3/",
        "/3/tutorial/",
        "/3/tutorial/introduction.html",
        "/3/tutorial/controlflow.html"
    ]
    
    # Define CSS selectors for content extraction
    selectors = {
        "content": "div.body",  # Main content area
        "title": "h1",          # Page title
        "navigation": "div.sphinxsidebar"  # Navigation menu
    }
    
    print(f"Scraping {len(pages)} pages from {base_url}...")
    print("Pages to scrape:")
    for page in pages:
        print(f"  - {base_url}{page}")
    
    try:
        # Scrape the portal
        bot.scrape_and_add_data(base_url, pages, selectors)
        print("✅ Scraping completed successfully!")
        
        # Test the knowledge base with some queries
        test_queries = [
            "What is Python?",
            "How do I use control flow in Python?",
            "What are the basic concepts?",
            "Tell me about Python tutorials"
        ]
        
        print("\n🧪 Testing the knowledge base with scraped data:")
        print("-" * 50)
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            response = bot.query(query)
            print(f"Response: {response}")
            print("-" * 30)
        
        # Save the knowledge graph
        bot.save_knowledge_graph("scraped_knowledge_graph.json")
        print("\n💾 Knowledge graph saved to 'scraped_knowledge_graph.json'")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")

def interactive_scraping():
    """Interactive web scraping session."""
    
    print("🎯 Interactive Web Scraping")
    print("="*50)
    
    # Initialize the bot
    bot = KnowledgeGraphBot()
    
    while True:
        print("\nOptions:")
        print("1. Scrape a web portal")
        print("2. Query the knowledge base")
        print("3. View sources")
        print("4. Debug mode")
        print("5. Save knowledge graph")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n🌐 Web Scraping Setup")
            base_url = input("Enter base URL (e.g., https://example.com): ").strip()
            
            if not base_url.startswith(('http://', 'https://')):
                base_url = 'https://' + base_url
            
            pages_input = input("Enter pages to scrape (comma-separated, e.g., /about, /help, /contact): ").strip()
            pages = [p.strip() for p in pages_input.split(',') if p.strip()]
            
            if base_url and pages:
                print(f"\nScraping {len(pages)} pages from {base_url}...")
                try:
                    bot.scrape_and_add_data(base_url, pages)
                    print("✅ Scraping completed!")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("❌ Invalid input")
                
        elif choice == "2":
            query = input("\nEnter your question: ").strip()
            if query:
                response = bot.query(query)
                print(f"\n🤖 Assistant: {response}")
            else:
                print("❌ Please enter a question")
                
        elif choice == "3":
            query = input("\nEnter query to find sources for: ").strip()
            if query:
                sources = bot.get_sources(query)
                print(f"\n📚 Sources:\n{sources}")
            else:
                print("❌ Please enter a query")
                
        elif choice == "4":
            query = input("\nEnter query for debug mode: ").strip()
            if query:
                debug_response = bot.query(query, debug_mode=True)
                print(f"\n🐛 Debug Mode:\n{debug_response}")
            else:
                print("❌ Please enter a query")
                
        elif choice == "5":
            filename = input("Enter filename to save (e.g., my_knowledge_graph.json): ").strip()
            if filename:
                bot.save_knowledge_graph(filename)
                print(f"✅ Knowledge graph saved to {filename}")
            else:
                print("❌ Please enter a filename")
                
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def main():
    """Main function."""
    print("🤖 Knowledge Graph Bot - Web Scraping Examples")
    print("="*60)
    
    print("\nChoose an option:")
    print("1. Run example scraping (Python docs)")
    print("2. Interactive scraping session")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        scrape_example_portal()
    elif choice == "2":
        interactive_scraping()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 