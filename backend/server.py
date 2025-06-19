from fastapi import FastAPI
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Initialize FastAPI and FastMCP
app = FastAPI()
mcp = FastMCP(app)

# ====================
# 🔹 Web Scraper Tool
# ====================
class ScrapeRequest(BaseModel):
    url: str
    extract_rules: Optional[Dict] = None

@mcp.tool()
@app.post("/scrape")
async def web_scraper(request: ScrapeRequest):
    """Scrape company website and extract structured data"""
    try:
        async with httpx.AsyncClient() as client:
            # Fetch HTML
            response = await client.get(request.url, follow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metadata
            metadata = {
                "title": soup.title.string if soup.title else None,
                "links": [a['href'] for a in soup.find_all('a', href=True) if a.get('href')],
                "text_content": soup.get_text(separator=' ', strip=True)[:5000]  # First 5000 chars
            }
            
            # Apply extraction rules if provided
            if request.extract_rules:
                extracted_data = {}
                if "products" in request.extract_rules:
                    products = [p.text for p in soup.select(request.extract_rules["products"])]
                    extracted_data["products"] = products
                if "careers" in request.extract_rules:
                    careers = [c.text for c in soup.select(request.extract_rules["careers"])]
                    extracted_data["careers"] = careers
                metadata["extracted_data"] = extracted_data
            
            return metadata
            
    except Exception as e:
        return {"error": str(e)}

# ==========================
# 🔹 Video Analyzer Tool
# ==========================
class VideoRequest(BaseModel):
    video_url: str
    analyze_visuals: bool = False  # Placeholder for future implementation

@mcp.tool()
@app.post("/analyze-video")
async def video_analyzer(request: VideoRequest):
    """Extract transcripts and analyze YouTube videos"""
    try:
        # Extract video ID from URL
        video_id = request.video_url.split("v=")[-1].split("&")[0]
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([t['text'] for t in transcript_list])
        
        return {
            "transcript": transcript,
            "key_frames": [],  # Could use OpenCV for frame analysis
            "sentiment": "positive"  # Could use TextBlob/NLTK for sentiment
        }
    except Exception as e:
        return {"error": str(e)}

# ==========================
# 🔹 LinkedIn Simulator Tool
# ==========================
class LinkedInRequest(BaseModel):
    company_name: str

@mcp.tool()
@app.post("/linkedin-data")
async def linkedin_simulator(request: LinkedInRequest):
    """Simulate LinkedIn data (real API requires authentication)"""
    try:
        # Simulated data - in a real scenario you'd use the LinkedIn API
        return {
            "hiring_trends": [
                "Increased hiring in AI/ML roles",
                "5 new job postings in engineering"
            ],
            "recent_updates": [
                f"{request.company_name} announced new cloud product",
                "CEO spoke at recent tech conference"
            ]
        }
    except Exception as e:
        return {"error": str(e)}

# ==========================
# 🔹 Summarizer Tool
# ==========================
class SummaryRequest(BaseModel):
    text: str
    focus_areas: List[str] = ["strategy", "products", "hiring"]

@mcp.tool()
@app.post("/summarize")
async def summarizer(request: SummaryRequest):
    """Generate strategic summary using LLM"""
    try:
        prompt = ChatPromptTemplate.from_template("""
        Analyze this text focusing on {focus_areas}:
        {text}
        
        Generate a strategic summary highlighting:
        - Key initiatives
        - Product developments
        - Hiring trends
        - Competitive positioning
        """)
        
        llm = ChatNVIDIA(
            model="meta/llama3-70b-instruct",
            temperature=0.3
        )

        chain = prompt | llm
        result = await chain.ainvoke({
            "text": request.text,
            "focus_areas": ", ".join(request.focus_areas)
        })

        return {"summary": result.content}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)