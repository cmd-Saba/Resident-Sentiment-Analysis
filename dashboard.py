import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static



# Page settings
st.set_page_config(layout="wide")
st.title("🏘️ Resident Sentiment Analysis Dashboard")

# Load the processed data
df = pd.read_csv("processed_feedback.csv")

# Load coordinates from sector_coords.csv
coord_df = pd.read_csv("sector_coords.csv")

# Convert to dictionary format
sector_coords = {
    row["Sector"]: [row["Latitude"], row["Longitude"]]
    for _, row in coord_df.iterrows()
}

st.subheader("🗺️ Sunabeda Sector Sentiment Map")

# Creating the base map centered on Sunabeda
m = folium.Map(location=[18.695, 82.855], zoom_start=14)

# Adding a marker for each sector based on sentiment
for sector, coords in sector_coords.items():
    # Filter feedback for this sector
    sector_df = df[df["Sector"] == sector]

    if len(sector_df) == 0:
        sentiment = "No Data"
        color = "gray"
    else:
        # Getting the most common sentiment in that sector
        sentiment = sector_df["Sentiment"].mode()[0]
        color = {
            "Satisfied": "green",
            "Neutral": "orange",
            "Frustrated": "red"
        }.get(sentiment, "gray")

    # Adding circle marker
    folium.CircleMarker(
        location=coords,
        radius=10,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=f"{sector}: {sentiment}"
    ).add_to(m)

# Showing the map in Streamlit
folium_static(m)



st.subheader("🌡️ Heatmap: Sentiment vs Sector")



# Pivot data
heatmap_data = df.pivot_table(index="Sector", columns="Sentiment", aggfunc="size", fill_value=0)



# Plot using seaborn
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="coolwarm", ax=ax)
plt.title("Number of Feedbacks by Sector and Sentiment")

st.pyplot(fig)


# Section: Sentiment Distribution
st.subheader("🔢 Overall Sentiment Distribution")
sentiment_count = df["Sentiment"].value_counts()
st.bar_chart(sentiment_count)

# Section: Sector-wise Sentiment Breakdown
st.subheader("📍 Sector-wise Sentiment")
sector_sentiment = pd.crosstab(df["Sector"], df["Sentiment"])
st.dataframe(sector_sentiment)

# Section: Word Cloud for Frustrated Feedback
st.subheader("☁️ Common Complaints (from Frustrated Feedback)")
frustrated_text = " ".join(df[df["Sentiment"] == "Frustrated"]["Feedback"])
if frustrated_text:
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(frustrated_text)
    st.image(wordcloud.to_array())
else:
    st.info("No frustrated feedback yet 😊")

# Section: Raw Feedback Table
st.subheader("📄 Full Feedback Dataset")
st.dataframe(df)

# CSV Download
st.subheader("📁 Download Feedback Data")

csv_data = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇️ Download as CSV",
    data=csv_data,
    file_name="resident_feedback.csv",
    mime="text/csv"
)


st.subheader("🧾 Top Complaint Categories")
category_count = df["Category"].value_counts()
st.bar_chart(category_count)

if st.button("🔄 Refresh Data"):
    import os
    os.system("python sync_feedback.py && python sentiment_analysis.py")
    st.success("Data updated!")
    st.rerun()





