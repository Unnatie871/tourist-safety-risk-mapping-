import pandas as pd
import folium

# Step 1: Load the real Jalandhar data
df = pd.read_csv("data/jalandhar_emergency_points.csv") 

# Step 2: Remove rows without coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Step 3: Find the centre of the map
latitude = df["latitude"].mean()
longitude = df["longitude"].mean()

# Step 4: Create the map
safety_map = folium.Map(
    location=[latitude, longitude],
    zoom_start=12
)

# Step 5: Add locations to the map
for _, row in df.iterrows():

    place_type = str(row["type"])
    place_name = str(row["name"])

    if place_type == "police":
        marker_color = "blue"

    elif place_type == "hospital":
        marker_color = "red"

    elif place_type == "fire_station":
        marker_color = "orange"

    else:
        marker_color = "green"

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=f"{place_name} ({place_type})",
        tooltip=place_name,
        icon=folium.Icon(color=marker_color)
    ).add_to(safety_map) 
# Step 6: Add map legend
legend_html = """
<div style="
position: fixed;
bottom: 30px;
left: 30px;
width: 220px;
background-color: white;
border: 2px solid grey;
z-index: 9999;
padding: 12px;
font-size: 14px;
border-radius: 8px;
">
<h4 style="margin-top: 0;">Map Legend</h4>
<b><span style="color: blue;">●</span> Police Station</b><br>
<b><span style="color: red;">●</span> Hospital</b><br>
<b><span style="color: orange;">●</span> Fire Station</b><br>
<b><span style="color: green;">●</span> Other Facilities</b>
</div>
"""

safety_map.get_root().html.add_child(folium.Element(legend_html)) 

# Step 6: Save the map
safety_map.save("templates/jalandhar_map.html")

print("Interactive map created successfully!")
print("Map contains", len(df), "mapped features.")
print("Saved to templates/jalandhar_map.html") 