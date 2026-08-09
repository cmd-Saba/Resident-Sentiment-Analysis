import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import folium
from streamlit_folium import folium_static
import subprocess
import sys

# Page settings
st.set_page_config(layout="wide", page_title="HAL Township Resident Sentiment Dashboard")

# Custom CSS for styling KPIs and layout
st.markdown("""
<style>
/* Main app background */
.stApp {
    background-color: #f8f9fa;
}
/* Sidebar background and text */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e1dfdd;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
    color: #111111 !important;
    font-weight: 700 !important;
}
/* Style the metric cards like PowerBI visuals (and make them look like buttons) */
div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e1dfdd;
    border-top: 4px solid #004d99;
    padding: 15px 20px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
div[data-testid="stMetricLabel"], 
div[data-testid="stMetricLabel"] * {
    font-size: 1.1rem !important;
    color: #000000 !important;
    font-weight: 800 !important;
    text-transform: uppercase;
}
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
    font-size: 2.2rem !important;
    color: #000000 !important;
    font-weight: 800 !important;
}
/* Style sidebar dropdowns to be basic white (targets both the box and the dropdown list) */
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="popover"],
ul[role="listbox"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
/* Style subheaders to look like widget titles */
h3, h2 {
    font-size: 1.1rem !important;
    color: #111111 !important;
    font-weight: 700 !important;
    padding-top: 15px !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid #e1dfdd;
    margin-bottom: 15px !important;
}
/* Style Tabs to make them highly visible */
div[data-testid="stTabs"] button {
    background-color: #ffffff;
    border: 1px solid #e1dfdd;
    border-radius: 4px 4px 0 0;
    padding: 10px 20px;
    font-weight: 600;
    color: #605e5c;
    margin-right: 5px;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background-color: #004d99 !important;
    color: #ffffff !important;
    border: 1px solid #004d99 !important;
}
/* Remove default tab border to blend with new buttons */
div[data-baseweb="tab-list"] {
    gap: 0px;
    border-bottom: 2px solid #004d99;
    padding-bottom: 0px;
}
</style>
""", unsafe_allow_html=True)

# Header with Logo
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/5f/Hindustan_Aeronautics_Limited_Logo.svg/1200px-Hindustan_Aeronautics_Limited_Logo.svg.png", use_container_width=True)
with col_title:
    st.markdown("<h1 style='color: #004d99; font-weight: 800; border-bottom: 3px solid #004d99; padding-bottom: 10px; margin-top: -15px;'>HAL Township Resident Sentiment Dashboard</h1>", unsafe_allow_html=True)

# Load the processed data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("processed_feedback.csv")
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Full Name", "Sector", "Feedback", "Date", "Sentiment", "Category"])

df = load_data()

# Load coordinates from sector_coords.csv
@st.cache_data
def load_coords():
    try:
        coord_df = pd.read_csv("sector_coords.csv")
        return {
            row["Sector"]: [row["Latitude"], row["Longitude"]]
            for _, row in coord_df.iterrows()
        }
    except FileNotFoundError:
        return {}

sector_coords = load_coords()

if df.empty:
    st.error("processed_feedback.csv not found or is empty! Please run 'Refresh Data' or sync data first.")
else:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Dashboard Filters")
    
    # Sector Filter
    all_sectors = ["All"] + sorted(df["Sector"].dropna().unique().tolist())
    selected_sector = st.sidebar.selectbox("Select Sector", all_sectors)
    
    # Sentiment Filter
    all_sentiments = ["All"] + sorted(df["Sentiment"].dropna().unique().tolist())
    selected_sentiment = st.sidebar.selectbox("Select Sentiment", all_sentiments)

    # Apply Filters
    filtered_df = df.copy()
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["Sector"] == selected_sector]
    if selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df["Sentiment"] == selected_sentiment]
        
    st.sidebar.markdown("---")
    if st.sidebar.button("Refresh Data"):
        with st.spinner("Updating data..."):
            try:
                subprocess.run([sys.executable, "sync_feedback.py"], check=True)
                subprocess.run([sys.executable, "sentiment_analysis.py"], check=True)
                st.cache_data.clear()
                st.success("Data updated!")
                st.rerun()
            except subprocess.CalledProcessError as e:
                st.sidebar.error(f"Error updating data: {e}")

    # Add space between header and KPIs
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- KPIs ---
    total_feedback = len(filtered_df)
    if total_feedback > 0:
        satisfied_pct = (len(filtered_df[filtered_df["Sentiment"] == "Satisfied"]) / total_feedback) * 100
        most_common_complaint = filtered_df[filtered_df["Sentiment"] == "Frustrated"]["Category"].mode()
        top_complaint = most_common_complaint[0] if not most_common_complaint.empty else "None"
    else:
        satisfied_pct = 0
        top_complaint = "N/A"

    col1, col2, col3 = st.columns(3)
    
    # Custom HTML for Clickable Light Blue KPI Cards
    kpi_style = "background-color: #e6f7ff; border: 1px solid #b3e0ff; border-top: 4px solid #004d99; padding: 15px 20px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
    label_style = "font-size: 1.1rem; color: #000000; font-weight: 800; text-transform: uppercase; margin-bottom: 5px;"
    val_style = "font-size: 2.2rem; color: #000000; font-weight: 800;"
    
    st.markdown("""
    <style>
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)
    
    with col1:
        st.markdown(f"""
            <a href="#full-feedback-dataset" style="text-decoration: none;">
                <div class="kpi-card" style="{kpi_style}">
                    <div style="{label_style}">Total Feedback</div>
                    <div style="{val_style}">{total_feedback}</div>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <a href="#full-feedback-dataset" style="text-decoration: none;">
                <div class="kpi-card" style="{kpi_style}">
                    <div style="{label_style}">Overall Satisfaction</div>
                    <div style="{val_style}">{satisfied_pct:.1f}%</div>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <a href="#full-feedback-dataset" style="text-decoration: none;">
                <div class="kpi-card" style="{kpi_style}">
                    <div style="{label_style}">Top Complaint Category</div>
                    <div style="{val_style}">{top_complaint}</div>
                </div>
            </a>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- TABS ---
    tab1, tab2 = st.tabs(["Geographic View", "Analytics & Trends"])

    with tab1:
        st.subheader("Sunabeda Sector Sentiment Map")
        m = folium.Map(location=[18.725, 82.825], zoom_start=15)
        
        # Adding a marker for each sector based on sentiment
        for sector, coords in sector_coords.items():
            sector_df = filtered_df[filtered_df["Sector"] == sector]
            if len(sector_df) == 0:
                sentiment = "No Data"
                color = "gray"
            else:
                sentiment = sector_df["Sentiment"].mode()[0]
                color = {"Satisfied": "green", "Neutral": "orange", "Frustrated": "red"}.get(sentiment, "gray")
                
            folium.CircleMarker(
                location=coords,
                radius=10,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=f"{sector}: {sentiment}"
            ).add_to(m)

        folium_static(m, width=1200, height=600)

    with tab2:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Overall Sentiment Distribution")
            if not filtered_df.empty:
                sentiment_count = filtered_df["Sentiment"].value_counts()
                st.bar_chart(sentiment_count)
            else:
                st.info("No data available for current filters.")
                
        with col_chart2:
            st.subheader("Top Complaint Categories")
            if not filtered_df.empty:
                category_count = filtered_df["Category"].value_counts()
                st.bar_chart(category_count)
            else:
                st.info("No data available for current filters.")

        st.markdown("---")
        
        col_heat, col_word = st.columns(2)
        
        with col_heat:
            st.subheader("Heatmap: Sentiment vs Sector")
            if not filtered_df.empty:
                heatmap_data = filtered_df.pivot_table(index="Sector", columns="Sentiment", aggfunc="size", fill_value=0)
                fig, ax = plt.subplots(figsize=(6, 4))
                sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Blues", ax=ax, linewidths=.5)
                plt.ylabel("")
                plt.xlabel("")
                st.pyplot(fig)
            else:
                st.info("No data available.")

        with col_word:
            st.subheader("Common Complaints (Frustrated)")
            frustrated_text = " ".join(filtered_df[filtered_df["Sentiment"] == "Frustrated"]["Feedback"])
            if frustrated_text:
                wordcloud = WordCloud(width=600, height=400, background_color="white", colormap="inferno").generate(frustrated_text)
                st.image(wordcloud.to_array(), use_container_width=True)
            else:
                st.info("No frustrated feedback matches the current filters.")

    # --- RAW DATA SECTION ---
    st.markdown("---")
    st.subheader("Full Feedback Dataset")
    st.dataframe(filtered_df, use_container_width=True)
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="resident_feedback.csv",
        mime="text/csv",
        type="primary"
    )
