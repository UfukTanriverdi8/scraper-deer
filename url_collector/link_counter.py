import os
import json

folder = "crawled_links"
total_html = 0
total_document = 0

for filename in os.listdir(folder):
    if filename.endswith(".json"):
        filepath = os.path.join(folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        html_links = data.get("html", [])
        document_links = data.get("document", [])
        total_html += len(html_links)
        total_document += len(document_links)
        print(f"{filename}: {len(html_links)} HTML links, {len(document_links)} Document links")
        print(f"Set vs original: {len(set(html_links))}, {len(html_links)} and {len(set(document_links))}, {len(document_links)}")

print("=" * 50)
print(f"Total HTML links: {total_html}")
print(f"Total Document links: {total_document}")
