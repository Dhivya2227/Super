"""
Train Passive Aggressive Classifier for fake job detection.
Run: python train_model.py
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# PAC is deprecated in sklearn 1.8+; use equivalent SGDClassifier
try:
    from sklearn.linear_model import SGDClassifier as _SGD
    import sklearn
    _ver = tuple(int(x) for x in sklearn.__version__.split('.')[:2])
    if _ver >= (1, 8):
        def PassiveAggressiveClassifier(**kwargs):
            kwargs.pop('tol', None); kwargs.pop('n_jobs', None)
            return _SGD(loss='hinge', penalty=None, learning_rate='pa1', eta0=1.0,
                       random_state=kwargs.get('random_state', 42),
                       max_iter=kwargs.get('max_iter', 1000))
    else:
        from sklearn.linear_model import PassiveAggressiveClassifier
except Exception:
    from sklearn.linear_model import PassiveAggressiveClassifier

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from preprocess import preprocess_text, combine_and_preprocess

# ── Paths ───────────────────────────────────────────────────────────────────
DATASET_PATH = os.path.join("dataset", "fake_job_postings.csv")
MODEL_PATH = "model.joblib"
VECTORIZER_PATH = "vectorizer.joblib"

def generate_synthetic_dataset():
    """Generate a synthetic dataset for training when real dataset is unavailable."""
    print("Generating synthetic training dataset...")
    
    genuine_templates = [
        "Software Engineer Python Django REST API AWS cloud services 3 years experience bachelor degree computer science",
        "Data Analyst SQL Python Excel Power BI reporting dashboard 2 years experience analytics",
        "Product Manager agile scrum roadmap stakeholder management 5 years experience MBA preferred",
        "DevOps Engineer Docker Kubernetes CI CD Jenkins terraform 4 years experience linux",
        "Frontend Developer React JavaScript TypeScript CSS HTML responsive design 3 years",
        "Machine Learning Engineer TensorFlow PyTorch deep learning NLP computer vision",
        "Business Analyst requirements gathering process improvement documentation communication",
        "Marketing Manager digital marketing SEO SEM social media campaigns analytics",
        "HR Manager recruitment onboarding payroll benefits compliance employment law",
        "Accountant financial reporting tax compliance audit reconciliation CPA preferred",
        "Sales Executive B2B enterprise software solutions client relationship management",
        "UX Designer user research wireframing prototyping Figma usability testing",
        "Cybersecurity Analyst threat detection incident response SIEM firewall networks",
        "Cloud Architect AWS Azure GCP infrastructure design scalability high availability",
        "Technical Writer documentation API reference user manuals software engineering background",
        "Project Manager PMP certified risk management budget planning delivery",
        "Database Administrator PostgreSQL MySQL performance tuning backup recovery",
        "Network Engineer Cisco routing switching VPN firewalls network security",
        "Quality Assurance Engineer selenium automation testing JIRA bug reporting",
        "Mobile Developer iOS Android Swift Kotlin React Native app development",
    ] * 50

    fake_templates = [
        "URGENT HIRING work from home earn 5000 per day no experience needed call now",
        "Make money online easy job no skills required 100000 salary immediate joining",
        "Data entry work from home earn unlimited income no qualification needed",
        "Part time job earn 50000 weekly send your details to gmail yahoo hotmail",
        "Lottery winner processing agent needed send bank details advance fee required",
        "Modeling acting casting call whatsapp us immediately good looking candidates",
        "Investment advisor earn passive income refer friends money multiplied",
        "Online tutor needed no experience earn per hour whatsapp number provided",
        "Home based business opportunity unlimited earning potential signup fee required",
        "Secret shopper mystery shopper needed send money order check cashing",
        "Government job guaranteed 100 percent job assistance pay registration fee",
        "Foreign company hiring Indians work abroad visa sponsorship send passport copy",
        "MLM network marketing downline upline join free training earn commission",
        "Crypto investment manager needed earn percentage no skills required",
        "Sugar mummy daddy connection job free registration earn dollars",
    ] * 66

    irrelevant_templates = [
        "Looking for house rent apartment 2bhk 3bhk furnished unfurnished contact",
        "Car for sale second hand vehicle good condition low mileage contact owner",
        "Matrimony bride groom wanted same caste vegetarian professional required",
        "Yoga classes meditation fitness trainer health wellness coaching available",
        "Tutoring home tuition all subjects maths science english spoken classes",
        "Travel agent tour packages honeymoon pilgrimage international domestic trips",
        "Astrology vastu consultation problem solution specialist contact immediately",
        "Property plot land sale purchase lease commercial residential area",
        "Medical equipment hospital furniture sale hospital bed wheelchair supplier",
        "Restaurant food delivery catering service events birthday corporate orders",
    ] * 100

    texts = genuine_templates + fake_templates + irrelevant_templates
    labels = (
        ['Genuine'] * len(genuine_templates) +
        ['Fake'] * len(fake_templates) +
        ['Irrelevant'] * len(irrelevant_templates)
    )

    df = pd.DataFrame({'text': texts, 'label': labels})
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

def load_dataset():
    """Load and preprocess the dataset."""
    if os.path.exists(DATASET_PATH):
        print(f"Loading dataset from {DATASET_PATH}...")
        try:
            df = pd.read_csv(DATASET_PATH)
            print(f"Dataset loaded: {len(df)} rows, columns: {list(df.columns)}")

            # Combine text fields
            text_cols = ['title', 'company_profile', 'description', 'requirements', 'benefits']
            available = [c for c in text_cols if c in df.columns]
            df['text'] = df[available].fillna('').astype(str).apply(lambda row: ' '.join(row), axis=1)

            # Map labels
            if 'fraudulent' in df.columns:
                df['label'] = df['fraudulent'].map({0: 'Genuine', 1: 'Fake'})
            else:
                df['label'] = 'Genuine'

            df.drop_duplicates(subset=['text'], inplace=True)
            df.dropna(subset=['text', 'label'], inplace=True)
            df = df[df['text'].str.strip() != '']
            print(f"After cleaning: {len(df)} rows")
            return df[['text', 'label']]
        except Exception as e:
            print(f"Error loading dataset: {e}")

    return generate_synthetic_dataset()

def preprocess_dataset(df):
    """Apply NLP preprocessing to dataset."""
    print("Preprocessing text...")
    df = df.copy()
    df['processed_text'] = df['text'].apply(preprocess_text)
    df = df[df['processed_text'].str.strip() != '']
    print(f"After preprocessing: {len(df)} rows")
    return df

def train_model():
    """Full training pipeline."""
    print("=" * 60)
    print("Fake Job Detection - Model Training")
    print("=" * 60)

    df = load_dataset()
    df = preprocess_dataset(df)

    print(f"\nClass distribution:\n{df['label'].value_counts()}")

    X = df['processed_text'].values
    y = df['label'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

    # TF-IDF Vectorization
    print("\nFitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Passive Aggressive Classifier
    print("Training Passive Aggressive Classifier...")
    model = PassiveAggressiveClassifier(
        C=1.0,
        max_iter=1000,
        random_state=42,
        tol=1e-3,
        n_jobs=-1
    )
    model.fit(X_train_tfidf, y_train)

    # Evaluation
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n{'='*60}")
    print(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"{'='*60}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model and vectorizer
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Vectorizer saved to: {VECTORIZER_PATH}")

    return model, vectorizer, accuracy

if __name__ == "__main__":
    os.makedirs("dataset", exist_ok=True)
    train_model()
