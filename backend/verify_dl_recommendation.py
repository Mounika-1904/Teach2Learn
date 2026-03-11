import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ml.recommendation import RecommendationEngine, DUMMY_STUDENTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_dl_model():
    print("--- Verifying Deep Learning Recommendation Engine ---")
    
    try:
        # 1. Initialize Engine
        print("\n[Step 1] Initializing Engine...")
        engine = RecommendationEngine()
        
        # 2. Check for DL Model components
        print("\n[Step 2] Checking for Deep Learning components...")
        # Note: Model is built only after first train/predict call in the current logic, 
        # or we can force build it.
        # Let's run a recommendation to trigger the build.
        
        # 3. Running Recommendation
        student_id = 1
        print(f"\n[Step 3] Running recommendation for Student {student_id}...")
        recs = engine.recommend_tutors(student_id)
        
        if engine.autoencoder is not None and engine.encoder is not None:
             print("[PASS] Autoencoder and Encoder models are initialized.")
        else:
             print("[FAIL] DL Models are NOT initialized.")
             
        # 4. Check Output
        print(f"\n[Step 4] Checking output for Student {student_id}...")
        if len(recs) > 0:
            print(f"Top Recommendation: {recs[0]['name']} (Score: {recs[0]['score']})")
            print("[PASS] Recommendations returned.")
        else:
            print("[FAIL] No recommendations returned.")
            
    except ImportError as e:
        print(f"[FAIL] ImportError: {e}")
        print("Ensure tensorflow and keras are installed.")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    verify_dl_model()
