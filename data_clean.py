import pandas as pd
import numpy as np
from pathlib import Path
import phonenumbers
from decimal import Decimal
from tqdm import tqdm

class DataClean:
    def __init__(self):
        # Load all necessary dataframes during initialization
        self.orders = pd.read_csv('data/Orders.csv')
        self.order_items = pd.read_csv('data/Order_Items.csv')
        self.products = pd.read_csv('data/Products.csv')
        self.customers = pd.read_csv('data/Customers.csv')
        self.transactions = pd.read_csv('data/Transactions.csv')
        self.behavioral_data = pd.read_csv('data/Behavioral_Data.csv')

        # Merge customer and behavioral data
        self.customer_behavior = self.customers.merge(self.behavioral_data, on='CustomerID')
        
        # Empty initialization to be filled out when this code is run
        self.orders_master = None

    # Function to format phone numbers
    def format_phone_number(self, number):
        try:
            if number.startswith('001'):
                number = number.replace('001', '+1', 1)
            parsed_number = phonenumbers.parse(number, "US")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except phonenumbers.NumberParseException:
            return number

    # Function to format age
    def format_age(self, age):
        if 'over' in age:
            return age.split(' ')[0] + '+'
        else:
            parts = age.split(' ')
            return f"{parts[0]}-{parts[2]}"
        
    def fill_purhcases(self, data):
        orderitem_id = self.full_orders['OrderItemID'].max() # last OrderItemID in the data
        order_id = self.full_orders['OrderID'].max() # last OrderID in the data

        # Creating new purchases for the orders and order_items based on the behavioral_data
        new_purchases = []
        for ix in data.CustomerID.unique():
            df = data[data['CustomerID'] == ix]
            
            for _, row in df.iterrows():

                orderitem_id += 1
                order_id += 1
                
                new_purchases.append({
                    'OrderItemID': orderitem_id,
                    'OrderID': orderitem_id,
                    'ProductID': row['ProductID'],
                    'Price': np.nan if pd.isna(row['Price']) else row['Price'],
                    'Quantity': 1,
                    'CustomerID': ix,
                    'OrderDate': row['Timestamp'][:19],
                    'Count': 1,
                    'TotalAmount': np.nan if pd.isna(row['Price']) else row['Price'],
                    'Status': np.random.choice(['Shipped', 'Delivered', 'In Transit'])
                })

        new_purchase_df = pd.DataFrame(new_purchases)
        return pd.concat([self.full_orders, new_purchase_df], ignore_index=True)

    def generate_prices(self):
        print("\nGenerating and filling prices...")

        # Step 1: Fill missing prices for products that have existing prices
        existing_prices = self.orders_master.dropna(subset=['Price']).groupby('Name')['Price'].first()
        self.orders_master['Price'] = self.orders_master.apply(
            lambda row: existing_prices.get(row['Name'], row['Price']), axis=1
        )

        # Step 2: Generate synthetic prices for remaining missing prices
        min_price, max_price = self.orders_master['Price'].min(), self.orders_master['Price'].max()
        self.orders_master['Price'] = self.orders_master.apply(
            lambda row: np.random.uniform(min_price, max_price) if pd.isnull(row['Price']) else row['Price'],
            axis=1
        )

        # Step 3: Ensure Price and Quantity are numeric
        self.orders_master['Price'] = self.orders_master['Price'].apply(lambda x: Decimal(str(round(x, 2))))
        self.orders_master['Quantity'] = self.orders_master['Quantity'].apply(lambda x: Decimal(str(round(x, 2))))

        # Step 4: Recalculate TotalAmount for each OrderID
        total_amount_per_order = self.orders_master.groupby('OrderID').apply(
            lambda group: (group['Price'] * group['Quantity']).sum()
        )
        self.orders_master['TotalAmount'] = self.orders_master['OrderID'].map(total_amount_per_order)

        # Step 5: Run checks on prices, quantities, and total amounts
        self.run_price_checks()

    def run_price_checks(self):
        first_check, second_check = [], []

        for i in tqdm(list(self.orders_master.OrderID), desc=' > Running checks...'):
            data = self.orders_master.loc[self.orders_master.OrderID == i]

            if sum(data.Price.isna()) > 0:
                try:
                    transaction = Decimal(str(self.transactions.loc[self.transactions.OrderID == i].Amount.iloc[0]))
                    transaction_amount = max(transaction, data.TotalAmount.iloc[0])
                except IndexError:
                    continue

                existing_total = sum((data['Price'] * data['Quantity']).dropna())
                nan_data = data.loc[data.Price.isna()]
                price_px = (transaction_amount - existing_total) / nan_data.Quantity.iloc[0]

                # Update missing price
                self.orders_master.at[nan_data.index[0], 'Price'] = price_px
                data.at[nan_data.index[0], 'Price'] = price_px

                # Update TotalAmount for the order
                for ix in data.index:
                    self.orders_master.at[ix, 'TotalAmount'] = transaction_amount
                    data.at[ix, 'TotalAmount'] = transaction_amount

            # First check: ensure count value matches the number of entries
            if data.Count.iloc[0] != len(data.index):
                first_check.append(i)

            # Second check: ensure price * quantity = total amount
            if sum((data['Price']) * data['Quantity']) != data.TotalAmount.iloc[0]:
                second_check.append(i)

        # Reporting results of the checks
        if len(first_check) > 0:
            print('Mismatch detected between "Count" and the number of entries for the following CustomerIDs:')
            for ix in first_check:
                print(f' - {self.orders_master.loc[self.orders_master.OrderID == ix]["CustomerID"].iloc[0]}')

        if len(second_check) > 0:
            print('Missing price information could not be resolved for the following ProductIDs:')
            for ix in second_check:
                print(f' - {self.orders_master.loc[self.orders_master.OrderID == ix]["ProductID"].iloc[0]}')
        else:
            print(' > All checks cleared!\n')
    
    # Function to clean customer behavior data
    def clean_customer_behavior(self):
        # Clean up and reformat the 'Phone' column with the custom function
        self.customer_behavior['Phone'] = self.customer_behavior['Phone'].apply(self.format_phone_number)

        # Reformat the Age column with the custom function
        self.customer_behavior['Age'] = self.customer_behavior['Age'].apply(self.format_age)
        self.customer_behavior['Age'] = self.customer_behavior['Age'].astype(str)

        self.customer_behavior['Gender'] = self.customer_behavior['Gender'].map({'female': 'F', 'male': 'M'})

        # Convert columns that include dates into datetime format for easier manipulation
        self.customer_behavior['Timestamp'] = pd.to_datetime(self.customer_behavior['Timestamp'])

        education_mapping = {
            'bachelors_degree': "Bachelor's Degree",
            'graduate_or_professional_degree': 'Graduate or Professional Degree',
            'high_school_graduate': 'High School Graduate',
            'less_than_high_school_diploma': 'Less than High School Diploma',
            'some_college_or_associates_degree': "Some College or Associate's Degree"
        }

        industry_mapping = {
            'agriculture_forestry_fishing_mining': 'Agriculture, Forestry, Fishing, Mining',
            'arts_entertainment_recreation_accommodation_food_services': 'Arts, Entertainment, Recreation, Accommodation, Food Services',
            'construction': 'Construction',
            'educational_services_health_care_social_assistance': 'Educational Services, Health Care, Social Assistance',
            'finance_insurance_real_estate': 'Finance, Insurance, Real Estate',
            'information': 'Information',
            'manufacturing': 'Manufacturing',
            'other_services': 'Other Services',
            'professional_scientific_management': 'Professional, Scientific, Management',
            'public_administration': 'Public Administration',
            'retail_trade': 'Retail Trade',
            'transportation_warehousing_utilities': 'Transportation, Warehousing, Utilities',
            'wholesale_trade': 'Wholesale Trade'
        }

        occuptation_mapping = {
            'management_business_science_arts': 'Management, Business, Science, and Arts',
            'natural_resources_construction_maintenance': 'Natural Resources, Construction, and Maintenance',
            'production_transportation_material_moving': 'Production, Transportation, and Material Moving',
            'sales_and_office_occupations': 'Sales and Office Occupations',
            'service_occupations': 'Service Occupations'
        }

        self.customer_behavior.Education = self.customer_behavior.Education.map(education_mapping)
        self.customer_behavior.EmploymentStatus = self.customer_behavior.EmploymentStatus.map({'unemployed':0, 'employed':1})
        self.customer_behavior.Industry = self.customer_behavior.Industry.map(industry_mapping)
        self.customer_behavior.Occupation = self.customer_behavior.Occupation.map(occuptation_mapping)

        # Save updated dataframe to files
        self.save_data('customer_behavior')

    # Main function to clean customer behavior data
    def clean_orders_master(self):

        ### CREATING COMPLETED ORDER INFORMATION
        self.full_orders = self.order_items.merge(self.orders, on='OrderID')

        # Apply mappings for the Status column to be uniform with the Tracking data
        status_mapping = {
            'Completed': 'Delivered',
            'Pending': 'In Transit',
            'Shipped': 'Shipped'}

        self.full_orders['Status'] = self.full_orders['Status'].map(status_mapping).fillna(self.full_orders['Status'])

        # all purchases from BehavioralData.csv that do not exist in the Orders and Order_Items files
        purchased = self.behavioral_data.merge(self.products, on='ProductID').loc[lambda df: df['ActionType'] == 'purchase']
        self.updated_orders = self.fill_purhcases(purchased) # updated with filled out price information
        
        self.orders_master = self.updated_orders.merge(self.products, on=['ProductID', 'Price']) # finally, add the product information

        self.generate_prices() # run to generate synthetic prices

        self.orders_master = self.orders_master.sort_values(by='OrderItemID')
        
        # Save the updated dataframe to files
        self.save_data('orders_master')

    def save_data(self, data_name):
        # Create a dictionary of your instance variables (orders_master, customer_behavior, etc.)
        dfs_dict = {
            'orders_master': [self.orders_master, ['orders', 'order_items', 'products']],
            'customer_behavior': [self.customer_behavior, ['customers', 'behavioral_data']]
        }
        
        if data_name not in dfs_dict:
            raise KeyError(f"No data found for {data_name}")

        # Unpack the dataframe and related tables from the dictionary
        df_main, df_related_names = dfs_dict[data_name]

        for df_name in df_related_names:
            # Save each related dataframe
            df = getattr(self, df_name)
            df.to_csv(f'data/{df_name.title()}.csv', index=False)
            print(f">> {df_name.title()}.csv generated!")

        # Save the main dataframe
        df_main.to_csv(f'data/{data_name.title()}.csv', index=False)
        print(f">> {data_name.title()}.csv generated!")

    # Additional checks or logic (from your original file) can go here

if __name__ == "__main__":
    cleaner = DataClean()
    
    cleaner.clean_customer_behavior()
    cleaner.clean_orders_master()