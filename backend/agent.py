from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
import httpx
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import asyncio
import re
from serpapi import GoogleSearch

# Initialize tools and LLM
llm = ChatNVIDIA(
    model="meta/llama3-70b-instruct",

    temperature=0.3
)

# ====================
# 🏗️ State & Workflow
# ====================

class AgentState(TypedDict):
    query: str
    company_name: str
    website_url: Optional[str]
    youtube_urls: List[str]
    website_data: Optional[dict]
    youtube_data: Optional[dict]
    linkedin_data: Optional[dict]
    report: Optional[str]

# ====================
# 🛠️ Tool Functions
# ====================

async def find_company_resources(state: AgentState) -> dict:
    """Search for company website and YouTube videos using Google Search"""
    query = state["query"]
    
    # Get company website
    website_search = GoogleSearch({
        "q": f"{query} official website",
        "location": "india",
        "api_key": serp_api_key
    })
    website_result = website_search.get_dict()
    website_url = extract_first_organic_url(website_result)
    
    # Get YouTube videos
    youtube_search = GoogleSearch({
        "q": f"{query} YouTube channel official",
        "location": "india",
        "api_key": serp_api_key
    })
    youtube_result = youtube_search.get_dict()
    youtube_urls = extract_youtube_urls(youtube_result)[:2]  # Limit to 2 videos
    
    return {
        "company_name": query,
        "website_url": website_url,
        "youtube_urls": youtube_urls
    }

async def scrape_website(state: AgentState) -> dict:
    """Scrape company website"""
    if not state.get("website_url"):
        return {"website_data": {"error": "No website found"}}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(state["website_url"], follow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                "website_data": {
                    "title": soup.title.string if soup.title else None,
                    "content": soup.get_text(separator=' ', strip=True)[:5000],
                    "products": extract_products(soup),
                    "careers": extract_careers(soup)
                }
            }
    except Exception as e:
        return {"website_data": {"error": str(e)}}

async def analyze_youtube_videos(state: AgentState) -> dict:
    """Analyze found YouTube videos"""
    if not state.get("youtube_urls"):
        return {"youtube_data": {"error": "No videos found"}}
    
    try:
        video_data = []
        for url in state["youtube_urls"]:
            video_id = url.split("v=")[-1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            video_data.append({
                "url": url,
                "transcript": " ".join([t['text'] for t in transcript]),
                "key_topics": extract_key_topics(transcript)
            })
        
        return {"youtube_data": video_data}
    except Exception as e:
        return {"youtube_data": {"error": str(e)}}

async def get_linkedin_data(state: AgentState) -> dict:
    """Search LinkedIn data using Google"""
    linkedin_search = GoogleSearch({
        "q": f"{state['company_name']} site:linkedin.com",
        "location": "india",
        "api_key": serp_api_key
    })
    linkedin_result = linkedin_search.get_dict()
    
    return {
        "linkedin_data": {
            "hiring_trends": extract_linkedin_hiring(linkedin_result),
            "recent_updates": extract_linkedin_updates(linkedin_result)
        }
    }

def generate_report(state: AgentState) -> dict:
    """Generate final competitive intelligence report"""
    sections = []
    
    # Website Data
    if state.get("website_data"):
        sections.append(f"""
### Website Analysis
- **Company Description**: {state['website_data'].get('content','')[:300]}...
- **Key Products**: {', '.join(state['website_data'].get('products', []))}
- **Career Opportunities**: {', '.join(state['website_data'].get('careers', []))}
""")
    
    # YouTube Data
    if state.get("youtube_data") and not isinstance(state['youtube_data'], dict):
        sections.append("""
### YouTube Analysis
""" + "\n".join([
f"- Video {i+1}: Topics - {', '.join(vid['key_topics'])}\n  {vid['transcript'][:100]}..."
for i, vid in enumerate(state['youtube_data'])
]))
    
    # LinkedIn Data
    if state.get("linkedin_data"):
        sections.append(f"""
### LinkedIn Insights
- **Hiring Trends**: {', '.join(state['linkedin_data'].get('hiring_trends', []))}
- **Recent Activity**: {', '.join(state['linkedin_data'].get('recent_updates', []))}
""")
    
    # Generate with LLM
    prompt = ChatPromptTemplate.from_template("""
    Create a professional competitive intelligence report about {company} using these data:
    {sections}
    
    Structure it with:
    1. Executive Summary
    2. Key Findings
    3. Strategic Recommendations
    """)
    
    chain = prompt | llm
    report = chain.invoke({
        "company": state["company_name"],
        "sections": "\n".join(sections)
    })
    
    return {"report": report.content}

# ====================
# 🔧 Helper Functions
# ====================

def extract_first_organic_url(search_results: dict) -> Optional[str]:
    """Extract first organic URL from Google search results"""
    if 'organic_results' in search_results and search_results['organic_results']:
        return search_results['organic_results'][0].get('link')
    return None

def extract_youtube_urls(search_results: dict) -> List[str]:
    """Extract YouTube URLs from Google search results"""
    urls = []
    if 'organic_results' in search_results:
        for result in search_results['organic_results']:
            if 'youtube.com' in result.get('link', ''):
                urls.append(result['link'])
    return urls[:2]  # Return max 2 URLs

def extract_products(soup) -> List[str]:
    """Extract products from website"""
    return list(set(
        p.text.strip() for p in soup.select('[class*="product"], [href*="product"], [class*="service"]')
        if p.text.strip()
    ))[:5]

def extract_careers(soup) -> List[str]:
    """Extract career info from website"""
    return list(set(
        c.text.strip() for c in soup.select('[href*="career"], [href*="job"], [class*="career"]')
        if c.text.strip()
    ))[:3]

def extract_key_topics(transcript: List[dict]) -> List[str]:
    """Extract key topics from YouTube transcript"""
    words = " ".join([t['text'] for t in transcript]).lower().split()
    return list(set(
        w for w in words 
        if len(w) > 5 and w.isalpha()
    ))[:5]

def extract_linkedin_hiring(search_results: dict) -> List[str]:
    """Extract hiring information from LinkedIn search results"""
    hiring_info = []
    if 'organic_results' in search_results:
        for result in search_results['organic_results']:
            if 'career' in result.get('link', '') or 'job' in result.get('link', ''):
                hiring_info.append(result.get('title', 'No title'))
    return hiring_info[:3] or ["No hiring information found"]

def extract_linkedin_updates(search_results: dict) -> List[str]:
    """Extract recent updates from LinkedIn search results"""
    updates = []
    if 'organic_results' in search_results:
        for result in search_results['organic_results']:
            if 'post' in result.get('link', '') or 'update' in result.get('link', ''):
                updates.append(result.get('snippet', 'No details'))
    return updates[:3] or ["No recent updates found"]

# ====================
# ⚙️ Graph Construction
# ====================

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("find_resources", find_company_resources)
workflow.add_node("scrape_website", scrape_website)
workflow.add_node("analyze_youtube", analyze_youtube_videos)
workflow.add_node("get_linkedin", get_linkedin_data)
workflow.add_node("generate_report", generate_report)

# Set entry point
workflow.set_entry_point("find_resources")

# Add edges
workflow.add_edge("find_resources", "scrape_website")
workflow.add_edge("scrape_website", "analyze_youtube")
workflow.add_edge("analyze_youtube", "get_linkedin")
workflow.add_edge("get_linkedin", "generate_report")
workflow.add_edge("generate_report", END)

# Compile the agent
agent = workflow.compile()

# ====================
# 🚀 Execution Function
# ====================

async def analyze_company(query: str):
    """Full analysis from user query"""
    results = await agent.ainvoke({"query": query})
    return results["report"]

# Example usage
async def main():
    report = await analyze_company("eSparkbiz ")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())