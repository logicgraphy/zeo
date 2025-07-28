
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from openai import OpenAI
import os

# Initialize LLAMA client with the correct environment variable and base URL
client = OpenAI(
    api_key=os.environ.get("LLAMA_API_KEY"), 
    base_url="https://api.llama.com/compat/v1/"
)

def get_all_links(base_url):
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and isinstance(href, str):
                full_url = urljoin(base_url, href)
                links.append(full_url)

        # Deduplicate and prioritize based on URL patterns
        unique_links = list(set(links))

        def priority_score(url):
            url_lower = url.lower()
            if any(kw in url_lower for kw in ['faq', 'questions']):
                return 100
            elif any(kw in url_lower for kw in ['blog', 'article', 'guide', 'resource']):
                return 80
            elif any(kw in url_lower for kw in ['product', 'service', 'solutions']):
                return 70
            elif any(kw in url_lower for kw in ['about', 'team', 'company']):
                return 60
            elif any(kw in url_lower for kw in ['contact', 'location']):
                return 40
            else:
                return 10  # default low priority

        sorted_links = sorted(unique_links, key=priority_score, reverse=True)
        return sorted_links
    except Exception as e:
        print(f"Error fetching links: {e}")
        return []

def extract_structured_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'headings': [h.get_text(strip=True) for h in soup.find_all(re.compile('^h[1-6]$'))],
            'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')],
            'lists': [li.get_text(strip=True) for li in soup.find_all('li')]
        }
        return content
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return {}


# LLM analysis function
def analyze_content_with_llm(content):
    try:
        prompt = f"""
Evaluate the following webpage content for the following:
1. Clarity and completeness of information.
2. Relevance to likely user intent.
3. Citation-worthiness for AI-generated answers.

Provide a score from 1 to 5 for each category, and a short explanation.
Also provide specific recommendations to improve the content for better AEO (Answer Engine Optimization) and GEO (Generative Engine Optimization).

Content:
Title: {content['title']}
Headings: {content['headings']}
Paragraphs: {content['paragraphs'][:3]}
Lists: {content['lists'][:3]}
"""
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error analyzing content: {e}")
        return "Analysis failed"

def score_aeo_geo_features(content):
    scores = {
        "faq_formatting": 0,
        "structured_data": 0,
        "author_metadata": 0,
        "semantic_markup": 0,
        "total_score": 0
    }

    # Check for potential FAQ formatting
    faq_keywords = ['faq', 'frequently asked', 'question']
    if any(faq_kw in h.lower() for h in content['headings'] for faq_kw in faq_keywords):
        scores["faq_formatting"] = 1

    # Check for semantic markup using headings, lists, etc.
    if content['headings']:
        scores["semantic_markup"] += 1
    if content['lists']:
        scores["semantic_markup"] += 1

    # Check for basic author/date metadata in paragraphs or page title
    if any("author" in p.lower() or "published" in p.lower() for p in content['paragraphs']):
        scores["author_metadata"] = 1

    # Check for structured data indicators in raw HTML (basic heuristic)
    if any('schema.org' in p.lower() or 'json-ld' in p.lower() for p in content['paragraphs']):
        scores["structured_data"] = 1

    scores["total_score"] = sum(scores.values())
    return scores

if __name__ == "__main__":
    start_url = "https://www.apple.com"  # Replace with target site
    all_links = get_all_links(start_url)
    for link in all_links[:5]:  # Limit to first 5 for testing
        content = extract_structured_content(link)
        # print(content)
        analysis = analyze_content_with_llm(content)
        print("AEO/GEO Analysis:")
        print(analysis)
        structure_scores = score_aeo_geo_features(content)
        print("Structural AEO/GEO Scores:")
        print(structure_scores)