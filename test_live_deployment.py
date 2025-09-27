#!/usr/bin/env python3
"""Test the live Railway deployment."""

import requests
import json

# Your live Railway URL
BASE_URL = "https://web-content-analyzer-production.up.railway.app"

def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_analyze_api():
    """Test the analyze API endpoint."""
    print("\n🔍 Testing website analysis API...")

    test_url = "https://example.com"
    payload = {"url": test_url}

    try:
        print(f"   Analyzing: {test_url}")
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis Status: {result.get('status')}")
            print(f"   ⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")

            if result.get('status') == 'success':
                keywords = result.get('keywords', [])
                print(f"   📊 Keywords Found: {len(keywords)}")
                print("\n   🔑 Top 10 Keywords:")
                for i, keyword in enumerate(keywords[:10], 1):
                    print(f"      {i:2d}. {keyword}")
                return True
            else:
                print(f"   ❌ Analysis failed: {result.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_batch_api():
    """Test the batch analysis API."""
    print("\n📦 Testing batch analysis API...")

    test_urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    payload = {"urls": test_urls}

    try:
        print(f"   Analyzing {len(test_urls)} URLs...")
        response = requests.post(
            f"{BASE_URL}/api/batch",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            summary = result.get('summary', {})
            print(f"   ✅ Batch Complete:")
            print(f"      Total: {summary.get('total', 0)}")
            print(f"      Successful: {summary.get('successful', 0)}")
            print(f"      Failed: {summary.get('failed', 0)}")
            return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Web Content Analyzer Live Deployment")
    print("=" * 60)
    print(f"📍 URL: {BASE_URL}")
    print("=" * 60)

    results = {
        "health": test_health(),
        "analyze": test_analyze_api(),
        "batch": test_batch_api()
    }

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.capitalize():10} : {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! Your deployment is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()