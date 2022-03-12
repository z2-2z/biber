#!/usr/bin/env python3

import json
import sys
sys.path.append("../..")

import biber

def get_test_data():
    with open("test-data.json") as f:
        return json.load(f)

def main():
    test_data = get_test_data()
    
    for entry in test_data:
        print(f"Running example: {entry['example']}")
        biber.parse_markdown(entry["markdown"])

if __name__ == "__main__":
    main()
