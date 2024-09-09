import pandas as pd

class GenerateTracking:
    def __init__(self):
        self.orders_master = pd.read_csv('data/Orders_Master.csv')
        self.tracking = pd.read_csv('data/Tracking.csv')

    def generate_tracking(self):
        # Merge orders_master with tracking on 'OrderID'
        merged_df = pd.merge(
            self.tracking, 
            self.orders_master[['OrderID', 'Status', 'OrderDate']], 
            on='OrderID', 
            how='outer'
        )

        # Update Tracking Status where necessary, maintaining the latest status from orders_master  
        merged_df['Status'] = merged_df.apply(
            lambda row: row['Status_y'] if pd.notnull(row['Status_y']) else row['Status_x'], axis=1) 
   
        # Drop unnecessary columns resulting from the merge
        merged_df_cleaned = merged_df.drop(columns=['Status_x', 'Status_y'])

        # Assign tracking numbers sequentially based on the OrderID
        merged_df_cleaned = merged_df_cleaned.sort_values('OrderID').reset_index(drop=True)
        merged_df_cleaned['TrackingID'] = range(1, len(merged_df_cleaned) + 1)

        # Populate UpdatedAt values using the OrderDate, assuming UpdatedAt is the same as OrderDate
        merged_df_cleaned['UpdatedAt'] = merged_df_cleaned['OrderDate']

        # Save the result
        self.update_tracking(merged_df)

    def update_tracking(self, df):
        df.to_csv('data/Tracking.csv', index=False)
        print('>> Tracking.csv updated!')

if __name__ == '__main__':
    # Initiate class instance
    tracking_generator = GenerateTracking()

    # Run
    tracking_generator.generate_tracking()