import os
import logging

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'dl_model.h5')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'vectorizer.pkl')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for lazy initialization
_tf = None
_vectorizer_class = None
_cosine_similarity = None
_autoencoder = None
_encoder = None
_vectorizer_instance = None
_model_trained = False

def get_tf():
    global _tf
    if _tf is None:
        import tensorflow as tf
        # Suppress TensorFlow logging
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        _tf = tf
    return _tf

def get_sklearn_components():
    global _vectorizer_class, _cosine_similarity
    if _vectorizer_class is None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        _vectorizer_class = TfidfVectorizer
        _cosine_similarity = cosine_similarity
    return _vectorizer_class, _cosine_similarity

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

class RecommendationEngine:
    def __init__(self, tutors=None):
        self.tutors = tutors if tutors is not None else DUMMY_TUTORS
        self._check_and_load_model()

    @property
    def autoencoder(self):
        global _autoencoder
        return _autoencoder

    @property
    def encoder(self):
        global _encoder
        return _encoder

    def _check_and_load_model(self):
        global _vectorizer_instance, _autoencoder, _encoder, _model_trained
        
        if _model_trained:
            return

        TfidfVectorizer, _ = get_sklearn_components()

        if _vectorizer_instance is None:
            _vectorizer_instance = TfidfVectorizer(
                stop_words='english', 
                ngram_range=(1, 2), 
                sublinear_tf=True
            )

        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            try:
                import pickle
                tf = get_tf()
                logger.info("Loading production model from disk...")
                _autoencoder = tf.keras.models.load_model(MODEL_PATH, compile=False)
                latent_layer = _autoencoder.get_layer("latent_layer")
                _encoder = tf.keras.models.Model(_autoencoder.input, latent_layer.output)
                
                with open(VECTORIZER_PATH, 'rb') as f:
                    _vectorizer_instance = pickle.load(f)
                
                _model_trained = True
                logger.info("Production model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading model: {e}. Re-training required.")
                _model_trained = False
        else:
            logger.info("No persistent model found. Training scheduled.")

    def build_model(self, input_dim):
        global _autoencoder, _encoder
        tf = get_tf()
        from tensorflow.keras.layers import Input, Dense, Dropout
        from tensorflow.keras.models import Model
        from tensorflow.keras import regularizers

        input_layer = Input(shape=(input_dim,))
        encoded = Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.001))(input_layer)
        encoded = Dropout(0.3)(encoded)
        encoded = Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001))(encoded)
        latent = Dense(64, activation='relu', name="latent_layer")(encoded)
        decoded = Dense(128, activation='relu')(latent)
        decoded = Dense(256, activation='relu')(decoded)
        output_layer = Dense(input_dim, activation='sigmoid')(decoded)

        _autoencoder = Model(input_layer, output_layer)
        _encoder = Model(input_layer, latent)
        _autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
        return _autoencoder, _encoder

    def train(self, data_matrix):
        global _model_trained, _autoencoder, _vectorizer_instance
        if _model_trained: return

        input_dim = data_matrix.shape[1]
        self.build_model(input_dim)
        
        logger.info("Starting DL Model training...")
        _autoencoder.fit(data_matrix, data_matrix, epochs=100, batch_size=8, shuffle=True, verbose=0)
        _model_trained = True
        
        try:
            import pickle
            _autoencoder.save(MODEL_PATH)
            with open(VECTORIZER_PATH, 'wb') as f:
                pickle.dump(_vectorizer_instance, f)
            logger.info("Model saved to disk.")
        except Exception as e:
            logger.error(f"Save error: {e}")

    def recommend_tutors(self, student_query, student_skill_level=None, top_n=5):
        global _vectorizer_instance, _encoder, _model_trained
        _, cosine_similarity = get_sklearn_components()
        import numpy as np
        
        try:
            query_text = str(student_query) if not isinstance(student_query, int) else DUMMY_STUDENTS.get(student_query, "general engineering")
            tutor_texts = [t.get('subjects', '') for t in self.tutors]
            prime_texts = tutor_texts + ALL_SUBJECTS + [query_text]

            if not _model_trained:
                tfidf_matrix = _vectorizer_instance.fit_transform(prime_texts).toarray()
                self.train(tfidf_matrix)
                full_matrix = _vectorizer_instance.transform(tutor_texts + [query_text]).toarray()
            else:
                full_matrix = _vectorizer_instance.transform(tutor_texts + [query_text]).toarray()
            
            latent_vectors = _encoder.predict(full_matrix, verbose=0)
            tutor_latent = latent_vectors[:-1]
            query_latent = latent_vectors[-1].reshape(1, -1)
            similarities = cosine_similarity(query_latent, tutor_latent).flatten()
            
            results = []
            for i, sim in enumerate(similarities):
                tutor = self.tutors[i].copy()
                norm_rating = tutor.get('rating', 0.0) / 5.0
                skill_rating = tutor.get('rating_from_same_skill_level_students', tutor.get('rating', 0.0)) / 5.0
                final_score = (0.5 * sim) + (0.2 * norm_rating) + (0.3 * skill_rating)
                tutor.update({'similarity': float(sim), 'score': float(f"{final_score:.4f}")})
                results.append(tutor)

            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_n]
        except Exception as e:
            logger.error(f"Recommendation Error: {e}")
            return []

if __name__ == "__main__":
    import numpy as np
    engine = RecommendationEngine()
    recs = engine.recommend_tutors("I want to learn Machine Learning")
    for r in recs: print(f"- {r['name']} ({r['score']})")
