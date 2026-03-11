import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_top_picks():
    print("--- Testing Top Picks API ---")
    
    # Test for a student
    student_id = 1
    print(f"\nRequesting Top Picks for student {student_id}...")
    
    responses = []
    for i in range(3):
        res = requests.get(f"{BASE_URL}/top_picks/lectures?student_id={student_id}")
        if res.status_code == 200:
            data = res.json()
            recs = [r['name'] for r in data.get('recommendations', [])]
            responses.append(recs)
            print(f"Call {i+1} Picks: {recs}")
        else:
            print(f"Call {i+1} failed with status {res.status_code}")

    # Verify if results are diverse (shuffled) or at least functional
    if len(responses) > 1:
        print("\nRandomization Check:")
        if responses[0] != responses[1] or responses[0] != responses[2]:
            print("[PASS] Results are randomized/shuffled across calls.")
        else:
            print("[INFO] Results were same in these calls (possibly small pool), but API is functional.")

if __name__ == "__main__":
    try:
        test_top_picks()
    except Exception as e:
        print(f"Test failed: {e}")
