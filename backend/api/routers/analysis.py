from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime, timedelta
import os
from urllib.parse import urljoin, urlparse

# Import necessary libraries for web scraping and analysis
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import json
from typing import Any, Dict, Tuple, List
from openai import OpenAI

load_dotenv(override=True)

# Initialize LLM client
try:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )
except Exception:
    client = None

LLM_MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-5-nano")

from ..models import (
    QuickAnalyzeRequest, ReportRequest, AnalysisResponse,
    ReportStatus, AEOReport,
    MessageResponse, EmailVerification,
    QuickAnalyzeResponse, CategoryScore
)
from ..utils import generate_verification_code, send_verification_email
from ..database import DatabaseService
# from .auth import verify_email  # not used by frontend flows

router = APIRouter(tags=["analysis"])


def normalize_url(input_url: str) -> str:
    if not input_url:
        return input_url
    url = input_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def crawl_website(start_url: str, max_pages: int = 10) -> list[str]:
    """Crawl a website to find unique, same-domain URLs."""
    try:
        parsed_start_url = urlparse(start_url)
        domain = parsed_start_url.netloc
        
        urls_to_visit = [start_url]
        visited_urls = set()
        found_urls = []

        while urls_to_visit and len(found_urls) < max_pages:
            url = urls_to_visit.pop(0)
            if url in visited_urls:
                continue
            
            visited_urls.add(url)
            
            try:
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/91.0.4472.124 Safari/537.36"
                    )
                }
                response = requests.get(url, timeout=5, headers=headers)
                response.raise_for_status()
                
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    continue

                found_urls.append(url)
                
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    if not isinstance(link, Tag):
                        continue
                    href_val = link.get('href')
                    if not href_val or not isinstance(href_val, str):
                        continue
                    full_url = urljoin(url, href_val)
                    parsed_full_url = urlparse(full_url)
                    
                    if (
                        parsed_full_url.netloc == domain and
                        parsed_full_url.scheme in ['http', 'https'] and
                        full_url not in visited_urls and
                        full_url not in urls_to_visit
                    ):
                        urls_to_visit.append(full_url)
            except requests.RequestException as e:
                print(f"Could not crawl {url}: {e}")
                
        return found_urls
    except Exception as e:
        print(f"Crawler failed for {start_url}: {e}")
        return [start_url]


def extract_structured_content(url: str) -> dict:
    """Extract structured content from a webpage.

    Captures:
    - title, headings, paragraphs, lists
    - meta name/property -> content
    - jsonld_types: list of JSON-LD @type strings (e.g., FAQPage, HowTo, Article)
    - links_text: list of anchor texts (lowercased) to detect supporting pages
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, timeout=12, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        headings = [h.get_text(strip=True) for h in soup.find_all(re.compile("^h[1-6]$"))]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        lists = [li.get_text(strip=True) for li in soup.find_all("li")]
        meta_tags = {
            (m.get("name") or m.get("property")): m.get("content")
            for m in soup.find_all("meta")
            if isinstance(m, Tag) and m.get("content") and (m.get("name") or m.get("property"))
        }

        # Extract JSON-LD @type values
        jsonld_types: List[str] = []
        try:
            for s in soup.find_all("script", type="application/ld+json"):
                if not isinstance(s, Tag):
                    continue
                raw_json = s.get_text(strip=True) if s else None
                if not raw_json:
                    continue
                try:
                    data = json.loads(raw_json)
                except Exception:
                    continue

                def collect_types(node: Any):
                    if isinstance(node, dict):
                        node_type = node.get("@type")
                        if isinstance(node_type, str):
                            jsonld_types.append(node_type)
                        elif isinstance(node_type, list):
                            for t in node_type:
                                if isinstance(t, str):
                                    jsonld_types.append(t)
                        # @graph may contain multiple nodes
                        if "@graph" in node and isinstance(node["@graph"], list):
                            for child in node["@graph"]:
                                collect_types(child)
                    elif isinstance(node, list):
                        for item in node:
                            collect_types(item)

                collect_types(data)
        except Exception:
            pass

        # Extract anchor texts for simple supporting page detection
        links_text: List[str] = []
        try:
            for a in soup.find_all("a", href=True):
                if not isinstance(a, Tag):
                    continue
                txt = a.get_text(strip=True)
                if txt:
                    links_text.append(txt.lower())
        except Exception:
            pass

        # Truncate to keep prompts small
        return {
            "url": url,
            "title": soup.title.string[:180] if soup.title and soup.title.string else "",
            "headings": headings[:12],
            "paragraphs": paragraphs[:8],
            "lists": lists[:12],
            "meta": {k: meta_tags[k] for k in list(meta_tags.keys())[:12] if k},
            "jsonld_types": list(dict.fromkeys(jsonld_types))[:12],
            "links_text": links_text[:30],
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return {}


def summarize_reports(summaries: list[str], url: str) -> str:
    """Use LLM to create a high-level summary from individual page summaries."""
    if not client or not summaries:
        return "Could not generate aggregate summary. Analysis may be incomplete."
        
    prompt = (
        "You are an AEO (Answer Engine Optimization) analyst. "
        f"You have analyzed several pages from the website {url}. "
        "Below are the summaries for each page. "
        "Create a single, cohesive summary of the entire site's AEO performance. "
        "Identify common themes, strengths, and weaknesses.\n\n"
        #"Conclude with the top 3-5 most impactful, site-wide recommendations.\n\n"
        "Page Summaries:\n" + "\n\n".join(summaries)
    )
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content or "Summary generation failed."
    except Exception as e:
        print(f"Error summarizing reports: {e}")
        return "Failed to generate an aggregate summary."


def build_aeo_prompt(content: dict) -> str:
    return (
        "You are an AEO (Answer Engine Optimization) auditor. "
        "Given the following webpage content, return a strict JSON object with this shape: "
        "{\n  \"scores\": {\n    \"content_quality\": { \"score\": 1-5, \"reason\": string },\n    \"structure_optimization\": { \"score\": 1-5, \"reason\": string },\n    \"authority_trust\": { \"score\": 1-5, \"reason\": string }\n  }\n}\n"
        "Rules: "
        "- Use integers 1-5 only for scores."
        "- Keep reasons under 140 characters each."
        "- Return only JSON without backticks or extra text."
        f"\n\nTitle: {content.get('title','')}\n"
        f"Headings: {content.get('headings', [])}\n"
        f"Paragraphs: {content.get('paragraphs', [])}\n"
        f"Lists: {content.get('lists', [])}\n"
        f"Meta: {content.get('meta', {})}\n"
    )


def parse_llm_json(text: str) -> Dict[str, Any] | None:
    try:
        return json.loads(text)
    except Exception:
        # Try to extract JSON blob
        try:
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                return json.loads(match.group(0))
        except Exception:
            return None
    return None


def analyze_content_with_llm(content: dict) -> Tuple[Dict[str, Any] | None, str]:
    """Analyze content using LLM for AEO scoring. Returns (parsed_json, raw_text)."""
    if not client:
        return None, "LLM analysis unavailable - API client not configured"
    try:
        prompt = build_aeo_prompt(content)
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content or ""
        parsed = parse_llm_json(raw) if raw else None
        return parsed, raw
    except Exception as e:
        print(f"Error analyzing content with LLM: {e}")
        return None, ""


def score_aeo_features(content: dict) -> dict:
    """Heuristic structural AEO features."""
    scores = {
        "faq_formatting": 0,
        "qa_text": 0,
        "structured_data": 0,
        "jsonld_schema": 0,
        "author_metadata": 0,
        "semantic_markup": 0,
        "supporting_pages_linked": 0,
        "meta_quality": 0,
        "total_score": 0,
    }

    headings = content.get("headings", [])
    paragraphs = content.get("paragraphs", [])
    meta = content.get("meta", {})

    faq_keywords = ["faq", "frequently asked", "question"]
    if any(any(kw in h.lower() for kw in faq_keywords) for h in headings):
        scores["faq_formatting"] = 1

    # Detect Q&A-like text patterns in paragraphs
    qa_patterns = [r"^\s*what\b", r"^\s*how\b", r"^\s*why\b", r"\?\s*$"]
    for p in paragraphs:
        low = p.lower()
        if any(re.search(pat, low) for pat in qa_patterns):
            scores["qa_text"] = 1
            break

    if headings:
        scores["semantic_markup"] += 1
    if content.get("lists"):
        scores["semantic_markup"] += 1

    if any("author" in p.lower() or "published" in p.lower() for p in paragraphs) or any(
        k and "author" in k.lower() for k in meta.keys()
    ):
        scores["author_metadata"] = 1

    if any("schema.org" in p.lower() or "json-ld" in p.lower() for p in paragraphs) or any(
        k and ("og:" in k.lower() or "twitter:" in k.lower()) for k in meta.keys()
    ):
        scores["structured_data"] = 1

    # JSON-LD specific schema types
    jsonld_types = content.get("jsonld_types", []) or []
    if any(t in {"FAQPage", "HowTo", "Article"} for t in jsonld_types if isinstance(t, str)):
        scores["jsonld_schema"] = 1

    # Meta title/description presence and length sanity
    title = content.get("title") or ""
    description = None
    # Prefer meta description
    for k, v in meta.items():
        if not k:
            continue
        if k.lower() == "description":
            description = v
            break
    if title and 20 <= len(title) <= 180:
        scores["meta_quality"] += 1
    if description and 50 <= len(description) <= 320:
        scores["meta_quality"] += 1

    # Supporting pages linked (simple anchor text heuristic)
    links_text = content.get("links_text", []) or []
    support_keywords = ["faq", "blog", "help", "support", "guide", "knowledge", "docs", "documentation"]
    if any(any(kw in (txt or "") for kw in support_keywords) for txt in links_text):
        scores["supporting_pages_linked"] = 1

    scores["total_score"] = sum(scores.values())
    return scores


def calculate_score_from_signals(
    llm_json: Dict[str, Any] | None,
    structural_score: int,
    max_structural: int = 4,
) -> int:
    try:
        # Derive an LLM numeric in [0,1] from category scores
        if llm_json and "scores" in llm_json:
            s = llm_json["scores"]
            values = [s.get(k, {}).get("score") for k in ["content_quality", "structure_optimization", "authority_trust"]]
            values = [v for v in values if isinstance(v, int) and 1 <= v <= 5]
            llm_normalized = (sum(values) / (len(values) * 5)) if values else 0.5
        else:
            llm_normalized = 0.5

        structural_normalized = structural_score / max_structural
        combined_score = (llm_normalized * 0.65) + (structural_normalized * 0.35)
        numeric_score = max(60, int(round(combined_score * 100)))
        return numeric_score
    except Exception as e:
        print(f"Error calculating grade: {e}")
        return 75


def create_summary_from_analysis(url: str, llm_json: Dict[str, Any] | None, structural_scores: dict) -> str:
    """Create human-readable summary from structured and heuristic results."""
    try:
        summary_parts = [
            f"Analyzed page: {url}.",
            f"Structural AEO features score: {structural_scores.get('total_score', 0)}/4.",
        ]

        if llm_json and "scores" in llm_json:
            s = llm_json["scores"]
            def reason_for(key: str) -> str:
                data = s.get(key, {})
                return f"{data.get('score', '?')}/5 - {data.get('reason', '')}".strip()

            summary_parts.append(
                "AEO review: "
                f"Content Quality: {reason_for('content_quality')}; "
                f"Structure: {reason_for('structure_optimization')}; "
                f"Authority: {reason_for('authority_trust')}"
            )

        return " ".join(summary_parts)
    except Exception:
        return f"AEO analysis completed for {url}."


async def perform_full_site_analysis(analysis_id: str, start_url: str):
    try:
        DatabaseService.update_analysis(analysis_id, {"status": "crawling"})
        urls = crawl_website(start_url, max_pages=5)
        
        DatabaseService.update_analysis(analysis_id, {"status": "analyzing", "urls_found": len(urls)})
        page_results = []
        for url in urls:
            content = extract_structured_content(url)
            if not content: continue
            
            llm_json, _ = analyze_content_with_llm(content)
            structural_scores = score_aeo_features(content)
            score = calculate_score_from_signals(llm_json, structural_scores["total_score"])
            summary = create_summary_from_analysis(url, llm_json, structural_scores)
            
            page_results.append({"url": url, "score": score, "summary": summary})

        if not page_results:
            DatabaseService.update_analysis(analysis_id, {"status": "failed", "summary": "Could not analyze any pages."})
            return

        DatabaseService.update_analysis(analysis_id, {"status": "summarizing"})
        average_score = round(sum(r["score"] for r in page_results) / len(page_results))
        individual_summaries = [r["summary"] for r in page_results]
        final_summary = summarize_reports(individual_summaries, start_url)
        
        final_result = {
            "status": "completed",
            "score": average_score,
            "summary": final_summary,
            "page_results": page_results
        }
        DatabaseService.update_analysis(analysis_id, final_result)
        print(f"Completed full site analysis for {analysis_id}")
    except Exception as e:
        print(f"Full site analysis failed for {analysis_id}: {e}")
        DatabaseService.update_analysis(analysis_id, {"status": "failed", "summary": str(e)})


@router.post("/analyze/quick", response_model=QuickAnalyzeResponse)
async def quick_analyze(req: QuickAnalyzeRequest):
    """Perform quick, site-level AEO analysis with limited sub-page scanning.

    Steps covered:
    1. Normalize and fetch homepage
    2. Scan for Q&A text, structured data (including JSON-LD FAQPage/HowTo/Article), meta title/description
    3. Discover a few same-domain links and scan a small subset of sub-pages
    4. Aggregate per-page scores into a final score and summary
    """
    analysis_id = str(uuid.uuid4())

    try:
        req.url = normalize_url(req.url)
        if not req.url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")

        # Crawl a small set of pages synchronously to keep it fast
        urls = crawl_website(req.url, max_pages=5)
        if not urls:
            urls = [req.url]

        page_results: List[dict] = []
        for page_url in urls:
            content = extract_structured_content(page_url)
            if not content or not content.get("title"):
                continue

            llm_json, _ = analyze_content_with_llm(content)
            structural_scores = score_aeo_features(content)
            score = calculate_score_from_signals(llm_json, structural_scores.get("total_score", 0))
            summary = create_summary_from_analysis(page_url, llm_json, structural_scores)
            page_results.append({"url": page_url, "score": score, "summary": summary, "llm": llm_json})

        if not page_results:
            raise HTTPException(status_code=400, detail="Unable to access or parse the URL content")

        # Aggregate
        average_score = round(sum(r["score"] for r in page_results) / len(page_results))

        # Select homepage LLM scores (fallback to first)
        primary = next((r for r in page_results if r["url"] == urls[0]), page_results[0])
        llm_scores = (primary.get("llm") or {}).get("scores") or {}

        # Build structured response
        def to_category(key: str) -> CategoryScore:
            data = llm_scores.get(key) or {}
            raw_score = data.get("score")
            s: int = int(raw_score) if isinstance(raw_score, int) else 3
            reason: str = data.get("reason") or ""
            s = max(1, min(5, s))
            return CategoryScore(score=s, reason=reason)

        DatabaseService.create_analysis(analysis_id, req.url, "", average_score)

        return QuickAnalyzeResponse(
            analysis_id=analysis_id,
            overall_score=average_score,
            url=req.url,
            content_quality=to_category("content_quality"),
            structure_optimization=to_category("structure_optimization"),
            authority_trust=to_category("authority_trust"),
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in quick_analyze: {e}")
        default_reason = "Analysis error. Using default values."
        score = 00
        DatabaseService.create_analysis(analysis_id, req.url, default_reason, score)
        return QuickAnalyzeResponse(
            analysis_id=analysis_id,
            overall_score=score,
            url=req.url,
            content_quality=CategoryScore(score=0, reason=default_reason),
            structure_optimization=CategoryScore(score=0, reason=default_reason),
            authority_trust=CategoryScore(score=0, reason=default_reason),
        )


@router.post("/report/request", response_model=MessageResponse)
async def request_report(req: ReportRequest):
    """Request a detailed report for a website"""
    # If user not registered, register as unverified
    user = DatabaseService.get_user(req.email)
    if not user:
        DatabaseService.create_user(req.email, "Anonymous", False)
    
    # Generate verification code
    verification_code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=5)
    DatabaseService.set_verification_code(req.email, verification_code, expires_at)
    
    send_verification_email(req.email, verification_code)
    return MessageResponse(message="Verification code sent to email")



@router.get("/report/{analysis_id}", response_model=AEOReport)
async def get_report(analysis_id: str):
    """Run full-site analysis for the given analysis_id and return a detailed report."""
    data = DatabaseService.get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Perform full-site analysis synchronously for now
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Analysis URL missing")

    urls = crawl_website(url, max_pages=5)
    if not urls:
        urls = [url]

    page_results: List[dict] = []
    for page_url in urls:
        content = extract_structured_content(page_url)
        if not content:
            continue
        llm_json, _ = analyze_content_with_llm(content)
        structural_scores = score_aeo_features(content)
        score = calculate_score_from_signals(llm_json, structural_scores.get("total_score", 0))
        summary = create_summary_from_analysis(page_url, llm_json, structural_scores)
        page_results.append({"url": page_url, "score": score, "summary": summary})

    if not page_results:
        raise HTTPException(status_code=400, detail="Unable to generate report from the site content")

    average_score = round(sum(r["score"] for r in page_results) / len(page_results))
    final_summary = summarize_reports([r["summary"] for r in page_results], url)

    # Build RAW_REPORT string
    raw_lines = [
        f"Overall Score: {average_score}",
        f"URL: {url}",
        "\nPage Results:",
    ]
    for r in page_results:
        raw_lines.append(f"- {r['url']} — {r['score']}/100\n  {r['summary']}")
    raw_lines.append("\nAggregate Summary:\n" + final_summary)
    raw_report = "\n".join(raw_lines)

    # Format with LLM per strict JSON schema
    prompt = (
        "You are an expert AEO report formatter. Convert the following unstructured AEO report into STRICT JSON that matches the schema below. Do not include explanations, markdown, or code fences—return JSON ONLY.\n\n"
        "INPUT_REPORT:\n{{RAW_REPORT}}\n\n"
        "REQUIRED JSON SCHEMA (TypeShape):\n{\n  \"meta\": {\n    \"report_title\": \"string\",\n    \"scope\": \"string\",\n    \"analyzed_at\": \"string (ISO 8601 date)\",\n    \"overall_score\": \"number [0,100]\",\n    \"analyst\": \"string\",\n    \"tool_version\": \"string\"\n  },\n  \"executive_summary\": {\n    \"summary_paragraph\": \"string\",\n    \"highlights\": [\"string\", \"...\"]\n  },\n  \"overall_findings\": {\n    \"content_quality\": { \"score\": \"number [1,5]\", \"notes\": \"string\" },\n    \"structure\":       { \"score\": \"number [1,5]\", \"notes\": \"string\" },\n    \"authority_signals\": { \"score\": \"number [1,5]\", \"notes\": \"string\" },\n    \"impact\": \"string\",\n    \"common_themes\": [\"string\", \"...\"]\n  },\n  \"strengths\": {\n    \"brand_domain_trust\": [\"string\", \"...\"],\n    \"navigation_layout\": [\"string\", \"...\"],\n    \"technical_signals\": [\"string\", \"...\"]\n  },\n  \"weaknesses\": {\n    \"content_depth\": [\"string\", \"...\"],\n    \"authority_trust\": [\"string\", \"...\"],\n    \"semantic_accessibility\": [\"string\", \"...\"],\n    \"ux_friction\": [\"string\", \"...\"]\n  },\n  \"implications_for_aeo\": {\n    \"overview\": \"string\",\n    \"bullets\": [\"string\", \"...\"]\n  },\n  \"recommendations\": [\n    {\n      \"priority\": \"high|medium|long\",\n      \"action\": \"string\",\n      \"rationale\": \"string\",\n      \"owner\": \"content|engineering|seo|design|product|analytics\",\n      \"effort\": \"S|M|L\",\n      \"impact\": \"S|M|L\",\n      \"success_metrics\": [\"string\", \"...\"]\n    }\n  ],\n  \"quick_win_checklist\": [\n    {\n      \"action\": \"string\",\n      \"why_it_matters\": \"string\",\n      \"status\": \"todo|in_progress|done\",\n      \"target_metric\": \"string\"\n    }\n  ],\n  \"page_scores\": [\n    {\n      \"url\": \"string (absolute or hash-anchored)\",\n      \"score\": \"number [0,100]\",\n      \"key_observations\": [\"string\", \"...\"]\n    }\n  ],\n  \"bottom_line\": \"string\",\n  \"ab_testing_plan\": [\n    {\n      \"hypothesis\": \"string\",\n      \"variant_changes\": [\"string\", \"...\"],\n      \"primary_metric\": \"string\",\n      \"secondary_metrics\": [\"string\", \"...\"],\n      \"duration_weeks\": \"number\"\n    }\n  ],\n  \"kpis_to_monitor\": [\"string\", \"...\"]\n}\n\nTRANSFORMATION RULES:\n1) Populate all fields from INPUT_REPORT; if a field is missing, infer briefly (1–2 sentences) or use an empty array [] if truly not present. Never omit required top-level keys.\n2) Clamp numeric scores to schema ranges. Convert textual scores (e.g., “2/5”) to numbers.\n3) Use concise, stakeholder-friendly language. Bullet points should be short, actionable statements.\n4) Preserve page list and scores exactly when present; normalize URLs; carry forward any anchors.\n5) Keep \"recommendations\" prioritized and specific; assign likely \"owner\" and rough \"effort/impact\".\n6) Dates must be ISO 8601. If missing, set to today's date in UTC.\n7) Return VALID JSON ONLY. No comments, no trailing commas, no markdown.\n"
    ).replace("{{RAW_REPORT}}", raw_report)

    def build_fallback() -> dict:
        today_iso = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        return {
            "meta": {
                "report_title": "AEO Site Report",
                "scope": url,
                "analyzed_at": today_iso,
                "overall_score": average_score,
                "analyst": "AI",
                "tool_version": "1.0"
            },
            "executive_summary": {
                "summary_paragraph": final_summary,
                "highlights": []
            },
            "overall_findings": {
                "content_quality": {"score": 3, "notes": ""},
                "structure": {"score": 3, "notes": ""},
                "authority_signals": {"score": 3, "notes": ""},
                "impact": "",
                "common_themes": []
            },
            "strengths": {"brand_domain_trust": [], "navigation_layout": [], "technical_signals": []},
            "weaknesses": {"content_depth": [], "authority_trust": [], "semantic_accessibility": [], "ux_friction": []},
            "implications_for_aeo": {"overview": "", "bullets": []},
            "recommendations": [],
            "quick_win_checklist": [],
            "page_scores": [{"url": r["url"], "score": r["score"], "key_observations": []} for r in page_results],
            "bottom_line": final_summary,
            "ab_testing_plan": [],
            "kpis_to_monitor": []
        }

    if not client:
        return build_fallback()

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        # Validate against schema; if invalid, fallback below
        try:
            validated = AEOReport(**data)
            return json.loads(validated.model_dump_json())
        except Exception as ve:
            print(f"Validation of LLM JSON failed: {ve}")
            return build_fallback()
    except Exception as e:
        print(f"Formatting failed, returning fallback schema: {e}")
        return build_fallback()

# Steps endpoint removed from workflow
