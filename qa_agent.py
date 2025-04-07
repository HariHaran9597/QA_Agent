import argparse
from crawler import Crawler
from processor import ContentProcessor
from indexer import VectorIndex
from typing import List
from langchain.schema import Document
import sys

class QAAgent:
    def __init__(self):
        self.index = VectorIndex()
        self.crawled_urls = set()

    def process_url(self, url: str) -> None:
        """Crawl, extract, and index the website content."""
        print(f"🕷️  Crawling {url}...")
        crawler = Crawler(url)
        crawler.crawl()
        
        print(f"📝 Processing {len(crawler.pages)} pages...")
        for page_url, html in crawler.pages:
            # Skip already processed URLs
            if page_url in self.crawled_urls:
                continue
                
            self.crawled_urls.add(page_url)
            text = ContentProcessor.extract_text(html, page_url)
            if not text.strip():
                continue
                
            chunks = ContentProcessor.chunk_text(text, page_url)
            self.index.add_documents(chunks)
        print(f"✅ Indexed {len(self.crawled_urls)} pages. Ready for questions!")

    def answer_question(self, question: str, top_k: int = 3) -> str:
        """Search the index and return formatted answers with sources and confidence scores."""
        if not question.strip():
            return "⚠️ Please enter a valid question."
            
        results = self.index.search(question, k=top_k)
        if not results:
            return "❌ No information found in the documentation."
        
        # Deduplicate by source URL and content
        seen = set()
        unique_results = []
        for doc, confidence in results:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append((doc, confidence))
        
        # Format answers with confidence scores
        formatted_answers = []
        for i, (doc, confidence) in enumerate(unique_results[:top_k], 1):
            confidence_percent = int(confidence * 100)
            formatted_answers.append(
                f"📖 Answer {i} (Confidence: {confidence_percent}%):\n{doc.page_content.strip()}\n\n"
                f"🔗 Source: {doc.metadata['source']}"
            )
            
        return "\n\n---\n\n".join(formatted_answers)

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered Help Documentation QA Agent",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--url", 
        action="append",
        required=True,
        help="Base URL of the help website (can be specified multiple times)"
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=3,
        help="Number of answers to return"
    )
    args = parser.parse_args()

    agent = QAAgent()
    for url in args.url:
        agent.process_url(url)

    print("\nAsk questions about the documentation (type 'exit' or press Ctrl+C to quit):")
    try:
        while True:
            try:
                question = input("\n> ").strip()
                if question.lower() in ["exit", "quit"]:
                    break
                    
                if not question:
                    print("⚠️ Please enter a question.")
                    continue
                    
                print("\n" + agent.answer_question(question, args.top_k))
                
            except KeyboardInterrupt:
                print("\n\nUse 'exit' to quit or continue asking questions.")
                continue
                
    except (KeyboardInterrupt, EOFError):
        print("\n\n🚀 Session ended. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()