from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Tuple
from langchain.schema import Document

class VectorIndex:
    def __init__(self):
        # Use a smaller model for compatibility
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.documents = []  # Stores (text, metadata) pairs

    def add_documents(self, documents: List[Document]):
        """Add documents to the FAISS index."""
        if not documents:
            return

        # Extract text and metadata
        texts = [doc.page_content for doc in documents]
        self.documents.extend(documents)

        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)

        # Initialize index if not exists
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])

        # Add embeddings to index
        self.index.add(np.array(embeddings, dtype=np.float32))

    def search(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """Search the index for top-k results with confidence scores."""
        if not self.index:
            return []

        # Encode query
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        distances, indices = self.index.search(query_embedding, k)

        # Convert L2 distances to similarity scores
        # L2 distance: smaller is better, so we convert to similarity
        max_distance = np.max(distances) + 1e-6  # Avoid division by zero
        similarities = 1 - (distances / max_distance)  # Normalize to [0, 1]

        # Return matched documents with confidence scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                confidence = float(similarities[0][i])
                results.append((self.documents[idx], confidence))
        return results
    
if __name__ == "__main__":
    # Test with sample documents
    from langchain.schema import Document

    index = VectorIndex()
    docs = [
        Document(page_content="Slack integrates with Zoom for video calls.", metadata={"source": "https://help.slack.com"}),
        Document(page_content="Use channels to organize team discussions.", metadata={"source": "https://help.slack.com"})
    ]
    index.add_documents(docs)

    # Search
    results = index.search("How to use Zoom with Slack?")
    if results:
        doc, confidence = results[0]
        print(f"Top result ({confidence:.2f} confidence):", doc.page_content)
    else:
        print("No results")