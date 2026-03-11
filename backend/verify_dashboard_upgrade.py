import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_search_suggestions():
    print("\n--- Testing Search Suggestions ---")
    res = requests.get(f"{BASE_URL}/search_tutors?q=m")
    if res.status_code == 200:
        tutors = res.json()
        print(f"Found {len(tutors)} suggestions.")
        for t in tutors[:3]:
            print(f"- {t['name']} (Suggestion: {t.get('suggestion')}) | Score: {t.get('relevance_score'):.2f}")
    else:
        print(f"Error: {res.status_code}")

def test_top_tutors():
    print("\n--- Testing Top Tutors ---")
    res = requests.get(f"{BASE_URL}/top_tutors")
    if res.status_code == 200:
        tutors = res.json()
        print(f"Found {len(tutors)} top tutors.")
        for t in tutors:
            print(f"- {t['name']} | Rating: {t['rating']}")
    else:
        print(f"Error: {res.status_code}")

def test_recommendations():
    print("\n--- Testing Recommendations (Student 1) ---")
    res = requests.get(f"{BASE_URL}/recommend_tutors/1")
    if res.status_code == 200:
        data = res.json()
        print(f"Model: {data.get('model_type')}")
        recs = data.get('recommendations', [])
        print(f"Found {len(recs)} recommendations.")
        for r in recs:
            print(f"- {r['name']} | Score: {r.get('score')} | Rating: {r.get('rating')}")
    else:
        print(f"Error: {res.status_code}")

def test_notifications():
    print("\n--- Testing Notifications (User 1) ---")
    # Fetch
    res = requests.get(f"{BASE_URL}/notifications/1")
    if res.status_code == 200:
        notifs = res.json()
        print(f"Found {len(notifs)} notifications.")
        for n in notifs[:2]:
            print(f"- {n['message']} (Read: {n['is_read']})")
    else:
        print(f"Error: {res.status_code}")

if __name__ == "__main__":
    try:
        test_search_suggestions()
        test_top_tutors()
        test_recommendations()
        test_notifications()
    except Exception as e:
        print(f"Connection Error: {e}. Is the Flask server running?")
