import re
import string
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Dataset Path
DATASET_PATH = r"D:\new\fake_job_detection\Balanced_FakeJob_Postings.csv"

# Download NLTK Data
def download_nltk_data():
    packages = ['stopwords', 'wordnet', 'punkt', 'omw-1.4']

    for package in packages:
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            print(f"Error downloading {package}: {e}")

download_nltk_data()

# Load Dataset
try:
    df = pd.read_csv(DATASET_PATH,encoding='latin1')

    print("Dataset Loaded Successfully")
    print("Dataset Shape:", df.shape)

except Exception as e:
    print("Error Loading Dataset:", e)

# Initialize NLP Tools
lemmatizer = WordNetLemmatizer()

try:
    STOPWORDS = set(stopwords.words('english'))

except Exception:
    STOPWORDS = set()

# Cleaning Functions
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', str(text))

def remove_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(' ', str(text))

def remove_emails(text):
    return re.sub(r'\S+@\S+', ' ', str(text))

def remove_phone_numbers(text):
    return re.sub(
        r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',
        ' ',
        str(text)
    )

def remove_punctuation(text):
    return text.translate(
        str.maketrans('', '', string.punctuation)
    )

def remove_special_characters(text):
    return re.sub(r'[^a-zA-Z\s]', ' ', str(text))

def remove_extra_spaces(text):
    return ' '.join(text.split())

def tokenize_and_lemmatize(text):

    try:
        tokens = word_tokenize(text.lower())

    except Exception:
        tokens = text.lower().split()

    clean_tokens = [
        lemmatizer.lemmatize(token)

        for token in tokens

        if token not in STOPWORDS
        and len(token) > 2
        and token.isalpha()
    ]

    return ' '.join(clean_tokens)

# Main Preprocessing Function
def preprocess_text(text):

    if pd.isna(text):
        return ''

    text = str(text)

    text = remove_html_tags(text)
    text = remove_urls(text)
    text = remove_emails(text)
    text = remove_phone_numbers(text)

    text = text.lower()

    text = remove_special_characters(text)
    text = remove_punctuation(text)
    text = remove_extra_spaces(text)

    text = tokenize_and_lemmatize(text)

    return text

# Combine Important Columns
def combine_and_preprocess(row):

    important_columns = [
        'title',
        'company_profile',
        'description',
        'requirements',
        'benefits'
    ]

    combined_text = ' '.join([
        str(row[col])

        for col in important_columns

        if col in row and str(row[col]) != 'nan'
    ])

    return preprocess_text(combined_text)

# Handle Null Values
df = df.fillna('')

# Apply Preprocessing
print("\nPreprocessing Started...\n")

df['cleaned_text'] = df.apply(
    combine_and_preprocess,
    axis=1
)

print("\nPreprocessing Completed Successfully\n")

# Display Output
print(
    df[
        [
            'cleaned_text',
            'fraudulent'
        ]
    ].head()
)

# Save Cleaned Dataset
OUTPUT_PATH = r"D:\new\fake_job_detection\cleaned_fake_jobs.csv"

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"\nCleaned Dataset Saved At:\n{OUTPUT_PATH}")

# Real-Time Prediction Preprocessing
def preprocess_for_prediction(
    title,
    description,
    requirements,
    skills=''
):

    combined = f"""
    {title}
    {description}
    {requirements}
    {skills}
    """

    return preprocess_text(combined)

# Test Prediction Preprocessing
sample_text = preprocess_for_prediction(
    title="Python Developer",

    description="""
    Looking for experienced Python developer
    with Machine Learning skills.
    Earn high salary immediately.
    """,

    requirements="""
    Python, ML, SQL, NLP
    """,

    skills="Python Machine Learning SQL"
)

print("\nSample Preprocessed Prediction Text:\n")
print(sample_text)