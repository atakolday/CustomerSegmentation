import pandas as pd
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

import warnings

# Suppress RuntimeWarnings due to an inconsistency with packages loaded from incompatible origins, no workaround works
warnings.filterwarnings("ignore", category=RuntimeWarning)

class TextProcessing:
    def __init__(self):
        # Load the data
        self.orders_master = pd.read_csv('data/Orders_Master.csv')

        # Initialize the lemmatizer and stopwords list
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.tfidf_matrix = None
        self.tfidf_df = None

    def check_reviews(self):
        # If the "Reviews" column doesn't exist, run generate_reviews and reload the data
        if "Reviews" not in self.orders_master.columns:
            import generate_reviews
            self.orders_master = pd.read_csv('data/Orders_Master.csv')

    def download_nltk_data(self):
        # Download necessary NLTK data
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('vader_lexicon')

    def preprocess_text(self, review):
        # Remove special characters and numbers
        review = re.sub(r'[^a-zA-Z\s]', '', review)
        
        # Convert to lowercase
        review = review.lower()
        
        # Tokenize
        words = word_tokenize(review)
        
        # Remove stopwords and lemmatize words
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        
        # Join words back into a single string
        return ' '.join(words)

    def apply_preprocessing(self):
        # Apply preprocessing to the reviews
        self.orders_master['CleanedReviews'] = self.orders_master['Reviews'].apply(
            lambda x: self.preprocess_text(x) if isinstance(x, str) else x
        )

    def extract_features(self):
        # Initialize TF-IDF Vectorizer
        tfidf = TfidfVectorizer(max_features=1000)  # Use the top 1000 words
        
        # Transform the cleaned reviews into TF-IDF matrix
        self.tfidf_matrix = tfidf.fit_transform(self.orders_master['CleanedReviews'].dropna())

        # Convert to DataFrame for easier inspection
        self.tfidf_df = pd.DataFrame(self.tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
        print(">> TF-IDF feature extraction completed.")

    def sentiment_analysis(self):
        # Initialize VADER sentiment analyzer
        sia = SentimentIntensityAnalyzer()

        # Function to calculate sentiment scores
        def get_sentiment(review):
            return sia.polarity_scores(review)

        # Apply sentiment analysis
        self.orders_master['Sentiment'] = self.orders_master['CleanedReviews'].apply(
            lambda x: get_sentiment(x) if isinstance(x, str) else x
        )

        # Extract sentiment scores (positive, negative, neutral, compound)
        sentiment_scores = pd.json_normalize(self.orders_master['Sentiment'])

        # Combine with the original data
        self.orders_master = pd.concat([self.orders_master, sentiment_scores], axis=1)
        print(">> Sentiment analysis completed.")

    def topic_modeling(self):
        # Initialize LDA with 5 topics
        lda = LatentDirichletAllocation(n_components=5, random_state=42)
        
        # Fit the LDA model on the TF-IDF matrix
        lda.fit(self.tfidf_matrix)
        print(">> LDA topic modeling completed.")

    def clustering(self):
        # Initialize K-Means clustering
        kmeans = KMeans(n_init=10, n_clusters=5, random_state=42)

        # Filter rows where 'cleaned_reviews' is not NaN
        filtered_data = self.orders_master.dropna(subset=['CleanedReviews']).copy()

        # Fit the model on the TF-IDF matrix for filtered data only
        kmeans.fit(self.tfidf_matrix)

        # Assign clusters to the filtered data
        filtered_data['Cluster'] = kmeans.labels_

        # Merge the filtered data with the original data to preserve other rows
        self.orders_master = self.orders_master.merge(filtered_data[['Cluster']], left_index=True, right_index=True, how='left')
        print(">> K-Means clustering completed.")

    def save_output(self):
        # Save the result to a CSV file
        self.orders_master.to_csv('data/Orders_Segmented.csv', index=False)
        print("\n>> Orders_Segmented.csv successfully created!")

if __name__ == "__main__":
    # Instantiate the class
    text_processor = TextProcessing()

    # Step 1: Ensure NLTK data is downloaded
    text_processor.download_nltk_data()

    # Step 2: Check if reviews need to be generated
    text_processor.check_reviews()

    # Step 3: Preprocess the reviews
    text_processor.apply_preprocessing()

    # Step 4: Extract features using TF-IDF
    text_processor.extract_features()

    # Step 5: Perform sentiment analysis
    text_processor.sentiment_analysis()

    # Step 6: Perform topic modeling using LDA
    text_processor.topic_modeling()

    # Step 7: Perform K-Means clustering
    text_processor.clustering()

    # Step 8: Save the output to a file
    text_processor.save_output()