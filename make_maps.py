import folium
from folium.plugins import HeatMap, MarkerCluster
from loader import load_all_cities

df = load_all_cities("data")

# Premium basemap — not washed out, good contrast
m = folium.Map(
    location=[22.9, 78.5],
    zoom_start=5,
    tiles="OpenStreetMap",
    control_scale=True
)

# Color function for safety levels
def color(score):
    if score >= 30:
        return "green"
    elif score >= 10:
        return "orange"
    return "red"

# Add marker clustering (prevents clutter)
marker_cluster = MarkerCluster().add_to(m)

# Add markers with labels
for _, row in df.iterrows():

    label = (
        f"<b>{row['school_name']}</b><br>"
        f"City: {row['city']}<br>"
        f"Safety Index: {row['overall_safety_index']}<br>"
        f"Pedestrian: {row['pedestrian_safety_index']}<br>"
        f"Emergency: {row['emergency_safety_index']}"
    )

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=7,                # Bigger for India scale
        color=color(row["overall_safety_index"]),
        fill=True,
        fill_color=color(row["overall_safety_index"]),
        fill_opacity=0.85,
        weight=1,
        popup=label,
        tooltip=row["school_name"]  # Label on hover
    ).add_to(marker_cluster)

# Cleaner heatmap (better smoothing, controlled intensity)
heat_data = df[['lat', 'lon', 'overall_safety_index']].values.tolist()
HeatMap(
    heat_data,
    min_opacity=0.3,
    radius=18,
    blur=22,
    max_zoom=9
).add_to(m)

# Add a legend (high | medium | low safety)
legend_html = """
<div style="
    position: fixed; 
    bottom: 30px; left: 30px; width: 180px; 
    background-color: white; 
    border-radius: 8px; 
    padding: 12px; 
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
    font-size: 14px;
">
<b>Safety Index Legend</b><br>
<span style="background: green; width: 12px; height: 12px; display: inline-block;"></span> High (30+)<br>
<span style="background: orange; width: 12px; height: 12px; display: inline-block;"></span> Medium (10–29)<br>
<span style="background: red; width: 12px; height: 12px; display: inline-block;"></span> Low (0–9)<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Layer control button
folium.LayerControl().add_to(m)

# Save map
m.save("all_cities_safety_map.html")
print("PREMIUM MAP GENERATED: all_cities_safety_map.html")
