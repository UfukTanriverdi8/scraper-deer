import os
import json
import math

# Configuration
input_file = '../batch_scraper/final_output.json'  # Your full JSON file with all entries
output_folder = 'md_output'
num_parts = 12  # Number of parts to split into

# Ensure output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load the full list of entries
with open(input_file, 'r', encoding='utf-8') as f:
    entries = json.load(f)

total_entries = len(entries)
split_size = math.ceil(total_entries / num_parts)

print(f"Total entries: {total_entries}, split size: {split_size}")

for i in range(num_parts):
    # Determine the entries for this part
    part_entries = entries[i * split_size : (i + 1) * split_size]
    
    # Build the markdown content. Here we add a header with the URL and then the markdown.
    md_content = ""
    for entry in part_entries:
        md_content += f"## {entry['url']}\n\n{entry['markdown']}\n\n---\n\n"
    
    # Write the markdown file
    md_filename = f"hacettepe_data_{i+1}.md"
    md_filepath = os.path.join(output_folder, md_filename)
    with open(md_filepath, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)
    
    # Create the metadata JSON file content
    metadata = {
        "metadataAttributes": {
            "college_name": "hacettepe"
        }
    }
    
    metadata_filename = f"{md_filename}.metadata.json"
    metadata_filepath = os.path.join(output_folder, metadata_filename)
    with open(metadata_filepath, 'w', encoding='utf-8') as meta_file:
        json.dump(metadata, meta_file, indent=2, ensure_ascii=False)
    
    print(f"Saved {md_filepath} and {metadata_filepath}")
