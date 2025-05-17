#!/usr/bin/env python3

import bibtexparser
import json
from datetime import datetime
import os
import re

# Taxonomy categories
TAXONOMY = {
    "parameters": {
        "n": "number of jobs",
        "m": "number of machines",
        "p_max": "maximum processing time",
        "d_max": "maximum deadline",
        "r_max": "maximum release time",
        "k": "solution size parameter",
        "w_max": "maximum weight",
        "Delta": "maximum degree (for precedence graphs)",
        "tw": "treewidth (for precedence graphs)"
    },
    "complexity_classes": {
        "FPT": "Fixed-Parameter Tractable",
        "XP": "Slice-wise Polynomial",
        "W[1]-hard": "W[1]-hard",
        "W[2]-hard": "W[2]-hard",
        "para-NP-hard": "Parameterized NP-hard"
    },
    "problem_types": {
        "single_machine": "Single Machine Scheduling",
        "parallel_machines": "Parallel Machine Scheduling",
        "flow_shop": "Flow Shop Scheduling",
        "job_shop": "Job Shop Scheduling",
        "open_shop": "Open Shop Scheduling",
        "precedence": "Scheduling with Precedence Constraints",
        "interval": "Interval Scheduling",
        "resource": "Resource Constrained Scheduling"
    },
    "objectives": {
        "makespan": "Minimize Makespan (Cmax)",
        "sum_completion": "Minimize Sum of Completion Times",
        "weighted_completion": "Minimize Weighted Sum of Completion Times",
        "tardiness": "Minimize Tardiness",
        "lateness": "Minimize Lateness",
        "num_tardy": "Minimize Number of Tardy Jobs",
        "energy": "Minimize Energy Consumption"
    }
}

def extract_keywords(text):
    """Extract relevant keywords from text"""
    keywords = set()
    
    # Convert text to lowercase for better matching
    text = text.lower()
    
    # Problem type keywords
    if any(x in text for x in ['single machine', '1-machine', '1 machine']):
        keywords.add('single_machine')
    if any(x in text for x in ['parallel machine', 'identical machine', 'uniform machine']):
        keywords.add('parallel_machines')
    if 'flow shop' in text:
        keywords.add('flow_shop')
    if 'job shop' in text:
        keywords.add('job_shop')
    if 'precedence' in text:
        keywords.add('precedence')
    if 'interval' in text:
        keywords.add('interval')
        
    # Objective keywords
    if any(x in text for x in ['makespan', 'cmax', 'c_max']):
        keywords.add('makespan')
    if 'completion time' in text:
        if 'weighted' in text:
            keywords.add('weighted_completion')
        else:
            keywords.add('sum_completion')
    if 'tardiness' in text:
        keywords.add('tardiness')
    if 'lateness' in text:
        keywords.add('lateness')
    if any(x in text for x in ['number of tardy', 'num tardy', 'tardy jobs']):
        keywords.add('num_tardy')
        
    # Parameter keywords
    if any(x in text for x in ['fixed-parameter', 'fpt']):
        keywords.add('FPT')
    if 'w[1]' in text:
        keywords.add('W[1]-hard')
    if 'w[2]' in text:
        keywords.add('W[2]-hard')
    if 'para-np' in text:
        keywords.add('para-NP-hard')
        
    return keywords

def classify_paper(entry):
    """Classify a paper based on its title and other fields"""
    # Combine title and journal for better classification
    text_to_analyze = f"{entry.get('title', '')} {entry.get('journal', '')}"
    
    # Extract keywords
    keywords = extract_keywords(text_to_analyze)
    
    # Create classification
    classification = {
        'title': entry.get('title', ''),
        'authors': entry.get('author', ''),
        'year': entry.get('year', ''),
        'url': entry.get('url', ''),
        'problem_types': [pt for pt in TAXONOMY['problem_types'] if pt in keywords],
        'objectives': [obj for obj in TAXONOMY['objectives'] if obj in keywords],
        'complexity_classes': [cc for cc in TAXONOMY['complexity_classes'] if cc in keywords]
    }
    
    return classification

def main():
    # Read the BibTeX file
    bib_file = f"bib/scholar_papers_{datetime.now().strftime('%Y%m%d')}.bib"
    if not os.path.exists(bib_file):
        print(f"BibTeX file {bib_file} not found!")
        return
        
    with open(bib_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)
        
    # Classify papers
    classifications = []
    for entry in bib_database.entries:
        classification = classify_paper(entry)
        classifications.append(classification)
        
    # Save classifications
    output_file = f"bib/paper_classifications.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'taxonomy': TAXONOMY,
            'papers': classifications
        }, f, indent=2)
        
    # Print summary
    print("\nPaper Classifications:")
    print("=====================")
    for paper in classifications:
        print(f"\nTitle: {paper['title']}")
        print(f"Authors: {paper['authors']}")
        print(f"Year: {paper['year']}")
        if paper['problem_types']:
            print(f"Problem Types: {', '.join(paper['problem_types'])}")
        if paper['objectives']:
            print(f"Objectives: {', '.join(paper['objectives'])}")
        if paper['complexity_classes']:
            print(f"Complexity Classes: {', '.join(paper['complexity_classes'])}")
        print("-" * 80)
        
    print(f"\nClassifications saved to {output_file}")

if __name__ == "__main__":
    main() 