# QA Agent

A sophisticated question-answering system that can crawl websites, process their content, and answer questions based on the indexed information. Built with modern ML tools and FastAPI.

## Features

- Web crawling with respect for robots.txt and rate limiting
- Advanced text processing using transformer models
- Vector-based search using FAISS
- RESTful API with FastAPI
- Response caching for improved performance
- Docker support for easy deployment

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv qa-env
source qa-env/bin/activate  # On Windows: qa-env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the API Server

```bash
python api.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### 1. Process URL
```http
POST /process
Content-Type: application/json

{
    "url": "https://example.com"
}
```

#### 2. Ask Questions
```http
POST /ask
Content-Type: application/json

{
    "question": "Your question here",
    "top_k": 3
}
```

#### 3. Health Check
```http
GET /health
```

### Docker Deployment

1. Build the image:
```bash
docker build -t qa-agent .
```

2. Run the container:
```bash
docker run -p 8000:8000 qa-agent
```

## Technical Details

The system consists of several components:

- **Crawler**: Recursively crawls websites while respecting domain boundaries
- **Processor**: Processes HTML content into clean text
- **Indexer**: Creates and manages vector embeddings using FAISS
- **QA Agent**: Coordinates the components and handles question answering
- **API**: Provides RESTful interface with FastAPI

## Dependencies

- `sentence-transformers`: For text embeddings
- `faiss-cpu`: For efficient vector similarity search
- `langchain`: For LLM operations
- `fastapi`: For the REST API
- `beautifulsoup4` & `trafilatura`: For web crawling and content extraction
- `cachetools`: For response caching
- Full list in `requirements.txt`

## Error Handling

The API includes comprehensive error handling:
- Invalid URLs
- Failed crawling attempts
- Processing errors
- No relevant information found

## Performance Considerations

- Uses TTL caching for frequently asked questions
- Implements efficient vector search with FAISS
- Handles concurrent requests through FastAPI's async support
