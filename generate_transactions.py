import pandas as pd
import numpy as np

class GenerateTransactions:
    def __init__(self):
        # Initialize dataframes
        self.transactions = pd.read_csv('data/Transactions.csv')
        self.orders = pd.read_csv('data/Orders.csv')

    def identify_missing_transactions(self):
        # Step 1: Identify orders that are missing in the Transactions dataset
        orders_with_transactions = self.transactions['OrderID'].unique()
        orders_without_transactions = self.orders[~self.orders['OrderID'].isin(orders_with_transactions)]
        return orders_without_transactions

    def generate_synthetic_transactions(self, orders_without_transactions):
        # Step 2: Generate synthetic transactions for the missing orders

        # Randomly assign payment methods based on existing distribution
        payment_methods = self.transactions['PaymentMethod'].value_counts(normalize=True).index.tolist()
        payment_method_probs = self.transactions['PaymentMethod'].value_counts(normalize=True).values

        # Generate random transaction dates similar to existing transactions
        transaction_dates = pd.to_datetime(self.transactions['TransactionDate'])
        min_date, max_date = transaction_dates.min(), transaction_dates.max()

        # Create synthetic transactions
        synthetic_transactions = []
        for _, row in orders_without_transactions.iterrows():
            order_id = row['OrderID']
            total_amount = row['TotalAmount']

            # Randomly assign a payment method
            payment_method = np.random.choice(payment_methods, p=payment_method_probs)

            # Generate a random transaction date within the range of existing transactions
            transaction_date = pd.to_datetime(np.random.uniform(min_date.value, max_date.value), unit='ns')

            # Create a new transaction entry
            synthetic_transactions.append({
                'TransactionID': self.transactions['TransactionID'].max() + len(synthetic_transactions) + 1,
                'OrderID': order_id,
                'PaymentMethod': payment_method,
                'Amount': total_amount,
                'TransactionDate': transaction_date
            })

        # Convert the synthetic transactions to a DataFrame
        synthetic_transactions_df = pd.DataFrame(synthetic_transactions)
        return synthetic_transactions_df

    def save_complete_transactions(self, synthetic_transactions_df, output_filepath):
        # Step 3: Combine synthetic and original transactions
        complete_transactions = pd.concat([self.transactions, synthetic_transactions_df], ignore_index=True)

        # Save the result to a CSV file
        complete_transactions.to_csv('data/Transactions.csv', index=False)
        print(f'>> Transactions.csv successfully updated!')

if __name__ == "__main__":
    # Instantiate the class
    transaction_generator = GenerateTransactions()

    # Identify missing transactions
    orders_without_transactions = transaction_generator.identify_missing_transactions()

    # Generate synthetic transactions for the missing orders
    synthetic_transactions_df = transaction_generator.generate_synthetic_transactions(orders_without_transactions)

    # Save the complete transactions to a file
    transaction_generator.save_complete_transactions(synthetic_transactions_df, 'data/Transactions.csv')