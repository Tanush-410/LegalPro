#!/usr/bin/env python3
"""
Test actual eCourts portals to understand their structure
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

def test_hcservices_portal():
    """Test High Court Services portal"""
    print("=" * 60)
    print("Testing: hcservices.ecourts.gov.in")
    print("=" * 60)
    
    url = "https://hcservices.ecourts.gov.in/ecourtindiaHC/index.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find search form
        forms = soup.find_all('form')
        print(f"✓ Forms found: {len(forms)}")
        
        if forms:
            form = forms[0]
            print(f"\nForm details:")
            print(f"  Action: {form.get('action')}")
            print(f"  Method: {form.get('method')}")
            
            # Get input fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"  Fields: {len(inputs)}")
            for inp in inputs[:10]:
                name = inp.get('name', 'unnamed')
                inp_type = inp.name if inp.name in ['select', 'textarea'] else inp.get('type')
                print(f"    - {name} ({inp_type})")
        
        # Check for tables
        tables = soup.find_all('table')
        print(f"\n✓ Tables: {len(tables)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_district_portal():
    """Test District Court portal (Bengaluru example)"""
    print("\n" + "=" * 60)
    print("Testing: bengaluru.dcourts.gov.in")
    print("=" * 60)
    
    # Try different possible URLs
    urls = [
        "https://bengaluru.dcourts.gov.in/court-orders-search",
        "https://bengaluru.dcourts.gov.in/",
        "https://bengaluru.ecourts.gov.in/",
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for url in urls:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                forms = soup.find_all('form')
                tables = soup.find_all('table')
                print(f"  Forms: {len(forms)}, Tables: {len(tables)}")
                
                if forms:
                    form = forms[0]
                    inputs = form.find_all(['input', 'select'])
                    print(f"  Form inputs: {len(inputs)}")
                    for inp in inputs[:5]:
                        print(f"    - {inp.get('name')}")
                
                return True
                
        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
    
    return False

def test_njdg_portal():
    """Test NJDG portal"""
    print("\n" + "=" * 60)
    print("Testing: njdg.ecourts.gov.in")
    print("=" * 60)
    
    url = "https://njdg.ecourts.gov.in/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content length: {len(response.content)}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for API endpoints or data
        scripts = soup.find_all('script')
        print(f"✓ Scripts: {len(scripts)}")
        
        # Check for API calls
        for script in scripts[:3]:
            if script.string and 'api' in script.string.lower():
                print(f"  Found potential API: {script.string[:100]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_hcservices_portal()
    test_district_portal()
    test_njdg_portal()
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
