import asyncio
import json
import re
from collections import deque
from urllib.parse import urlparse, urlunparse
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

import json

with open("../url_files/start_urls_tr.json", "r", encoding="utf-8") as f:
    START_URLS = json.load(f)


""" START_URLS = [
    "https://sksdb.hacettepe.edu.tr/bidbnew/index.php",
]  """


BATCH_SIZE = 8    # Number of concurrent crawls per batch
MAX_DEPTH = 5     # Limit recursion depth

browser_config = BrowserConfig(headless=True, verbose=True)
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    word_count_threshold=10,
    remove_overlay_elements=True,
    check_robots_txt=True,
    user_agent_mode="random",
)

def normalize_url(url):
    """Force URL to HTTPS and remove 'www.' prefix unless the domain is ee.hacettepe.edu.tr."""
    parsed = urlparse(url)
    scheme = "https"
    netloc = parsed.netloc
    # Only remove "www." if the domain is NOT ee.hacettepe.edu.tr
    if not netloc.endswith("ee.hacettepe.edu.tr") and netloc.startswith("www."):
        netloc = netloc[4:]
    # Keep "/" as is; otherwise remove trailing slash for consistency
    #path = parsed.path if parsed.path == "/" else parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

def is_html_or_pdf(url):
    parsed = urlparse(url)
    path = parsed.path
    # Consider as HTML if no file extension or ending with '/' 
    if path.endswith("/") or '.' not in path.split("/")[-1]:
        return True
    # Allow .html, .pdf, and .php pages
    return path.lower().endswith((".html", ".pdf", ".php", ".doc", ".docx", ".xls", ".xlsx", ".htm"))


def is_excluded(url):
    exclude_patterns = [
        r'https?://(www\.)?radyo\.hacettepe\.edu\.tr.*',
        r'https?://(www\.)?library\.hacettepe\.edu\.tr(/.*)?',
        r'https?://(www\.)?openaccess\.hacettepe\.edu\.tr.*',
        r'https?://(www\.)?hastane\.hacettepe\.edu\.tr.*',
        r'https://librarycalendar.hacettepe.edu.tr/',
        r'https://libraryworkflows.hacettepe.edu.tr/',
        r'efdergi.hacettepe.edu.tr',
        r'katalog.hacettepe.edu.tr',
        r'https://hadi.hacettepe.edu.tr/',
        r'https://beb.hacettepe.edu.tr/',
        r'https://gazete.hacettepe.edu.tr/tr/paylas',
        r'https://gazete.hacettepe.edu.tr/en/paylas/',
        r'http://www.eob.hacettepe.edu.tr/',
        r'https://avesis.hacettepe.edu.tr/',
        r'https://orhondan21yuzyila.hacettepe.edu.tr/',
        r'https://webyeni2.hacettepe.edu.tr/',
        r'https://bilsis.hacettepe.edu.tr/oibs/std/login.aspx',
        r'https?://yunus.hacettepe.edu.tr/',
        r'https://haberler.hacettepe.edu.tr/',
        r'https?://syk.hacettepe.edu.tr',
        r'https://www.mevlana.hacettepe.edu.tr',
        r'https://www.farabi.hacettepe.edu.tr',
        r'https://www.huzem.hacettepe.edu.tr',
        r'https://www.hacettepe.edu.tr',
    ]
    return any(re.match(pattern, url) for pattern in exclude_patterns)

async def get_links(start_url):
    visited_pages = set()
    collected_urls = set()
    # Normalize the start URL and use it as the base
    start_url_norm = normalize_url(start_url)
    urls_to_crawl = deque([(start_url_norm, 0)])  # (URL, depth)
    html_links, document_links = [], []

    # Determine the base domain for subdomain checking
    start_domain = urlparse(start_url_norm).netloc

    async with AsyncWebCrawler(config=browser_config) as crawler:
        while urls_to_crawl:
            current_url, depth = urls_to_crawl.popleft()
            if depth >= MAX_DEPTH or current_url in visited_pages:
                continue

            result = await crawler.arun(current_url, config=run_config)
            if not result.success:
                print(f"Error crawling {current_url}: {result.error_message}")
                continue
            if ("the requested url" in result.markdown.lower() and 
                "was not found on this server." in result.markdown.lower()):
                print(f"Skipping page: {current_url} - Not Found")
                continue
            
            visited_pages.add(current_url)
            for link in result.links.get("internal", []):
                raw_url = link.get("href")
                if not raw_url:
                    continue
                url = normalize_url(raw_url)
                # Check domain: allow if URL's domain equals start_domain or is a subdomain of it.
                link_domain = urlparse(url).netloc
                if not (link_domain == start_domain or link_domain.endswith("." + start_domain)):
                    #print(f"Skipping external link: {url}")
                    continue
                if url in visited_pages or url in collected_urls:
                    #print(f"Skipping duplicate link: {url}")
                    continue
                if is_excluded(url) or not is_html_or_pdf(url):
                    #print(f"Skipping excluded link: {url}")
                    continue

                
                
                if url.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
                    document_links.append(url)
                    collected_urls.add(url)
                else:
                    html_links.append(url)
                    urls_to_crawl.append((url, depth + 1))
                    collected_urls.add(url)

    # Save results for this start_url
    file_name = f"crawled_links/{start_url_norm.replace('https://', '').replace('/', '_')}_crawled_links.json"
    if not start_url_norm in html_links:
        html_links.append(start_url_norm)
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump({"html": html_links, "document": document_links}, file, indent=2, ensure_ascii=False)
    print("="*50)
    print(f"Saved results for {start_url_norm} to {file_name}.")
    print(f"Collected {len(html_links)} HTML links and {len(document_links)} Document links from {start_url_norm}.")

async def run_in_batches():
    # Process START_URLS in batches
    for i in range(0, len(START_URLS), BATCH_SIZE):
        batch = START_URLS[i:i + BATCH_SIZE]
        await asyncio.gather(*(get_links(url) for url in batch))
        print("="*50)
        print(f"Batch {i // BATCH_SIZE + 1} completed.")
        await asyncio.sleep(2)  # Pause between batches

if __name__ == "__main__":
    asyncio.run(run_in_batches())
