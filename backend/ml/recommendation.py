import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras import regularizers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import os
import pickle
from tensorflow.keras.models import load_model

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to persistent models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'dl_model.h5')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'vectorizer.pkl')

# Expanded B.Tech & M.Tech Subject Corpus
SUBJECT_CORPUS = {
    "Computer Science": [
        "Data Structures", "Algorithms", "Operating Systems", "DBMS", "Computer Networks",
        "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Distributed Systems", "Compiler Design", "Software Engineering", "Cloud Computing",
        "Big Data", "Cyber Security", "Blockchain", "IoT"
    ],
    "Electronics": [
        "Embedded Systems", "VLSI", "Digital Signal Processing", "Communication Systems", "Microprocessors"
    ],
    "Electrical": [
        "Power Systems", "Control Systems", "Electrical Machines", "Power Electronics"
    ],
    "Mechanical": [
        "Thermodynamics", "Fluid Mechanics", "Robotics", "Manufacturing Technology", "Heat Transfer"
    ],
    "Civil": [
        "Structural Engineering", "Geotechnical Engineering", "Environmental Engineering", "Transportation Engineering"
    ],
    "Mathematics Core": [
        "Linear Algebra", "Probability & Statistics", "Numerical Methods", "Optimization Techniques"
    ]
}

# Flattened list for vectorizer priming
ALL_SUBJECTS = [sub for subs in SUBJECT_CORPUS.values() for sub in subs]

DUMMY_TUTORS = [
    {"id": 1, "name": "Dr. Aris", "subjects": "Artificial Intelligence Machine Learning Deep Learning NLP", "rating": 4.8},
    {"id": 2, "name": "Prof. Khanna", "subjects": "Computer Networks Distributed Systems Cloud Computing", "rating": 4.5},
    {"id": 3, "name": "Sarah Miller", "subjects": "Data Structures Algorithms Software Engineering", "rating": 4.2},
    {"id": 4, "name": "James Watt", "subjects": "Thermodynamics Heat Transfer Fluid Mechanics", "rating": 4.6},
    {"id": 5, "name": "Elena Volt", "subjects": "Power Systems Electrical Machines Control Systems", "rating": 4.9},
    {"id": 6, "name": "Vikas Gupta", "subjects": "VLSI Embedded Systems Microprocessors", "rating": 4.4},
    {"id": 7, "name": "Rohan Das", "subjects": "Structural Engineering Geotechnical Engineering", "rating": 4.3},
    {"id": 8, "name": "Anita Desai", "subjects": "Linear Algebra Probability Statistics Optimization", "rating": 4.7},
]

DUMMY_STUDENTS = {
    1: "Machine Learning AI",
    2: "Cloud Computing Networks",
    3: "Robotics Mechatronics",
    4: "Power Electronics Machines"
}

# Global Deep Learning Model Components
vectorizer = None
autoencoder = None
encoder = None
model_trained = False

class RecommendationEngine:
    def __init__(self, tutors=None):
        """
        Initialize the Production-Ready Deep Learning Recommendation Engine.
        """
        self.tutors = tutors if tutors is not None else DUMMY_TUTORS
        self._check_and_load_model()

    @property
    def autoencoder(self):
        global autoencoder
        return autoencoder

    @property
    def encoder(self):
        global encoder
        return encoder

    def _check_and_load_model(self):
        """
        Checks if a trained model exists on disk and loads it if found.
        """
        global vectorizer, autoencoder, encoder, model_trained
        
        if model_trained:
            return

        if vectorizer is None:
            # Enhanced TF-IDF with sublinear tf scaling and broader ngram range
            vectorizer = TfidfVectorizer(
                stop_words='english', 
                ngram_range=(1, 2), 
                sublinear_tf=True
            )

        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            try:
                logger.info("Loading production model from disk...")
                autoencoder = load_model(MODEL_PATH, compile=False)
                latent_layer = autoencoder.get_layer("latent_layer")
                encoder = Model(autoencoder.input, latent_layer.output)
                
                with open(VECTORIZER_PATH, 'rb') as f:
                    vectorizer = pickle.load(f)
                
                model_trained = True
                logger.info("Production model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading model: {e}. Re-training required.")
                model_trained = False
        else:
            logger.info("No persistent model found. Training scheduled.")

    def build_model(self, input_dim):
        """
        Builds a Production-Ready Deep Learning Autoencoder.
        - Deeper architecture for complex B.Tech relationship mapping.
        - Higher dropout for better generalization across academic domains.
        """
        global autoencoder, encoder
        input_layer = Input(shape=(input_dim,))
        
        # Encoder: Richer feature extraction
        encoded = Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.001))(input_layer)
        encoded = Dropout(0.3)(encoded)
        encoded = Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001))(encoded)
        
        # Latent Representation (Bottleneck)
        latent = Dense(64, activation='relu', name="latent_layer")(encoded)
        
        # Decoder: Reconstruction
        decoded = Dense(128, activation='relu')(latent)
        decoded = Dense(256, activation='relu')(decoded)
        output_layer = Dense(input_dim, activation='sigmoid')(decoded)

        autoencoder = Model(input_layer, output_layer)
        encoder = Model(input_layer, latent)

        autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
        logger.info("Upgraded DL Architecture built.")
        return autoencoder, encoder

    def build_autoencoder(self, input_dim):
        """Alias for backward compatibility."""
        return self.build_model(input_dim)

    def train(self, data_matrix):
        """
        Train and save the model for production use.
        """
        global model_trained, autoencoder, vectorizer
        if model_trained: return

        input_dim = data_matrix.shape[1]
        self.build_model(input_dim)
        
        logger.info("Starting DL Model training on engineering corpus...")
        autoencoder.fit(data_matrix, data_matrix,
                       epochs=100,
                       batch_size=8,
                       shuffle=True,
                       verbose=0)
        
        model_trained = True
        
        try:
            autoencoder.save(MODEL_PATH)
            with open(VECTORIZER_PATH, 'wb') as f:
                pickle.dump(vectorizer, f)
            logger.info("Model saved to disk.")
        except Exception as e:
            logger.error(f"Save error: {e}")

    def train_global_model(self, data_matrix):
        """Alias for backward compatibility."""
        return self.train(data_matrix)

    def recommend_tutors(self, student_query, student_skill_level=None, top_n=5):
        """
        Compute recommendations using latent similarity, normalized rating, and personalized skill-based rating.
        Formula: 0.5 * Similarity + 0.2 * Normalized General Rating + 0.3 * Normalized Skill-Level Rating
        """
        global vectorizer, encoder, model_trained
        try:
            query_text = ""
            if isinstance(student_query, int):
                query_text = DUMMY_STUDENTS.get(student_query, "general engineering")
            else:
                query_text = str(student_query)

            # Ensure corpus completeness including query
            tutor_texts = [t.get('subjects', '') for t in self.tutors]
            # Use ALL_SUBJECTS to prime the vectorizer if first run
            prime_texts = tutor_texts + ALL_SUBJECTS + [query_text]

            if not model_trained:
                tfidf_matrix = vectorizer.fit_transform(prime_texts).toarray()
                self.train(tfidf_matrix)
                # Re-transform just tutor and query
                full_matrix = vectorizer.transform(tutor_texts + [query_text]).toarray()
            else:
                full_matrix = vectorizer.transform(tutor_texts + [query_text]).toarray()
            
            latent_vectors = encoder.predict(full_matrix, verbose=0)
            tutor_latent = latent_vectors[:-1]
            query_latent = latent_vectors[-1].reshape(1, -1)

            similarities = cosine_similarity(query_latent, tutor_latent).flatten()
            
            results = []
            for i, sim in enumerate(similarities):
                tutor = self.tutors[i].copy()
                rating = tutor.get('rating', 0.0)
                norm_rating = rating / 5.0

                # Calculate personalized rating from same skill level students (defaults to general rating if none exists)
                skill_rating = tutor.get('rating_from_same_skill_level_students')
                if skill_rating is None:
                    skill_rating = rating
                norm_skill_rating = skill_rating / 5.0
                
                # NEW PRODUCTION RANKING FORMULA
                # final_score = 0.5 * similarity_score + 0.2 * normalized_rating + 0.3 * normalized_skill_level_rating
                final_score = (0.5 * sim) + (0.2 * norm_rating) + (0.3 * norm_skill_rating)
                
                tutor['similarity'] = float(sim)
                tutor['score'] = float(f"{final_score:.4f}")
                results.append(tutor)

            # Rank by final_score
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_n]

        except Exception as e:
            logger.error(f"Recommendation Error: {e}")
            return []

if __name__ == "__main__":
    print("--- PRODUCTION RECOMMENDATION ENGINE TEST ---")
    engine = RecommendationEngine()
    test_queries = ["I want to learn Machine Learning and Deep Learning", "Structural Engineering for Bridge Design"]
    
    for q in test_queries:
        print(f"\nQuery: {q}")
        recs = engine.recommend_tutors(q)
        for r in recs:
            print(f"- {r['name']} (Score: {r['score']}, Sim: {r.get('similarity'):.2f}, Rate: {r.get('rating')}) -> {r['subjects']}")
