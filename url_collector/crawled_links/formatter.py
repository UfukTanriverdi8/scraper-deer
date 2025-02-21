import json

def merge_json_files(file1, file2, output_file):
    # Load the first file
    with open(file1, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    # Load the second file
    with open(file2, 'r', encoding='utf-8') as f:
        data2 = json.load(f)

    # Merge each key's list (removing duplicates)
    merged = {
        "html": list(set(data1.get("html", [])) | set(data2.get("html", []))),
        "document": list(set(data1.get("document", [])) | set(data2.get("document", [])))
    }

    # Write the merged data to the output file without escaping non-ASCII characters
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    print(f"Merged file saved as {output_file}")

# Example usage:
merge_json_files('cs.hacettepe.edu.tr__crawled_links.json', 'cs.hacettepe.edu.tr_index.html#curriculum_ai_crawled_links.json', 'merged_cs.json')
