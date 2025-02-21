import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from collections import defaultdict
from urllib.parse import urlparse, urlunparse
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

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

def get_https_version(url):
    parsed = urlparse(url)
    return urlunparse(('https', parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

final_domains = set()
async def test(start_url="https://www.hacettepe.edu.tr/hakkinda/siteharitasi", site="sitemap"):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(start_url)
        print(result.links)
        links = result.links["internal"]
        """ for link in links:
            url = link.get("href")
            url = normalize_url(url)
            parsed = urlparse(url)
            if parsed.scheme == "http":
                https_version = get_https_version(url)
                url = https_version
            rest_of_url = url[8:]
            domain = rest_of_url.split(".")[0]
            if domain == "bilsis" or domain == "akts":
                if site == "lisans" and domain == "bilsis" and "https://bilsis.hacettepe.edu.tr/oibs/bologna/index.aspx" in url:
                    final_domains.add(url)
                elif site == "lisansustu" and domain == "akts":
                    final_domains.add(url)
                else:
                    continue
            final_domains.add(domain) """


    

""" asyncio.run(test())
asyncio.run(test(start_url="https://www.hacettepe.edu.tr/ogretim/lisansonlisans_ogretim", site="lisans"))
asyncio.run(test(start_url="https://www.hacettepe.edu.tr/ogretim/lisansustu_ogretim", site="lisansustu")) """
asyncio.run(test(start_url="https://cs.hacettepe.edu.tr", site="lisansustu"))

for dom in final_domains:
    print(dom)