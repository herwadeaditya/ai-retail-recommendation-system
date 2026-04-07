# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 17:45:18 2026

@author: ADITYA
"""

import pandas as pd
import random

products = {
    "Diwali": ["Sweets", "Dry Fruits", "Gift Box"],
    "Holi": ["Colors", "Pichkari"],
    "Summer": ["Cap", "Sunglasses", "Sunscreen", "Water Bottle"],
    "Rainy": ["Raincoat", "Umbrella"],
    "Winter": ["Jacket", "Heater", "Blanket"]
}

categories = {
    "Sweets": "Food", "Dry Fruits": "Food", "Gift Box": "Gift",
    "Colors": "Toys", "Pichkari": "Toys",
    "Cap": "Fashion", "Sunglasses": "Fashion", "Sunscreen": "Health", "Water Bottle": "Utility",
    "Raincoat": "Fashion", "Umbrella": "Utility",
    "Jacket": "Fashion", "Heater": "Electronics", "Blanket": "Home"
}

data = []
invoice_id = 1

for _ in range(400):
    occasion = random.choice(list(products.keys()))

    # ✅ FIX HERE
    num_products = random.randint(2, min(3, len(products[occasion])))
    selected_products = random.sample(products[occasion], num_products)

    for product in selected_products:
        quantity = random.randint(1, 10)
        price = random.randint(100, 1000)

        data.append([invoice_id, product, categories[product], occasion, quantity, price])

    invoice_id += 1

df = pd.DataFrame(data, columns=["InvoiceNo", "Product", "Category", "Occasion", "Quantity", "Price"])
df.to_csv("sales_data.csv", index=False)

print("✅ Dataset generated successfully!")