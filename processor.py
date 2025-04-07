from langchain.text_splitter import RecursiveCharacterTextSplitter
import trafilatura
from typing import List
from langchain.schema import Document

class ContentProcessor:
    @staticmethod
    def extract_text(html: str, url: str) -> str:
        """Extract clean text from HTML using trafilatura."""
        text = trafilatura.extract(html)
        return text if text else ""

    @staticmethod
    def chunk_text(text: str, url: str, chunk_size: int = 300) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,  # Smaller chunks
            chunk_overlap=30,       # Moderate overlap
            separators=["\n\n", "\n", ". ", " "]  # Split on natural boundaries
        )
        chunks = splitter.create_documents([text], metadatas=[{"source": url}])
        return chunks
    
if __name__ == "__main__":
    # Larger mock HTML
    html = """
    <html>
        <body>
            <h1>Slack Features</h1>
            <p>Slack offers these features:</p>
            <ul>
                <li>Channels for team communication</li>
                <li>Direct messages</li>
                <li>File sharing</li>
            </ul>
            <h2>Integrations</h2>
            <p>Slack works with Google Drive, Zoom, and GitHub.</p>
        </body>
    </html>
    """
    processor = ContentProcessor()
    text = processor.extract_text(html, "https://help.slack.com")
    print("Extracted Text:\n", text[:200] + "...")  # Print first 200 chars
    chunks = processor.chunk_text(text, "https://help.slack.com")
    print(f"\nExtracted {len(chunks)} chunks.")
    print("\nFirst chunk:", chunks[0].page_content)