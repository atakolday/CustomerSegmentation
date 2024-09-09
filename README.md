
# Customer Behavior Data Processing and Analysis Pipeline

This project implements a comprehensive data processing and analysis pipeline to handle customer behavior, generate synthetic transactions and reviews, perform text and sentiment analysis, and create geolocation-based heatmaps. The workflow is modular, with each stage encapsulated in a separate Python class.

## Project Overview

The pipeline consists of the following steps:
1. **Data Cleaning (DataClean)**: Cleans and processes the raw customer behavior data.
2. **Generate Transactions (GenerateTransactions)**: Generates synthetic transactions for orders that are missing transaction data.
3. **Generate Reviews (GenerateReviews)**: Generates synthetic customer reviews and ratings for delivered orders.
4. **Generate Tracking (GenerateTracking)**: Generates tracking information for customer orders based on their status.
5. **Text Processing (TextProcessing)**: Preprocesses reviews, performs sentiment analysis, topic modeling (LDA), and clustering (KMeans) on customer reviews.
6. **Generate Heatmaps (HeatmapGenerator)**: Creates geolocation-based heatmaps for customers by clusters.

## Project Workflow

The entire pipeline can be executed sequentially by running the `main.py` file, which handles each step in order. 

### Workflow:
1. **Data Cleaning**: Cleans the `Orders.csv` data and customer behavior data.
2. **Generate Transactions**: Identifies orders missing transaction records and generates synthetic transactions.
3. **Generate Reviews**: Generates synthetic reviews and ratings for the orders.
4. **Generate Tracking**: Generates tracking information for each order based on their status.
5. **Text Processing**: Preprocesses text reviews, performs sentiment analysis, topic modeling, and clustering.
6. **Generate Heatmaps**: Generates heatmaps based on the location data of the customers by cluster.

## Project Structure

```bash
├── data_clean.py                # Handles data cleaning and preprocessing.
├── generate_transactions.py     # Generates synthetic transactions for orders.
├── generate_reviews.py          # Generates synthetic reviews and ratings for orders.
├── generate_tracking.py         # Generates tracking information for orders.
├── text_processing.py           # Preprocesses reviews and performs sentiment analysis, LDA, and clustering.
├── heatmap_generator.py         # Generates geolocation-based heatmaps for clusters.
├── main.py                      # Orchestrates the entire workflow.
├── data/                        # Folder containing raw data files.
│   ├── Orders.csv
│   ├── Transactions.csv
│   ├── Tracking.csv
├── data_test/                   # Folder where processed data and output files are saved.
│   ├── Orders_Master.csv
│   ├── Orders_Segmented.csv
│   ├── Complete_Transactions.csv
│   ├── heatmap_cluster_X.html   # Heatmaps generated for each cluster.
└── README.md                    # Project documentation (this file).
```

## Dependencies

Ensure you have the following libraries installed before running the project:

```bash
pip install pandas numpy geopy tqdm nltk sklearn folium
```

Additionally, you need to download the necessary NLTK datasets for tokenization, lemmatization, and sentiment analysis. This will be handled in the `TextProcessing` class.

## How to Run the Project

### 1. Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```

### 2. Install the dependencies:

```bash
pip install -r requirements.txt
```

You may create a `requirements.txt` file to manage dependencies:

```bash
pandas
numpy
geopy
tqdm
nltk
sklearn
folium
```

### 3. Run the pipeline:

```bash
python main.py
```

This will execute the entire workflow as described above, including generating synthetic data, text processing, sentiment analysis, and generating heatmaps.

### 4. View the Heatmaps:

Once the pipeline finishes, the heatmaps for each customer cluster will be saved in the `data_test/` folder as `.html` files, which you can open in your browser.

### Example Output Files:
- `Orders_Master.csv`: Cleaned and processed orders data.
- `Complete_Transactions.csv`: The complete transactions file with synthetic transactions.
- `Orders_Segmented.csv`: Orders data with segmented clusters.
- `heatmap_cluster_X.html`: Geolocation-based heatmaps for each cluster.

## Customization

- **Data Input**: Modify the input CSV files in the `data/` folder as needed.
- **Clustering**: You can modify the number of clusters for KMeans or topics for LDA in the `TextProcessing` class.
- **Heatmap Settings**: The `HeatmapGenerator` class allows customization of heatmap parameters such as the radius, blur, and gradient.

## Future Improvements

- Add functionality to automatically download missing data.
- Optimize the geocoding process by using caching for previously geocoded locations.
- Implement additional clustering algorithms for customer segmentation.
- Add interactive features to the heatmaps for better visualization.

## Contributing

If you have any suggestions or improvements, feel free to open an issue or submit a pull request. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or inquiries, feel free to reach out:
- Email: your-email@example.com
- GitHub: [yourusername](https://github.com/yourusername)
