# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 17:15:22 2026

@author: ADITYA
"""
import pandas as pd

def suggest_discount(quantity):
    if quantity > 12:
        return "🔥 High Demand → 5% Discount"
    elif quantity > 8:
        return "⚡ Medium Demand → 10% Discount"
    else:
        return "💡 Low Demand → 15% Discount"

def explain_recommendation(product, quantity):
    return f"{product} is trending with expected sales of {quantity} units."
