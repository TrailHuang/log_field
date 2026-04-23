#!/usr/bin/env python3
import os
import re
import csv

def extract_log_fields(directory):
    """Search all C source files and extract LOG_FIELD_REG macro definitions"""
    pattern = r'LOG_FIELD_REG\s*\(\s*"([^"]+)"\s*,\s*([^\)]+)\s*\)'
    fields = []

    # Search all C language files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.c', '.h')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.findall(pattern, content)
                        for field_name, func_name in matches:
                            # Clean function name, remove semicolons and whitespace
                            func_name = func_name.strip().rstrip(';')
                            fields.append((field_name, func_name))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Sort by field name
    fields.sort(key=lambda x: x[0])

    return fields

def generate_csv(fields, output_file):
    """Generate CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Field Name', 'Function Name'])
        for field_name, func_name in fields:
            writer.writerow([field_name, func_name])

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python extract_log_fields.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    print(f"Searching for LOG_FIELD_REG in {directory}...")
    fields = extract_log_fields(directory)

    if not fields:
        print("No LOG_FIELD_REG found")
        sys.exit(0)

    output_file = 'log_fields.csv'
    generate_csv(fields, output_file)

    print(f"Found {len(fields)} LOG_FIELD_REG entries")
    print(f"Generated {output_file}")
    print("\nFields found:")
    for field_name, func_name in fields:
        print(f"{field_name}: {func_name}")
