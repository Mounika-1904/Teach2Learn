import requests
import json

def test_recommendation_api():
    student_id = 1
    url = f"http://127.0.0.1:5000/api/recommend_tutors/{student_id}"
    
    print(f"Testing Recommendation API: {url}")
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Metadata:")
            print(f"- Model Type: {data.get('model_type')}")
            print(f"- Encoding Dimension: {data.get('encoding_dimension')}")
            
            print("\nRecommendations:")
            for rec in data.get('recommendations', []):
                print(f"- {rec['name']} (Score: {rec['score']})")
            
            # Validation
            assert data.get('model_type') == "Deep Learning Autoencoder"
            assert data.get('encoding_dimension') == 64
            print("\n[PASS] API Metadata verified successfully.")
        else:
            print(f"[FAIL] Server returned error: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        print("Note: Ensure the Flask server is running on http://127.0.0.1:5000")

if __name__ == "__main__":
    test_recommendation_api()
