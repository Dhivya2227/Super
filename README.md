# 🧠 RecruitAI — Detection of Fake and Irrelevant Job Postings
### Using Passive Aggressive Classifier Model

> An end-to-end AI-powered recruitment verification platform built entirely with **Python** and **Streamlit**

---

## 📌 Project Overview

RecruitAI is a smart recruitment platform that uses Machine Learning to automatically detect **fake, fraudulent, and irrelevant job postings** in real-time. The system employs a **Passive Aggressive Classifier (PAC)** trained on NLP-preprocessed text features to classify job postings as:

- ✅ **Genuine** — Legitimate job posting
- 🚨 **Fake** — Fraudulent or spam posting  
- ⚠️ **Irrelevant** — Non-job content

---

## 🎯 Objectives

1. Detect fraudulent job postings using ML classification
2. Protect job seekers from scams and data theft
3. Provide recruiters with AI-powered job authenticity feedback
4. Deliver real-time predictions with confidence scores
5. Build a complete multi-role recruitment platform in pure Python/Streamlit

---

## 🏗️ Architecture

```
RecruitAI/
├── app.py                    # Main Streamlit application entry point
├── database.py               # SQLite database operations & models
├── preprocess.py             # NLP text preprocessing pipeline (NLTK)
├── train_model.py            # Model training script (PAC + TF-IDF)
├── predict.py                # Real-time prediction module
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── model.joblib              # Trained PAC model (generated)
├── vectorizer.joblib         # TF-IDF vectorizer (generated)
├── recruitment.db            # SQLite database (generated)
├── pages/
│   ├── login.py              # Authentication pages
│   ├── admin.py              # Admin dashboard
│   ├── recruiter.py          # Recruiter module
│   └── seeker.py             # Job seeker module
├── utils/
│   └── helpers.py            # Shared UI utilities
├── dataset/
│   └── fake_job_postings.csv # Training dataset (optional)
└── uploads/                  # Resume uploads (generated)
```

---

## 🔬 ML Workflow

```
Raw Text → Preprocessing → TF-IDF → PAC Model → Prediction
                                                      │
Job Text ──► HTML removal ──► Tokenization ──► Feature Vector ──► Genuine/Fake/Irrelevant
             URL cleaning      Stopword removal   (15k features)    + Confidence Score
             Lowercasing       Lemmatization
             Punctuation       Special chars
             removal           removal
```

### Preprocessing Steps (NLTK)
1. HTML tag removal
2. URL & email removal  
3. Lowercase conversion
4. Special character removal
5. Punctuation removal
6. Tokenization
7. Stopword removal
8. Lemmatization
9. Duplicate removal

### Model: Passive Aggressive Classifier
- **Algorithm**: Online learning, large-margin classifier
- **Vectorizer**: TF-IDF (15,000 features, unigrams + bigrams)
- **Training**: 80/20 train-test split
- **Evaluation**: Accuracy, F1-score, confusion matrix

---

## 👥 User Roles

| Role | Login | Key Features |
|------|-------|-------------|
| 🛡️ Admin | admin@recruit.ai / Admin@123 | Full control, analytics, user management |
| 🏢 Recruiter | recruiter@demo.com / Recruiter@123 | Post jobs, manage applicants |
| 🔍 Job Seeker | seeker@demo.com / Seeker@123 | Search jobs, apply, track |

---

## ✨ Features

### Admin Module
- 📊 Real-time dashboard with Plotly charts
- 👥 User & recruiter management
- 💼 Job monitoring with fake detection
- 🤖 ML prediction logs
- 📥 CSV report downloads
- 📈 Advanced analytics (employment types, locations, confidence distribution)

### Recruiter Module
- 🏢 Company profile management
- ➕ AI-analyzed job posting
- ✏️ Edit & re-analyze jobs
- 📋 Applicant management with status tracking
- 📊 Job performance analytics

### Job Seeker Module
- 🔍 Intelligent search with advanced filters
- ⭐ AI-powered recommendations (skill-based)
- 📝 One-click job application with resume upload
- 💾 Job bookmarking
- 📋 Application status tracking

### ML Predictor (Sandbox)
- 🧪 Real-time test of any job text
- 📊 Per-class probability breakdown
- 🚩 Red flag detection (suspicious patterns)
- 📝 Human-readable explanations

---

## 🚀 Installation & Setup

### 1. Clone / Download the project
```bash
git clone <repo-url>
cd fake_job_detection
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Add your dataset
Place `fake_job_postings.csv` in the `dataset/` folder.  
If not provided, a synthetic dataset will be generated automatically.

### 5. Train the ML model
```bash
python train_model.py
```
This creates `model.joblib` and `vectorizer.joblib`.

### 6. Run the application
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📦 Dataset

**Kaggle dataset**: [Real or Fake? Fake Job Posting Prediction](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction)

| Column | Description |
|--------|-------------|
| job_id | Unique identifier |
| title | Job title |
| location | Job location |
| description | Full job description |
| requirements | Job requirements |
| company_profile | Company information |
| benefits | Benefits offered |
| fraudulent | **Target**: 0=Genuine, 1=Fake |

Text columns combined for NLP: `title + company_profile + description + requirements + benefits`

---

## 🌐 Streamlit Cloud Deployment

1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set main file: `app.py`
5. Add secrets if needed
6. Deploy!

---

## 🧪 Testing

### Test ML Model
```bash
python train_model.py
```

### Test Predictions
```python
from predict import predict_job

result = predict_job(
    title="Senior Python Developer",
    description="We are looking for an experienced developer...",
    requirements="5+ years Python, AWS, Docker"
)
print(result)
# {'prediction': 'Genuine', 'confidence': 0.94, 'risk_level': 'Low', ...}
```

### Test Database
```python
from database import init_db, get_stats
init_db()
print(get_stats())
```

---

## 🔮 Future Enhancements

- [ ] BERT/transformer-based classification
- [ ] Email notification for job status updates
- [ ] Company verification with external APIs
- [ ] Resume parsing and skill extraction
- [ ] Job expiry and auto-archival
- [ ] Multi-language support
- [ ] Mobile-responsive PWA
- [ ] REST API layer for integrations
- [ ] A/B testing for ML models
- [ ] Feedback loop for model improvement

---

## 📄 License

MIT License — Free for educational and commercial use.

---

*Built with ❤️ using Python + Streamlit | Passive Aggressive Classifier | NLTK | SQLite*
