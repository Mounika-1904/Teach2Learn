import requests
import json
import socket

BASE_URL = "http://127.0.0.1:5000"

def is_flask_running():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        return result == 0
    except:
        return False

def test_search():
    print("--- Verifying Search System Upgrade ---")
    
    if not is_flask_running():
        print("[SKIP] Flask app not running on 127.0.0.1:5000. Start app.py first.")
        return

    # Test cases: (query, use_ml, description)
    test_cases = [
        ("Dr. Aris", False, "Name Search (Exact)"),
        ("Machine Learning", False, "Subject Search (Exact)"),
        ("Deep Learni", False, "Subject Search (Partial)"),
        ("Structur", False, "Subject Search (Partial - B.Tech)"),
        ("ML", True, "ML-Enhanced Search (AI/DL Tutors)"),
        ("Networks", True, "ML-Enhanced Search (Cloud/Distributed)")
    ]
    
    for query, ml_enabled, desc in test_cases:
        url = f"{BASE_URL}/api/search_tutors?query={query}&ml={str(ml_enabled).lower()}"
        print(f"\n[Test] {desc} | Query: '{query}' | ML: {ml_enabled}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                results = response.json()
                print(f"Found {len(results)} results.")
                for r in results[:3]:
                    score_info = f" (Score: {r.get('score', 'N/A')})" if ml_enabled else ""
                    print(f"- {r['name']}: {r['subjects']}{score_info}")
                if len(results) > 0:
                    print("[PASS]")
                else:
                    print("[WARN] No results found.")
            else:
                print(f"[FAIL] HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_search()
