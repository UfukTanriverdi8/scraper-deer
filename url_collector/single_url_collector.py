import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from collections import defaultdict, deque
from urllib.parse import urlparse, urlunparse
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

DOMAIN = "cs"

# Precompile regex patterns for performance
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
compiled_exclude_patterns = [re.compile(p) for p in exclude_patterns]

def is_html_or_pdf(url):
    parsed = urlparse(url)
    path = parsed.path
    # Allow URLs ending with '/' or with no extension as HTML
    if path.endswith('/') or '.' not in path.split('/')[-1]:
        return True
    return any(path.lower().endswith(ext) for ext in [".html", ".pdf"])

def is_pdf(url):
    return url.lower().endswith(".pdf")

def is_excluded(url):
    for pattern in compiled_exclude_patterns:
        if pattern.match(url):
            print(f"Skipping: {url}")
            return True
    return False

def remove_www_and_upgrade(url):
    parsed = urlparse(url)
    netloc = parsed.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    # Force scheme to https
    return urlunparse(("https", netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


async def get_links():
    start_url = f"https://{DOMAIN}.hacettepe.edu.tr/"
    start_url = remove_www_and_upgrade(start_url) 
    start_urls = [start_url]

    start_domain = urlparse(start_url).netloc  # Reliable domain for filtering
    print(start_domain)

    visited_pages = set()    # URLs that have been crawled
    collected_urls = set()   # To avoid duplicates
    urls_to_crawl = deque(start_urls)  # Use deque for efficient pops from the front
    
    html_links = []
    pdf_links = []

    # Using fresh configs
    browser_config = BrowserConfig(headless=True, verbose=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=10,
        remove_overlay_elements=True,
        check_robots_txt=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        while urls_to_crawl and len(collected_urls) < 300:
            current_url = urls_to_crawl.popleft()
            if current_url in visited_pages:
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
                url = link.get("href")
                if not url:
                    continue
                url = remove_www_and_upgrade(url)
                # Use reliable domain check
                link_domain = urlparse(url).netloc
                if start_domain not in link_domain:
                    continue

                if url in visited_pages or url in collected_urls:
                    continue

                if is_excluded(url) or not is_html_or_pdf(url):
                    continue

                urls_to_crawl.append(url)
                collected_urls.add(url)

                if is_pdf(url):
                    pdf_links.append(url)
                else:
                    html_links.append(url)

    output = {
        "html": html_links,
        "pdf": pdf_links
    }
    with open(f"{DOMAIN}_crawled_links.json", "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)
    print(f"Collected {len(html_links)} html links and {len(pdf_links)} pdf links and saved them to '{DOMAIN}_crawled_links.json'.")
    find_duplicates(html_links + pdf_links)

def find_duplicates(urls):
    url_count = defaultdict(int)
    for url in urls:
        url_count[url] += 1

    duplicates = {url: count for url, count in url_count.items() if count > 1}
    if duplicates:
        print("Found duplicates:")
        for url, count in duplicates.items():
            print(f"{url} - {count} times")
    else:
        print("No duplicates found.")
    return duplicates

asyncio.run(get_links())
