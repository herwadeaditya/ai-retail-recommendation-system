# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 16:31:59 2026

@author: ADITYA
"""
import os
import pandas as pd
import pickle
from mlxtend.frequent_patterns import apriori, association_rules

os.makedirs("model", exist_ok=True)

df = pd.read_csv("sales_data.csv")

basket = df.groupby(['InvoiceNo', 'Product'])['Quantity'].sum().unstack().fillna(0)
basket = (basket > 0).astype(int)

frequent_items = apriori(basket, min_support=0.02, use_colnames=True)

if frequent_items.empty:
    rules = pd.DataFrame()
else:
    rules = association_rules(frequent_items, metric="lift", min_threshold=1)

with open("model/combo_rules.pkl", "wb") as f:
    pickle.dump(rules, f)

print("✅ Combo model ready!")