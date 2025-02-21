import os
import json

def merge_html_links(crawled_folder, extra_files, output_file):
    all_html_links = set()

    # Merge html links from all JSON files in the crawled_links folder.
    for filename in os.listdir(crawled_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(crawled_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Expecting a dictionary with a key "html"
                links = data.get("html", [])
                all_html_links.update(links)

    # Merge in extra link files.
    for extra_file in extra_files:
        if extra_file.endswith(".json"):
            with open(extra_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # If the JSON is a dict with "html" key, or a list directly
                if isinstance(data, dict):
                    links = data.get("html", [])
                elif isinstance(data, list):
                    links = data
                else:
                    links = []
                all_html_links.update(links)
        else:
            # For plain text files (one URL per line)
            with open(extra_file, 'r', encoding='utf-8') as f:
                for line in f:
                    link = line.strip()
                    if link:
                        all_html_links.add(link)

    # Save the merged html links to the output file.
    merged_links = list(all_html_links)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_links, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(merged_links)} html links into {output_file}")

if __name__ == "__main__":
    # Folder containing your crawled_links JSON files.
    crawled_folder = "../url_collector/crawled_links"
    # List your extra link files here (adjust filenames as needed).
    extra_files = ["../url_files/akts_links.json", "../url_files/bilsis_links.json","../url_files/extra_urls.json"]
    # Name for the final merged output.
    output_file = "final_html_links.json"
    
    merge_html_links(crawled_folder, extra_files, output_file)
