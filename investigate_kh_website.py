#!/usr/bin/env python3
"""Investigate Karnataka High Court website structure"""

import requests
from bs4 import BeautifulSoup
import json

url = "https://judiciary.karnataka.gov.in/ds_judgment.php"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

try:
    print("🔍 Fetching Karnataka High Court judgment page...")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Response Length: {len(response.text)} bytes")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for page structure
    print("\n=== Page Structure ===")
    tables = soup.find_all('table')
    print(f"Tables found: {len(tables)}")
    
    forms = soup.find_all('form')
    print(f"Forms found: {len(forms)}")
    
    links = soup.find_all('a')
    print(f"Links found: {len(links)}")
    
    # Look for search parameters
    inputs = soup.find_all('input')
    print(f"Input fields: {len(inputs)}")
    for inp in inputs[:5]:
        print(f"  - {inp.get('name')}: {inp.get('id')}")
    
    # Check for case-related content
    print("\n=== Content Analysis ===")
    text_lower = response.text.lower()
    print(f"Contains 'judgment': {('judgment' in text_lower)}")
    print(f"Contains 'case': {('case' in text_lower)}")
    print(f"Contains 'judge': {('judge' in text_lower)}")
    print(f"Contains 'order': {('order' in text_lower)}")
    
    # Try to find all text content
    body = soup.find('body')
    if body:
        print(f"\nBody content preview (first 1500 chars):")
        text = body.get_text()
        print(text[:1500])
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
