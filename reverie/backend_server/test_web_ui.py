#!/usr/bin/env python3
"""
Test script to verify the web UI integration is working properly.
"""
import requests
import json
import sys

def test_simulation_config_page():
    """Test that the simulation config page loads"""
    print("🧪 Testing simulation config page...")
    try:
        response = requests.get('http://localhost:8000/simulation_config/', timeout=5)
        if response.status_code == 200:
            print("✅ Simulation config page loads successfully")
            return True
        else:
            print(f"❌ Simulation config page returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server at http://localhost:8000")
        print("   Make sure the Django server is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error testing config page: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n🧪 Testing API endpoint...")
    try:
        test_config = {
            "fork_simulation": "base_the_ville_isabella_maria_klaus",
            "new_simulation": "test-web-ui",
            "steps": 10,
            "speed": 2
        }

        response = requests.post(
            'http://localhost:8000/api/start_simulation/',
            json=test_config,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ API endpoint working correctly")
                print(f"   Config: {json.dumps(result.get('config', {}), indent=2)}")
                return True
            else:
                print(f"❌ API returned error: {result.get('message')}")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server at http://localhost:8000")
        print("   Make sure the Django server is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_landing_page():
    """Test that the landing page has the new link"""
    print("\n🧪 Testing landing page...")
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            if '/simulation_config/' in response.text:
                print("✅ Landing page has link to simulation config")
                return True
            else:
                print("❌ Landing page missing link to simulation config")
                return False
        else:
            print(f"❌ Landing page returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing landing page: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Web UI Integration Test")
    print("=" * 50)

    results = []
    results.append(test_simulation_config_page())
    results.append(test_api_endpoint())
    results.append(test_landing_page())

    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed!")
        print("\n📋 Quick Start Guide:")
        print("1. Start Django: cd environment/frontend_server && python manage.py runserver")
        print("2. Open http://localhost:8000/")
        print("3. Click 'Configure New Simulation'")
        print("4. Fill in the form and click 'Start Simulation'")
        print("5. Follow the instructions to run the backend simulation")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
