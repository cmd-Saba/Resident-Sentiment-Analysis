import pandas as pd
from textblob import TextBlob

# Load raw feedback
df = pd.read_csv("resident_feedback.csv")

# --- Step 1: Sentiment Analysis ---
def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Satisfied"
    elif polarity < -0.1:
        return "Frustrated"
    else:
        return "Neutral"

df["Sentiment"] = df["Feedback"].apply(get_sentiment)

# --- Step 2: Define Categories and Keywords ---
category_keywords = {
    "Water": ["water", "drinking", "supply", "tap", "pipeline"],
    "Electricity": ["electricity", "power", "voltage", "cut", "load shedding"],
    "Sanitation": ["garbage", "waste", "trash", "cleaning", "dustbin"],
    "Infrastructure": ["road", "street", "drain", "pothole", "construction", "sidewalk"],
    "Security": ["security", "theft", "guards", "safety", "robbery"],
    "Noise": ["noise", "loud", "sound", "disturbance"],
    "Other": []  # Default fallback
}

# --- Step 3: Categorization Function ---
def categorize_feedback(text):
    text = text.lower()
    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Other"

df["Category"] = df["Feedback"].apply(categorize_feedback)

# Save updated file
df.to_csv("processed_feedback.csv", index=False)
print("✅ Sentiment + Category added and saved in 'processed_feedback.csv'")

