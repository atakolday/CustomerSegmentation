import pandas as pd
import random

class GenerateReviews:
    def __init__(self):
        # initializing the dataframe
        self.data = pd.read_csv('data/Orders_Master.csv')

    def generate_review_and_rating(self, product_name):
        positive_reviews = [
            f"I absolutely loved the {product_name}, it was even better than I expected. The quality is top-notch, and it's very well-made. Definitely worth every penny!",
            f"The {product_name} is fantastic! It fits perfectly and performs as promised. I couldn’t be happier with my purchase and will recommend it to my friends.",
            f"Very satisfied with the {product_name}. It exceeded my expectations in every way. High quality and durable, I’m extremely pleased with the performance!",
            f"The {product_name} works like a charm! It's everything I needed and more. Would definitely buy it again without hesitation.",
            f"Had a great experience with the {product_name}, from ordering to delivery, and the product quality is superb. I'm very happy and would highly recommend it!"
        ]
        
        neutral_reviews = [
            f"The {product_name} is okay. It does the job but doesn't stand out in any particular way. I'm not sure if I would purchase it again, but it serves its purpose.",
            f"I have mixed feelings about the {product_name}. It's decent for the price, but there are some things that could be improved. It works fine, though.",
            f"The {product_name} is average. Not too bad, but also nothing extraordinary. It's functional, but I’m not overly excited about it.",
            f"To be honest, the {product_name} is just alright. It’s not terrible, but there’s room for improvement. I wouldn't say it’s great, but it’s not awful either.",
            f"The {product_name} is fine for everyday use. It's not exceptional, but it gets the job done. I don't feel strongly about it either way."
        ]
        
        negative_reviews = [
            f"I was really disappointed with the {product_name}. The quality was poor, and it didn't meet any of my expectations. I wouldn't recommend it to anyone.",
            f"The {product_name} turned out to be a big letdown. It feels cheaply made, and I regret buying it. Definitely not worth the money I spent.",
            f"The {product_name} broke after only a few uses. I expected much better quality, and this product didn’t deliver. I wouldn't purchase this again.",
            f"I’m really unhappy with the {product_name}. It didn’t work as advertised and had multiple issues. Save your money and look for something else.",
            f"The {product_name} was overpriced and didn’t live up to the hype. I found it frustrating to use and wouldn't recommend it at all."
        ]
        
        choice = random.random()
        if choice < 0.33:
            review = random.choice(negative_reviews)
            rating = random.randint(1, 2)  # Negative reviews get 1 or 2 stars
        elif 0.33 <= choice < 0.66:
            review = random.choice(neutral_reviews)
            rating = 3  # Neutral reviews get 3 stars
        else:
            review = random.choice(positive_reviews)
            rating = random.randint(4, 5)  # Positive reviews get 4 or 5 stars
        
        return review, rating
    
    def add_reviews(self):
        # Filter delivered orders from orders_master
        delivered_orders = self.data.loc[self.data['Status'] == 'Delivered']
        
        # Add Reviews and Ratings columns if they don't exist
        self.data['Reviews'], self.data['Ratings'] = None, None
        
        # Generate reviews and ratings for delivered orders
        for idx, row in delivered_orders.iterrows():
            review, rating = self.generate_review_and_rating(row['Name'])
            self.data.at[idx, 'Reviews'] = review
            self.data.at[idx, 'Ratings'] = rating

        self.update_orders()

    def update_orders(self):
        self.data.to_csv('data/Orders_Master.csv', index=False)
        print('>> Generated reviews and ratings added to Orders_Master.csv!')

if __name__ == '__main__':
    # Instantiate GenerateReviews (which inherits orders_master from DataClean)
    review_generator = GenerateReviews()
    
    # Generate reviews and ratings
    review_generator.add_reviews()