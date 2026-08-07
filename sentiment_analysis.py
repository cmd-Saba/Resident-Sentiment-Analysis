import pandas as pd
from textblob import TextBlob
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

#  Defining Categories and Keywords 
category_keywords = {
    "Water": ["water", "drinking", "water supply", "tap", "pipeline"],
    "Electricity": ["electricity", "power", "voltage", "cut", "load shedding", "supply"],
    "Sanitation": ["garbage", "waste", "trash", "cleaning", "dustbin"],
    "Infrastructure": ["road", "street", "drain", "pothole", "construction", "sidewalk"],
    "Security": ["security", "theft", "guards", "safety", "robbery"],
    "Noise": ["noise", "loud", "sound", "disturbance"],
    "Other": []  # Default fallback
}

#  Sentiment Analysis 
def get_sentiment(text):
    if not isinstance(text, str) or not text.strip():
        return "Neutral"
    
    text = text.strip()
    text_lower = text.lower()
    
    # Keyword based boosting for negative sentiment
    frustration_keywords = ["frustrating", "delayed", "noise", "urgent", "dirty", "irregular", "flooding", "bad", "worst"]
    if any(keyword in text_lower for keyword in frustration_keywords):
        return "Frustrated"

    # Positive keywords override
    satisfaction_keywords = ["good", "clean", "stable", "happy", "fine", "peaceful", "love", "useful"]
    if any(keyword in text_lower for keyword in satisfaction_keywords):
        return "Satisfied"
        
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.05:
        return "Satisfied"
    elif polarity < -0.05:
        return "Frustrated"
    else:
        return "Neutral"

#  Categorization Function 
def categorize_feedback(text):
    if not isinstance(text, str) or not text.strip():
        return "Other"
        
    text = text.lower().strip()
    
    # Calculate score for each category based on keyword matches
    category_scores = {category: 0 for category in category_keywords}
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text:
                category_scores[category] += 1
                
    # Find category with highest score
    best_category = "Other"
    max_score = 0
    for category, score in category_scores.items():
        if score > max_score:
            max_score = score
            best_category = category
            
    return best_category

def main():
    try:
        # Load raw feedback
        df = pd.read_csv("resident_feedback.csv")
    except FileNotFoundError:
        logging.error("'resident_feedback.csv' not found. Please ensure it exists or run sync_feedback.py first.")
        sys.exit(1)
        
    # Drop rows where Feedback is completely missing
    df = df.dropna(subset=['Feedback'])

    df["Sentiment"] = df["Feedback"].apply(get_sentiment)
    df["Category"] = df["Feedback"].apply(categorize_feedback)

    try:
        # Save updated file
        df.to_csv("processed_feedback.csv", index=False)
        logging.info("✅ Sentiment + Category added and saved in 'processed_feedback.csv'")
    except Exception as e:
        logging.error(f"Failed to save processed feedback: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
