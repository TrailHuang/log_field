#!/usr/bin/env python3
import os
import json
import csv

def extract_template_fields(directory):
    """Search all JSON files and extract template fields"""
    results = []
    all_fields = set()

    # Search all JSON files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'template' in data and isinstance(data['template'], list):
                            template_fields = data['template']
                            tpl_name = data.get('tpl_name', 'N/A')
                            relative_path = os.path.relpath(file_path, directory)
                            results.append((relative_path, tpl_name, template_fields))
                            # Add fields to set for deduplication
                            all_fields.update(template_fields)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return results, sorted(all_fields)

def generate_csv(results, output_file):
    """Generate CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Path', 'Template Name', 'Template Fields'])
        for file_path, tpl_name, fields in results:
            fields_str = ';'.join(fields)
            writer.writerow([file_path, tpl_name, fields_str])

def generate_unique_fields_csv(unique_fields, output_file):
    """Generate CSV file with unique template fields"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Unique Template Fields'])
        for field in unique_fields:
            writer.writerow([field])

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python extract_json_template.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    print(f"Searching for JSON files in {directory}...")
    results, unique_fields = extract_template_fields(directory)

    if not results:
        print("No JSON files with template field found")
        sys.exit(0)

    # Generate main CSV file
    output_file = 'json_template_fields.csv'
    generate_csv(results, output_file)

    # Generate unique fields CSV file
    unique_output_file = 'unique_template_fields.csv'
    generate_unique_fields_csv(unique_fields, unique_output_file)

    print(f"Found {len(results)} JSON files with template field")
    print(f"Generated {output_file}")
    print(f"Generated {unique_output_file} with {len(unique_fields)} unique fields")
    print("\nFiles found:")
    for file_path, tpl_name, fields in results:
        print(f"{file_path} (Template: {tpl_name}): {len(fields)} fields")

    print("\nSample unique fields:")
    for field in unique_fields[:10]:
        print(f"- {field}")
    if len(unique_fields) > 10:
        print(f"... and {len(unique_fields) - 10} more fields")
