import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import re

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
]

def is_html_or_pdf(url):
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith('/') or '.' not in path.split('/')[-1]:
        return True
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

en_degree_links = []
en_bilsis_links = []
en_akts_links = []
degree_links = []
bilsis_links = []
akts_links = []
def get_degree_links(url , lang="tr"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Loop through each clickable heading (each degree)
    for heading in soup.find_all("span", class_="clickable-heading"):
        # The next sibling div contains the details
        details_div = heading.find_next_sibling("div")
        if details_div:
            # Extract all <a> tags within this div
            for a in details_div.find_all("a", href=True):
                link = a["href"]
                #link = normalize_url(link)
                if is_excluded(link):
                    print(f"Link: {link} is excluded!")
                    continue
                if lang == "tr":
                    if "akts.hacettepe.edu.tr" in link:
                        akts_links.append(link)
                    elif "bilsis.hacettepe.edu.tr" in link:
                        bilsis_links.append(link)
                    else:
                        degree_links.append(link)
                elif lang == "en":
                    if "akts.hacettepe.edu.tr" in link:
                        en_akts_links.append(link)
                    elif "bilsis.hacettepe.edu.tr" in link:
                        en_bilsis_links.append(link)
                    else:
                        if not link.endswith("en"):
                            if link.endswith(".tr"):
                                en_degree_links.append(link + "/en")
                                continue
                                en_response = requests.get(link + "/en")
                                if en_response.ok:
                                    en_degree_links.append(link + "/en")
                                else:
                                    print(f"Link {link + "/en"} didn't work trying the /english")
                                    en_response_2 = requests.get(link + "/english")
                                    if en_response_2.ok:
                                        en_degree_links.append(link + "/english")
                                    else:
                                        print(f"Link {link + "/english"} still didn't work just appending: {link}")
                                        en_degree_links.append(link)
                            elif link.endswith(".tr/"):
                                en_degree_links.append(link + "en")
                                continue
                                en_response = requests.get(link + "en")
                                if en_response.ok:
                                    en_degree_links.append(link + "en")
                                else:
                                    print(f"Link {link + "en"} didn't work trying the /english")
                                    en_response_2 = requests.get(link + "english")
                                    if en_response_2.ok:
                                        en_degree_links.append(link + "english")
                                    else:
                                        print(f"Link {link + "/english"} still didn't work just appending: {link}")
                                        en_degree_links.append(link)

                        else:
                            en_degree_links.append(link)
                        
                        #en_degree_links.append(link)


get_degree_links("https://www.hacettepe.edu.tr/ogretim/lisansonlisans_ogretim")
get_degree_links("https://www.hacettepe.edu.tr/ogretim/lisansustu_ogretim")
get_degree_links("https://www.hacettepe.edu.tr/teaching/undergraduate_programs", lang="en")
get_degree_links("https://www.hacettepe.edu.tr/teaching/graduate_programs", lang="en")
unique_degrees = list(dict.fromkeys(degree_links))
en_unique_degrees = list(dict.fromkeys(en_degree_links))
unique_bilsis = list(dict.fromkeys(bilsis_links + en_bilsis_links))
unique_akts = list(dict.fromkeys(akts_links + en_akts_links))

for link in unique_degrees[:10]:
    print(link)
print("="*10)
for link in en_unique_degrees[:10]:
    print(link)
#print(f"tr bilsis check: list len {len(bilsis_links)}, set len {len(set(bilsis_links))} ")
for link in bilsis_links[:5]:
    print(link)


import json

# Save TR start URLs (unique_degrees)
with open("start_urls_tr.json", "w", encoding="utf-8") as f:
    json.dump(unique_degrees, f, indent=2)

# Save EN start URLs (en_unique_degrees)
with open("start_urls_en.json", "w", encoding="utf-8") as f:
    json.dump(en_unique_degrees, f, indent=2)

# Combine bilsis and akts links (for both languages)
bilsis = list(dict.fromkeys(unique_bilsis))
with open("bilsis_links.json", "w", encoding="utf-8") as f:
    json.dump(bilsis, f, indent=2)

akts = list(dict.fromkeys(unique_akts))
with open("akts_links.json", "w", encoding="utf-8") as f:
    json.dump(akts, f, indent=2)

print("Files saved successfully!")