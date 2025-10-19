#!/usr/bin/env python3
"""
Comprehensive tests for MeshQuery fixes.
Tests all API endpoints, pagination, distance calculations, and frontend functionality.
"""
import requests
import json
import sys
import time
from typing import Dict, Any, List

BASE_URL = "http://localhost:8080"

class TestRunner:
    """Test runner for MeshQuery fixes."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name: str, condition: bool, message: str = ""):
        """Run a test and record result."""
        if condition:
            print(f"[PASS] {name}")
            if message:
                print(f"       {message}")
            self.passed += 1
            return True
        else:
            print(f"[FAIL] {name}")
            if message:
                print(f"       {message}")
            self.failed += 1
            return False
    
    def warn(self, name: str, message: str):
        """Log a warning."""
        print(f"[WARN] {name}: {message}")
        self.warnings += 1
    
    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({self.passed/total*100 if total > 0 else 0:.1f}%)")
        print(f"Failed: {self.failed}")
        print(f"Warnings: {self.warnings}")
        print("=" * 60)
        
        return self.failed == 0


def test_pagination_api(runner: TestRunner):
    """Test pagination on API endpoints."""
    print("\n--- Testing Pagination ---")
    
    # Test packets pagination
    try:
        resp = requests.get(f"{BASE_URL}/api/packets/data?page=1&limit=10", timeout=10)
        runner.test("Packets API responds", resp.status_code == 200)
        
        if resp.status_code == 200:
            data = resp.json()
            runner.test("Packets API has pagination fields", 
                       all(k in data for k in ['data', 'total_count', 'page', 'limit', 'total_pages']))
            runner.test("Packets API respects limit=10", 
                       len(data['data']) <= 10,
                       f"Got {len(data['data'])} items")
    except Exception as e:
        runner.test("Packets API responds", False, str(e))
    
    # Test nodes pagination
    try:
        resp = requests.get(f"{BASE_URL}/api/nodes/data?page=1&limit=10", timeout=10)
        runner.test("Nodes API responds", resp.status_code == 200)
        
        if resp.status_code == 200:
            data = resp.json()
            runner.test("Nodes API has pagination fields",
                       all(k in data for k in ['data', 'total_count', 'page', 'limit', 'total_pages']))
            runner.test("Nodes API respects limit=10",
                       len(data['data']) <= 10,
                       f"Got {len(data['data'])} items")
    except Exception as e:
        runner.test("Nodes API responds", False, str(e))
    
    # Test traceroute pagination
    try:
        resp = requests.get(f"{BASE_URL}/api/traceroute/data?page=1&limit=10", timeout=10)
        runner.test("Traceroute API responds", resp.status_code == 200)
        
        if resp.status_code == 200:
            data = resp.json()
            runner.test("Traceroute API has pagination fields",
                       all(k in data for k in ['data', 'total_count', 'page', 'limit', 'total_pages']))
            runner.test("Traceroute API respects limit=10",
                       len(data['data']) <= 10,
                       f"Got {len(data['data'])} items")
    except Exception as e:
        runner.test("Traceroute API responds", False, str(e))


def test_longest_links(runner: TestRunner):
    """Test longest links with distance calculations."""
    print("\n--- Testing Longest Links ---")
    
    try:
        resp = requests.get(f"{BASE_URL}/api/longest-links?min_distance=0&min_snr=-200&max_results=10", timeout=15)
        runner.test("Longest Links API responds", resp.status_code == 200)
        
        if resp.status_code == 200:
            data = resp.json()
            runner.test("Longest Links has summary", 'summary' in data)
            runner.test("Longest Links has direct_links", 'direct_links' in data)
            runner.test("Longest Links has indirect_links", 'indirect_links' in data)
            
            # Check direct links
            if 'direct_links' in data and len(data['direct_links']) > 0:
                direct_link = data['direct_links'][0]
                has_distance = direct_link.get('distance_km') is not None
                runner.test("Direct links have distance_km field",
                           'distance_km' in direct_link,
                           f"distance_km: {direct_link.get('distance_km')}")
                
                if has_distance:
                    runner.test("Direct links distance is not 'Unknown'",
                               direct_link['distance_km'] != 'Unknown' and direct_link['distance_km'] != 0,
                               f"distance_km: {direct_link.get('distance_km')}")
                else:
                    runner.warn("Direct links", "distance_km is None (nodes may not have GPS data)")
            else:
                runner.warn("Direct links", "No direct links found (may need more data)")
            
            # Check indirect links (complete paths)
            if 'indirect_links' in data and len(data['indirect_links']) > 0:
                indirect_link = data['indirect_links'][0]
                runner.test("Indirect links have total_distance_km field",
                           'total_distance_km' in indirect_link,
                           f"total_distance_km: {indirect_link.get('total_distance_km')}")
                
                runner.test("Indirect links have hop_count",
                           'hop_count' in indirect_link,
                           f"hop_count: {indirect_link.get('hop_count')}")
            else:
                runner.warn("Indirect links", "No indirect links found (may need more multi-hop data)")
                
    except Exception as e:
        runner.test("Longest Links API responds", False, str(e))


def test_dashboard_analytics(runner: TestRunner):
    """Test dashboard analytics including top nodes."""
    print("\n--- Testing Dashboard Analytics ---")
    
    try:
        resp = requests.get(f"{BASE_URL}/api/analytics", timeout=15)
        runner.test("Analytics API responds", resp.status_code == 200)
        
        if resp.status_code == 200:
            data = resp.json()
            runner.test("Analytics has top_nodes", 'top_nodes' in data)
            
            if 'top_nodes' in data and len(data['top_nodes']) > 0:
                top_node = data['top_nodes'][0]
                required_fields = ['node_id', 'display_name', 'packet_count']
                runner.test("Top nodes have required fields",
                           all(f in top_node for f in required_fields),
                           f"Fields: {list(top_node.keys())}")
                
                runner.test("Top nodes have packet_count > 0",
                           top_node.get('packet_count', 0) > 0,
                           f"packet_count: {top_node.get('packet_count')}")
            else:
                runner.warn("Top nodes", "No active nodes found (may need more data)")
                
    except Exception as e:
        runner.test("Analytics API responds", False, str(e))


def test_map_locations(runner: TestRunner):
    """Test map locations API."""
    print("\n--- Testing Map Locations ---")
    
    try:
        resp = requests.get(f"{BASE_URL}/api/locations", timeout=15)
        runner.test("Locations API responds", resp.status_code == 200)
        
        if resp.status_code == 200:
            data = resp.json()
            runner.test("Locations has locations field", 'locations' in data)
            runner.test("Locations has traceroute_links field", 'traceroute_links' in data)
            runner.test("Locations has packet_links field", 'packet_links' in data)
            
            if 'traceroute_links' in data:
                link_count = len(data['traceroute_links'])
                runner.test("Traceroute links present",
                           link_count > 0,
                           f"Found {link_count} traceroute links")
            
            if 'locations' in data:
                loc_count = len(data['locations'])
                runner.test("Node locations present",
                           loc_count > 0,
                           f"Found {loc_count} nodes with GPS")
                
    except Exception as e:
        runner.test("Locations API responds", False, str(e))


def test_frontend_pages(runner: TestRunner):
    """Test that frontend pages load correctly."""
    print("\n--- Testing Frontend Pages ---")
    
    pages = [
        ("/", "Dashboard"),
        ("/packets", "Packets"),
        ("/nodes", "Nodes"),
        ("/traceroute", "Traceroute"),
        ("/map", "Map"),
        ("/longest-links", "Longest Links"),
        ("/live-topography", "Live Topography"),
    ]
    
    for path, name in pages:
        try:
            resp = requests.get(f"{BASE_URL}{path}", timeout=10)
            runner.test(f"{name} page loads", resp.status_code == 200)
        except Exception as e:
            runner.test(f"{name} page loads", False, str(e))


def main():
    """Run all tests."""
    print("=" * 60)
    print("MeshQuery Fix Verification Tests")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            resp = requests.get(f"{BASE_URL}/", timeout=5)
            if resp.status_code == 200:
                print("Services are ready!\n")
                break
        except:
            pass
        time.sleep(2)
        print(f"Retry {i+1}/{max_retries}...")
    else:
        print("ERROR: Services did not start in time")
        sys.exit(1)
    
    # Run all tests
    runner = TestRunner()
    
    test_pagination_api(runner)
    test_longest_links(runner)
    test_dashboard_analytics(runner)
    test_map_locations(runner)
    test_frontend_pages(runner)
    
    # Print summary and exit with appropriate code
    success = runner.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

