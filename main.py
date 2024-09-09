from data_clean import DataClean
from generate_transactions import GenerateTransactions
from generate_reviews import GenerateReviews
from generate_tracking import GenerateTracking
from nlp_segmentation import TextProcessing
from heatmap_generator import HeatmapGenerator

def main():
    # Step 1: Run DataClean
    print("\n>>> Running DataClean...\n")
    cleaner = DataClean()
    cleaner.clean_customer_behavior()
    cleaner.clean_orders_master()

    # Step 2: Run GenerateTransactions
    print("\n>>> Running GenerateTransactions...")
    transaction_generator = GenerateTransactions()
    orders_without_transactions = transaction_generator.identify_missing_transactions()  # Identify missing transactions
    synthetic_transactions_df = transaction_generator.generate_synthetic_transactions(orders_without_transactions)  # Generate synthetic transactions
    transaction_generator.save_complete_transactions(synthetic_transactions_df, 'data/Complete_Transactions.csv')  # Save the complete transactions

    # Step 3: Run GenerateReviews
    print("\n>>> Running GenerateReviews...")
    review_generator = GenerateReviews()
    review_generator.generate_reviews()  # Generate reviews

    # Step 4: Run GenerateTracking
    print("\n>>> Running GenerateTracking...")
    tracking_generator = GenerateTracking()
    tracking_generator.generate_tracking()  # Generate tracking information

    # Step 5: Run TextProcessing
    print("\n>>> Running TextProcessing...")
    text_processor = TextProcessing()
    text_processor.download_nltk_data()  # Ensure all NLTK data is downloaded
    text_processor.check_reviews()  # Ensure reviews are generated
    text_processor.apply_preprocessing()  # Preprocess reviews
    text_processor.extract_features()  # Extract TF-IDF features
    text_processor.sentiment_analysis()  # Perform sentiment analysis
    text_processor.topic_modeling()  # Perform topic modeling using LDA
    text_processor.clustering()  # Perform KMeans clustering
    text_processor.save_output()  # Save the output

    # Step 6: Run HeatmapGenerator
    print("\n>>> Running HeatmapGenerator...")
    heatmap_generator = HeatmapGenerator()
    heatmap_generator.preprocess_data()  # Preprocess data
    heatmap_generator.geocode_locations()  # Geocode locations
    heatmap_generator.create_heatmaps()  # Generate and save heatmaps

if __name__ == "__main__":
    main()