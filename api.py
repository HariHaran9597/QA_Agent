from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qa_agent import QAAgent
from cachetools import TTLCache
from typing import List, Optional
import uvicorn

app = FastAPI(title="QA Agent API")

# Initialize QA Agent
agent = QAAgent()

# Cache configuration: 100 items, 5 minutes TTL
question_cache = TTLCache(maxsize=100, ttl=300)

class URLRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class Answer(BaseModel):
    content: str
    source: str
    confidence: float

class AnswerResponse(BaseModel):
    answers: List[Answer]

@app.post("/process")
async def process_url(request: URLRequest):
    """Process and index content from a URL."""
    try:
        agent.process_url(request.url)
        return {"status": "success", "message": f"Indexed content from {request.url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Answer a question using the indexed content."""
    cache_key = f"{request.question}:{request.top_k}"
    
    # Check cache first
    if cache_key in question_cache:
        return question_cache[cache_key]

    # Get answers from agent
    raw_response = agent.answer_question(request.question, request.top_k)
    if "❌" in raw_response:
        raise HTTPException(status_code=404, detail="No information found")

    # Parse the raw response into structured answers
    answers = []
    sections = raw_response.split("\n\n---\n\n")
    
    for section in sections:
        lines = section.split("\n")
        content = "\n".join(line for line in lines if not line.startswith("🔗"))
        source = next((line.replace("🔗 Source: ", "") for line in lines if line.startswith("🔗")), "")
        
        # Calculate confidence score based on content relevance
        # This is a simple implementation that could be improved
        confidence = min(1.0, len(content.split()) / 100)  # Simple length-based confidence
        
        answers.append(Answer(
            content=content.replace("📖 Answer 1:\n", "").strip(),
            source=source,
            confidence=round(confidence, 2)
        ))

    response = AnswerResponse(answers=answers)
    question_cache[cache_key] = response
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)