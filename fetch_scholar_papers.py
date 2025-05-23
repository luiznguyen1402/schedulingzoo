#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import bibtexparser
import os
import sys
from datetime import datetime
import time
import re

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    options = Options()
    options.add_argument('--headless=new')  # Use new headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    # Add user agent to avoid detection
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
    
    # Install and setup ChromeDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_paper_info(element):
    """Extract paper information from a Google Scholar result element"""
    try:
        # Extract title
        title_elem = element.find_element(By.CLASS_NAME, 'gs_rt')
        title = title_elem.text.strip()
        
        # Extract authors and venue
        authors_venue = element.find_element(By.CLASS_NAME, 'gs_a').text
        authors = authors_venue.split('-')[0].strip()
        venue = authors_venue.split('-')[1].strip() if len(authors_venue.split('-')) > 1 else ''
        
        # Extract year
        year_match = re.search(r'\b\d{4}\b', authors_venue)
        year = year_match.group(0) if year_match else ''
        
        # Extract URL if available
        url = ''
        try:
            url = title_elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
        except:
            pass
            
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'venue': venue,
            'url': url
        }
    except Exception as e:
        print(f"Error extracting paper info: {e}")
        return None

def fetch_citing_papers(citation_url):
    """Fetch papers from Google Scholar using Selenium"""
    papers = []
    driver = None
    
    try:
        print("Setting up Chrome driver...")
        driver = setup_driver()
        
        print(f"Fetching papers from {citation_url}")
        driver.get(citation_url)
        
        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'gs_r'))
        )
        
        # Get all paper elements
        paper_elements = driver.find_elements(By.CLASS_NAME, 'gs_r')
        
        print(f"Found {len(paper_elements)} papers")
        for element in paper_elements:
            paper_info = extract_paper_info(element)
            if paper_info:
                papers.append(paper_info)
            time.sleep(1)  # Add delay between processing papers
            
    except TimeoutException:
        print("Timeout waiting for Google Scholar to load")
    except Exception as e:
        print(f"Error fetching papers: {e}")
    finally:
        if driver:
            driver.quit()
            
    return papers

def convert_to_bibtex(papers):
    """Convert paper data to BibTeX entries"""
    entries = []
    
    for i, paper in enumerate(papers):
        # Generate citation key
        first_author = paper['authors'].split(',')[0].split()[-1] if paper['authors'] else 'Unknown'
        year = paper['year'] or 'XXXX'
        key = f"{first_author}{year}"
        
        # Create BibTeX entry
        entry = {
            'ID': key,
            'ENTRYTYPE': 'article',
            'title': paper['title'],
            'author': paper['authors'],
            'year': paper['year'],
            'journal': paper['venue'],
            'url': paper['url']
        }
        
        # Remove empty fields
        entry = {k: v for k, v in entry.items() if v}
        entries.append(entry)
        
    return entries

def main():
    citation_urls = [
        "https://scholar.google.com/scholar?cites=5784273002509972618&as_sdt=2005&sciodt=0,5&hl=de",
        "https://scholar.google.com/scholar?start=10&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=20&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=30&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=40&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=50&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=60&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=70&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=81&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=91&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc=",
        "https://scholar.google.com/scholar?start=101&hl=de&as_sdt=2005&sciodt=0,5&cites=5784273002509972618&scipsc="
    ]
    
    # Create bib directory if it doesn't exist
    if not os.path.exists('bib'):
        os.makedirs('bib')
        
    # Fetch papers from all URLs
    print("Starting Google Scholar paper fetch...")
    all_papers = []
    for url in citation_urls:
        print(f"\nProcessing URL: {url}")
        papers = fetch_citing_papers(url)
        if papers:
            all_papers.extend(papers)
            print(f"Found {len(papers)} papers from this URL")
            # Add a delay between processing different URLs to avoid rate limiting
            time.sleep(2)
    
    if not all_papers:
        print("No papers found or error occurred")
        sys.exit(1)
        
    # Convert to BibTeX
    bibtex_entries = convert_to_bibtex(all_papers)
    
    # Create BibTeX database
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = bibtex_entries
    
    # Save to file
    output_file = f"bib/hard_scheduling_papers.bib"
    writer = bibtexparser.bwriter.BibTexWriter()
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(writer.write(db))
        
    print(f"\nSuccessfully saved {len(all_papers)} papers to {output_file}")

if __name__ == "__main__":
    main() 