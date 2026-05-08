"""
Real-time prediction module for fake job detection.
"""
import os
import warnings
import joblib
import numpy as np
from preprocess import preprocess_for_prediction

# Suppress deprecation warnings
warnings.filterwarnings('ignore', category=FutureWarning)

MODEL_PATH = "model.joblib"
VECTORIZER_PATH = "vectorizer.joblib"

_model = None
_vectorizer = None

def load_model_and_vectorizer():
    """Load model and vectorizer, training if not found."""
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            print("Model not found. Training now...")
            from train_model import train_model
            _model, _vectorizer, _ = train_model()
        else:
            _model = joblib.load(MODEL_PATH)
            _vectorizer = joblib.load(VECTORIZER_PATH)
    return _model, _vectorizer

def predict_job(title, description, requirements='', skills=''):
    """
    Predict whether a job posting is Genuine, Fake, or Irrelevant.
    
    Returns:
        dict: {
            'prediction': str,       # 'Genuine', 'Fake', 'Irrelevant'
            'confidence': float,     # 0.0 - 1.0
            'risk_level': str,       # 'Low', 'Medium', 'High'
            'details': dict          # per-class scores
        }
    """
    model, vectorizer = load_model_and_vectorizer()

    # Preprocess text
    processed = preprocess_for_prediction(title, description, requirements, skills)
    if not processed.strip():
        return {
            'prediction': 'Irrelevant',
            'confidence': 0.5,
            'risk_level': 'Medium',
            'details': {}
        }

    # Vectorize
    X = vectorizer.transform([processed])

    # Predict
    prediction = model.predict(X)[0]

    # Confidence via decision function
    try:
        decision = model.decision_function(X)[0]
        if hasattr(decision, '__len__'):
            # Multi-class
            scores = np.array(decision)
            exp_scores = np.exp(scores - scores.max())
            probs = exp_scores / exp_scores.sum()
            classes = model.classes_
            details = {cls: float(p) for cls, p in zip(classes, probs)}
            confidence = float(probs.max())
        else:
            # Binary
            confidence = float(abs(decision)) / (1 + float(abs(decision)))
            details = {prediction: confidence}
    except Exception:
        confidence = 0.75
        details = {prediction: confidence}

    # Risk level
    if prediction == 'Genuine':
        risk_level = 'Low' if confidence > 0.8 else 'Medium'
    elif prediction == 'Fake':
        risk_level = 'High' if confidence > 0.7 else 'Medium'
    else:
        risk_level = 'Medium'

    return {
        'prediction': prediction,
        'confidence': round(confidence, 4),
        'risk_level': risk_level,
        'details': details
    }

def predict_batch(jobs_list):
    """
    Predict multiple job postings at once.
    
    Args:
        jobs_list: list of dicts with keys: title, description, requirements, skills
    
    Returns:
        list of prediction dicts
    """
    model, vectorizer = load_model_and_vectorizer()
    results = []
    for job in jobs_list:
        result = predict_job(
            job.get('title', ''),
            job.get('description', ''),
            job.get('requirements', ''),
            job.get('skills', '')
        )
        results.append(result)
    return results

def get_risk_explanation(prediction, confidence):
    """Return human-readable explanation of prediction."""
    explanations = {
        'Genuine': [
            "✅ This job posting appears to be legitimate.",
            "The description contains professional language and clear requirements.",
            "Company information and job details appear credible.",
        ],
        'Fake': [
            "🚨 This job posting shows signs of fraud.",
            "Warning: Contains suspicious patterns common in fake postings.",
            "Exercise extreme caution before applying or sharing personal information.",
        ],
        'Irrelevant': [
            "⚠️ This posting may not be a valid job advertisement.",
            "Content appears unrelated to professional employment.",
            "This may be spam, an advertisement, or misdirected posting.",
        ]
    }
    base = explanations.get(prediction, ["Unable to determine posting authenticity."])
    
    if confidence > 0.9:
        confidence_note = f"Model confidence: Very High ({confidence*100:.1f}%)"
    elif confidence > 0.75:
        confidence_note = f"Model confidence: High ({confidence*100:.1f}%)"
    elif confidence > 0.6:
        confidence_note = f"Model confidence: Moderate ({confidence*100:.1f}%)"
    else:
        confidence_note = f"Model confidence: Low ({confidence*100:.1f}%) — manual review recommended"
    
    return base + [confidence_note]

def get_red_flags(title, description, requirements):
    """Detect specific red flags in job text."""
    red_flags = []
    combined = f"{title} {description} {requirements}".lower()
    
    patterns = {
        "Unrealistic salary": ["earn lakhs", "earn crores", "unlimited income", "guaranteed income", "earn per day"],
        "Urgency tactics": ["urgent hiring", "immediate joining", "apply now", "limited seats", "hurry"],
        "No experience needed": ["no experience required", "no qualification", "freshers only all welcome"],
        "Suspicious contact": ["whatsapp us", "call immediately", "send details to gmail", "yahoo", "hotmail"],
        "Fee required": ["registration fee", "advance fee", "training fee", "deposit required", "pay to join"],
        "Vague description": ["work from home", "part time earn", "easy money", "online job"],
        "Personal info request": ["send passport", "bank details", "aadhar number", "pan card required"],
    }
    
    for flag, keywords in patterns.items():
        if any(kw in combined for kw in keywords):
            red_flags.append(flag)
    
    return red_flags
