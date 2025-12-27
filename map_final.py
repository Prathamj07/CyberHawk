import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import os
import json
import geopandas as gpd

with open("D:/Study/SIH 2024/CyberCrew/trials/saved/states_india.geojson", "r") as f:
    geojson_data = json.load(f)

geo_data = gpd.GeoDataFrame.from_features(geojson_data["features"])


# Your existing create_map function
def create_map(csv_file, geojson_file):
    # Load the CSV data (dynamic data)
    data = pd.read_csv(csv_file)

    # Load the GeoJSON data into a GeoDataFrame
    geo_data = gpd.read_file(geojson_file)

    # Dynamically merge GeoJSON with the latest CSV data
    geo_data = geo_data.merge(data, left_on="st_nm", right_on="State/UT", how="left")

    # Create the base map
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="cartodbpositron")

    # Add the choropleth layer
    folium.Choropleth(
        geo_data=geojson_file,
        name="choropleth",
        data=data,
        columns=["State/UT", "Incidents in 2024", "Rate of Total Cyber Crimes (2024)", "Key Trends"],
        key_on="feature.properties.st_nm", 
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Cyber Incidents in India",
    ).add_to(m)


    folium.GeoJson(
        geo_data,
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=folium.features.GeoJsonTooltip(
            fields=["st_nm", "Incidents in 2024", "Rate of Total Cyber Crimes (2024)", "Key Trends"],
            aliases=["Region:", "Incidents in 2024", "Rate of Total Cyber Crimes (2024)", "Key Trends"],
            localize=True
        ),
        highlight_function=lambda x: {"weight": 3, "fillColor": "grey", "color": "black"},
    ).add_to(m)

    # Add a layer control panel
    folium.LayerControl().add_to(m)

    # Save the map temporarily
    map_path = "choropleth_map.html"
    m.save(map_path)

    # Get the absolute file path
    file_url = 'file://' + os.path.abspath(map_path)

    # Return the path to be used in the Streamlit app
    return file_url


# Sidebar navigation
def sidebar_navigation():
    st.sidebar.title("Navigation")
    options = ["Feed", "Visualization", "Cyber Mapping", "Cert", "Report Incident"]
    choice = st.sidebar.radio("Select Option", options)
    return choice

# Main function to display the Streamlit app
def app():
    st.title("CyberHawk")
    choice = sidebar_navigation()

    if choice == "Feed":
        st.subheader("Cyber News Feed")
        # Load and display news feed
        pass

    elif choice == "Cyber Mapping":
        st.subheader("Cyber Mapping")
        st.write("Visualize the cyber threats and map the locations.")
        
        # Generate the map and get the file URL
        map_url = create_map("Cyber_Crime_Data.csv", "states_india.geojson")
        
        # Embed the map in the Streamlit app using an iframe
        st.markdown(f'<iframe src="{map_url}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

    elif choice == "Cert":
        st.subheader("Cert Information")
        st.write("View CERT-related data and statistics.")

    elif choice == "Report Incident":
        st.title("Report an Incident")
        # Incident reporting form
        pass

if __name__ == "__main__":
    app()
