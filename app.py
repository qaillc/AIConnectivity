import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datasets import load_dataset
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# Top-level menu
menu = st.sidebar.selectbox(
    "Select a Section",
    ["Introduction", "Funding", "Networking", "Content Delivery", "Maintenance"]
)

menu = "Networking"

# Introduction Section
if menu == "Introduction":
    st.title("Welcome to the Smart Network Infrastructure Planner")
    st.markdown("""
    This application provides tools and insights to optimize network infrastructure 
    based on various criteria such as budget, signal strength, terrain challenges, and climate risks.
    """)

# Funding Section
elif menu == "Funding":
    st.title("Funding Overview")
    st.markdown("""
    Explore various funding strategies and options to support the development of 
    smart network infrastructures.
    """)

# Networking Section
elif menu == "Networking":
    # Initialize geolocator
    geolocator = Nominatim(user_agent="geoapiExercises")

    # Hugging Face Datasets
    @st.cache_data
    def load_data():
        network_insights = load_dataset("infinite-dataset-hub/5GNetworkOptimization", split="train")
        return network_insights.to_pandas()

    # Load Datasets
    network_insights = load_data()

    # Title Section with Styling
    st.markdown("""
    # 🌍 **Smart Network Infrastructure Planner**
    Effortlessly optimize network infrastructure while accounting for budget, signal strength, terrain challenges, and climate risks.
    """)
    st.sidebar.header("🔧 Input Parameters")

    # User Inputs from Sidebar
    with st.sidebar:
        budget = st.number_input("💰 Total Budget (in $1000s):", min_value=10, max_value=1000, step=10)
        priority_area = st.selectbox("🌎 Priority Area:", ["Rural", "Urban", "Suburban"])
        signal_threshold = st.slider("📶 Signal Strength Threshold (dBm):", min_value=-120, max_value=-30, value=-80)
        terrain_weight = st.slider("🌄 Terrain Difficulty Weight:", min_value=0.0, max_value=1.0, value=0.5)
        cost_weight = st.slider("💵 Cost Weight:", min_value=0.0, max_value=1.0, value=0.5)
        climate_risk_weight = st.slider("🌡️ Climate Risk Weight:", min_value=0.0, max_value=1.0, value=0.5)
        include_human_readable = st.checkbox("🗺️ Include Human-Readable Info", value=True)

    # Tabs for Data Display and Analysis
    st.markdown("## 🚀 Insights & Recommendations")
    tabs = st.tabs(["Terrain Analysis", "Filtered Data", "Geographical Map"])

    # Simulate Terrain and Climate Risk Data
    def generate_terrain_data():
        np.random.seed(42)
        data = {
            "Region": [f"Region-{i}" for i in range(1, 11)],
            "Latitude": np.random.uniform(30.0, 50.0, size=10),
            "Longitude": np.random.uniform(-120.0, -70.0, size=10),
            "Terrain Difficulty (0-10)": np.random.randint(1, 10, size=10),
            "Signal Strength (dBm)": np.random.randint(-120, -30, size=10),
            "Cost ($1000s)": np.random.randint(50, 200, size=10),
            "Priority Area": np.random.choice(["Rural", "Urban", "Suburban"], size=10),
            "Climate Risk (0-10)": np.random.randint(0, 10, size=10),
            "Description": [
                "Flat area with minimal obstacles",
                "Hilly terrain, moderate construction difficulty",
                "Dense urban area with high costs",
                "Suburban area, balanced terrain",
                "Mountainous region, challenging setup",
                "Remote rural area, sparse population",
                "Coastal area, potential for high signal interference",
                "Industrial zone, requires robust infrastructure",
                "Dense forest region, significant signal attenuation",
                "Open plains, optimal for cost-effective deployment"
            ]
        }
        return pd.DataFrame(data)

    terrain_data = generate_terrain_data()

    # Reverse Geocoding Function
    def get_location_name(lat, lon):
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True)
            return location.address if location else "Unknown Location"
        except Exception as e:
            return "Error: Unable to fetch location"

    # Add Location Name to Filtered Data
    if include_human_readable:
        filtered_data = terrain_data[
            (terrain_data["Signal Strength (dBm)"] >= signal_threshold) & 
            (terrain_data["Cost ($1000s)"] <= budget) & 
            (terrain_data["Priority Area"] == priority_area)
        ]
        filtered_data["Location Name"] = filtered_data.apply(
            lambda row: get_location_name(row["Latitude"], row["Longitude"]), axis=1
        )
    else:
        filtered_data = terrain_data[
            (terrain_data["Signal Strength (dBm)"] >= signal_threshold) & 
            (terrain_data["Cost ($1000s)"] <= budget) & 
            (terrain_data["Priority Area"] == priority_area)
        ]

    # Add Composite Score for Ranking
    filtered_data["Composite Score"] = (
        (1 - terrain_weight) * filtered_data["Signal Strength (dBm)"] + 
        (terrain_weight) * (10 - filtered_data["Terrain Difficulty (0-10)"]) - 
        (cost_weight) * filtered_data["Cost ($1000s)"] -
        (climate_risk_weight) * filtered_data["Climate Risk (0-10)"]
    )

    # Display Filtered Data in Tab
    with tabs[1]:
        st.subheader("Filtered Terrain Data")
        columns_to_display = [
            "Region", "Location Name", "Priority Area", "Signal Strength (dBm)",
            "Cost ($1000s)", "Terrain Difficulty (0-10)", "Climate Risk (0-10)", "Description", "Composite Score"
        ] if include_human_readable else [
            "Region", "Priority Area", "Signal Strength (dBm)", "Cost ($1000s)", "Terrain Difficulty (0-10)", "Climate Risk (0-10)", "Description", "Composite Score"
        ]
        st.dataframe(filtered_data[columns_to_display])

    # Map Visualization in Tab
    with tabs[2]:
        st.subheader("Geographical Map of Regions")
        if not filtered_data.empty:
            map_center = [filtered_data["Latitude"].mean(), filtered_data["Longitude"].mean()]
            region_map = folium.Map(location=map_center, zoom_start=6)

            for _, row in filtered_data.iterrows():
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=(f"<b>Region:</b> {row['Region']}<br>"
                           f"<b>Location:</b> {row.get('Location Name', 'N/A')}<br>"
                           f"<b>Description:</b> {row['Description']}<br>"
                           f"<b>Signal Strength:</b> {row['Signal Strength (dBm)']} dBm<br>"
                           f"<b>Cost:</b> ${row['Cost ($1000s)']}k<br>"
                           f"<b>Terrain Difficulty:</b> {row['Terrain Difficulty (0-10)']}<br>"
                           f"<b>Climate Risk:</b> {row['Climate Risk (0-10)']}")
                ).add_to(region_map)

            st_folium(region_map, width=700, height=500)
        else:
            st.write("No regions match the selected criteria.")

    # Visualization Tab
    with tabs[0]:
        st.subheader("Signal Strength vs. Cost")
        fig = px.scatter(
            filtered_data,
            x="Cost ($1000s)",
            y="Signal Strength (dBm)",
            size="Terrain Difficulty (0-10)",
            color="Region",
            title="Signal Strength vs. Cost",
            labels={
                "Cost ($1000s)": "Cost in $1000s",
                "Signal Strength (dBm)": "Signal Strength in dBm",
            },
        )
        st.plotly_chart(fig)

    # Recommendation Engine
    st.header("✨ Deployment Recommendations")

    def recommend_deployment(data):
        if data.empty:
            return "No viable deployment regions within the specified parameters."
        best_region = data.loc[data["Composite Score"].idxmax()]
        return f"**Recommended Region:** {best_region['Region']}  \n" \
               f"**Composite Score:** {best_region['Composite Score']:.2f}  \n" \
               f"**Signal Strength:** {best_region['Signal Strength (dBm)']} dBm  \n" \
               f"**Terrain Difficulty:** {best_region['Terrain Difficulty (0-10)']}  \n" \
               f"**Climate Risk:** {best_region['Climate Risk (0-10)']}  \n" \
               f"**Estimated Cost:** ${best_region['Cost ($1000s)']}k  \n" \
               f"**Description:** {best_region['Description']}  \n" \
               f"**Location Name:** {best_region.get('Location Name', 'N/A')}"

    recommendation = recommend_deployment(filtered_data)

    # Display Recommendation
    st.markdown("### 🌟 Final Recommendation")
    st.markdown(recommendation)

# Content Delivery Section
elif menu == "Content Delivery":
    st.title("Content Delivery Strategies")
    st.markdown("""
    Learn how to effectively deliver content to enhance user engagement and ensure seamless communication.
    """)

# Maintenance Section
elif menu == "Maintenance":
    st.title("System Maintenance")
    st.markdown("""
    Discover best practices for maintaining your smart network infrastructure to ensure reliability and longevity.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Developed for Hackathon using Hugging Face Infinite Dataset Hub**\n\n[Visit Hugging Face](https://huggingface.co)"
)
