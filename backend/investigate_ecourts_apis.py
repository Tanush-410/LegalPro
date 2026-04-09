"""
Investigation script to identify actual eCourts API endpoints
Used by: bengaluru.dcourts.gov.in, hcservices.ecourts.gov.in, njdg.ecourts.gov.in
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Suppress warnings
import urllib3
urllib3.disable_warnings()

print("="*80)
print("INVESTIGATING REAL eCORTS API ENDPOINTS")
print("="*80)

# Known eCourts API endpoints used in India
KNOWN_ENDPOINTS = {
    "hcservices": {
        "base": "https://hcservices.ecourts.gov.in",
        "endpoints": [
            "/ecourtindiaHC/index.php?act=case_status",
            "/ecourtindiaHC/api/case_search",
            "/ecourtindiaHC/webservices/rest/advocatewisedata",
            "/ecourtindiaHC/webservices/caseDetail",
        ]
    },
    "njdg": {
        "base": "https://njdg.ecourts.gov.in",
        "endpoints": [
            "/njdgnew/index.php",
            "/njdgnew/njdgapi",
            "/njdgnew/api/search",
            "/njdgnew/statistics",
        ]
    },
    "bengaluru_district": {
        "base": "https://bengaluru.dcourts.gov.in",
        "endpoints": [
            "/court-orders-search",
            "/api/cases",
            "/search/cases",
            "/searchorders",
        ]
    },
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://hcservices.ecourts.gov.in/',
    'X-Requested-With': 'XMLHttpRequest',
}

def test_endpoint(base_url, endpoint, method="GET", params=None):
    """Test if an endpoint returns valid JSON response"""
    url = base_url + endpoint
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, params=params, timeout=10, verify=False)
        else:
            response = requests.post(url, headers=HEADERS, json=params, timeout=10, verify=False)
        
        print(f"\n✓ {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response Type: JSON ✓")
                print(f"  Keys: {list(data.keys())[:5]}")
                return True, data
            except:
                print(f"  Response Type: HTML/Text")
                return True, response.text[:200]
        else:
            return False, response.status_code
    except Exception as e:
        print(f"✗ {url} - {str(e)[:50]}")
        return False, str(e)

# Step 1: Test basic endpoints
print("\n" + "="*80)
print("STEP 1: Testing Basic Endpoints")
print("="*80)

for portal_name, portal_config in KNOWN_ENDPOINTS.items():
    print(f"\n📍 Testing {portal_name} portal...")
    base_url = portal_config["base"]
    
    for endpoint in portal_config["endpoints"][:2]:  # Test first 2 endpoints
        time.sleep(0.5)  # Rate limiting
        test_endpoint(base_url, endpoint)

# Step 2: Test with search parameters
print("\n" + "="*80)
print("STEP 2: Testing with Search Parameters")
print("="*80)

# Common case search patterns
case_search_params = {
    "case_type": "WP",
    "case_no": "123",
    "year": "2024",
    "act": "case_search",
}

print("\n📍 Testing HC Services with search params...")
test_endpoint(
    "https://hcservices.ecourts.gov.in",
    "/ecourtindiaHC/index.php",
    params={"act": "case_status", "case_type": "WP", "case_no": "1", "year": "2024"}
)

# Step 3: Common eCourts web service endpoints
print("\n" + "="*80)
print("STEP 3: Testing NJDG API Endpoints")
print("="*80)

njdg_endpoints = [
    "/njdgnew/index.php?action=judgment_search",
    "/njdgnew/judgementsearch",
]

for endpoint in njdg_endpoints:
    time.sleep(0.5)
    test_endpoint("https://njdg.ecourts.gov.in", endpoint)

# Step 4: District court pattern
print("\n" + "="*80)
print("STEP 4: Testing District Court Patterns (Bengaluru)")
print("="*80)

print("\n📍 Testing Bengaluru District Court API...")
test_endpoint(
    "https://bengaluru.dcourts.gov.in",
    "/orders",
    params={"from_date": "01/01/2024", "to_date": "31/12/2024"}
)

# Step 5: Check for known working endpoints (documented by users)
print("\n" + "="*80)
print("STEP 5: Testing Documented Working Endpoints")
print("="*80)

documented_endpoints = [
    ("https://hcservices.ecourts.gov.in", "/ecourtindiaHC/index.php?act=case_status"),
    ("https://njdg.ecourts.gov.in", "/njdgnew/index.php"),
    ("https://services.ecourts.gov.in", "/ecourtindiaHC/index.php"),
]

for base_url, endpoint in documented_endpoints:
    time.sleep(0.5)
    print(f"\n🔍 Testing {base_url}{endpoint}")
    test_endpoint(base_url, endpoint)

print("\n" + "="*80)
print("INVESTIGATION COMPLETE")
print("="*80)
print("\n✓ Check above for endpoints that return Status 200 + JSON response")
print("✓ Those are the real APIs to use for data ingestion")
print("✓ Next step: Build ingestion script with working endpoints")
