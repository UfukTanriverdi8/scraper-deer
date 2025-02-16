import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from collections import defaultdict
from urllib.parse import urlparse, urlunparse
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

DOMAIN = "bilsis"

browser_config = BrowserConfig(headless=True, verbose=True)
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    word_count_threshold=30,        # filter out pages with very little content
    exclude_external_links=True,    # already filtering domains manually
)

def get_https_version(url):
    parsed = urlparse(url)
    return urlunparse(('https', parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

def normalize_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    # Reconstruct the URL without the fragment and trailing slash in the path
    return urlunparse((parsed.scheme, netloc, parsed.path.rstrip('/'), '', '', ''))


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

def is_html_or_pdf(url):
    parsed = urlparse(url)
    path = parsed.path
    # Allow URLs ending with '/' or with no extension as HTML
    if path.endswith('/') or '.' not in path.split('/')[-1]:
        return True
    # Allow explicit .html pages
    return any(path.lower().endswith(ext) for ext in [".html", ".pdf"])

def is_pdf(url):
    return url.lower().endswith(".pdf")

def is_excluded(url):
    for pattern in exclude_patterns:
        if re.match(pattern, url):
            print(f"Skipping: {url}")
            return True
    return False

async def get_links():
    start_urls = [f"https://{DOMAIN}.hacettepe.edu.tr/oibs/bologna/index.aspx"]
    visited_pages = set()       # URLs that have been crawled
    collected_urls = set()      # URLs that have been collected (to avoid duplicates)
    urls_to_crawl = start_urls.copy()
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
        while urls_to_crawl and (len(html_links) + len(pdf_links)) < 100:
            current_url = urls_to_crawl.pop(0)
            if current_url in visited_pages:
                continue

            result = await crawler.arun(current_url, config=run_config)
            visited_pages.add(current_url)

            if not result.success:
                print(f"Error crawling {current_url}: {result.error_message}")
                continue

            """ if "was not found on this server." in result.cleaned_html.lower():
                print(f"Skipping Not Found page: {current_url}")
                continue """
            print(result.links)
            # Extract internal links
            for link in result.links.get("internal", []):
                url = link.get("href")
                #url = normalize_url(url)
                if not (url and start_urls[0] in url):
                    continue
                if url in visited_pages or url in collected_urls:
                    continue
                if is_excluded(url) or not is_html_or_pdf(url):
                    continue

                # If URL is http and https version exists, skip it.
                parsed = urlparse(url)
                if parsed.scheme == "http":
                    https_version = get_https_version(url)
                    if https_version in collected_urls:
                        continue

                urls_to_crawl.append(url)
                collected_urls.add(url)
                # Separate based on file type
                if is_pdf(url):
                    pdf_links.append(url)
                else:
                    html_links.append(url)

    # Save as a JSON object with "html" and "pdf" keys
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
