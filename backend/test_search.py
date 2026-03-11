import requests

def test_search(query):
    url = f"http://127.0.0.1:5000/api/search_tutors?query={query}"
    try:
        response = requests.get(url)
        print(f"Query: {query}")
        print(f"Status: {response.status_code}")
        print(f"Results: {response.json()}")
        print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search("Math")
    test_search("Aris")
    test_search("")
