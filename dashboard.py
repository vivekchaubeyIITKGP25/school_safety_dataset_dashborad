import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from loader import load_all_cities

st.set_page_config(layout="wide")

# Load full dataset
df = load_all_cities("data")

st.title("Multi-City School Safety Dashboard")
st.markdown("Analyze and compare safety indicators across cities.")

# ---------------------------------------------------------
# 1️⃣ CITY SAFETY SUMMARY TABLE
# ---------------------------------------------------------
st.header("City Safety Summary")

city_summary = df.groupby("city").agg({
    "overall_safety_index": "mean",
    "pedestrian_safety_index": "mean",
    "emergency_safety_index": "mean"
}).round(2)

city_summary = city_summary.rename(columns={
    "overall_safety_index": "Avg Overall Safety",
    "pedestrian_safety_index": "Avg Pedestrian Safety",
    "emergency_safety_index": "Avg Emergency Safety"
})

st.dataframe(city_summary)


# ---------------------------------------------------------
# CLEAN + CRISP LINE PLOT (final improved version)
# ---------------------------------------------------------
st.header("Top 10 Safest Cities")

top10 = (
    city_summary
    .sort_values("Avg Overall Safety", ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(11, 4.2))

x_vals = np.arange(len(top10))
y_vals = top10["Avg Overall Safety"].values
labels = top10.index

# light blue subtle band (not the huge filled polygon)
ax.axhspan(
    min(y_vals) - 2, max(y_vals) + 2,
    facecolor="#e8f1fc",
    alpha=0.55
)

# vertical guides (same style as histogram)
for x in x_vals:
    ax.axvline(
        x, color="gray", linestyle="--",
        linewidth=0.6, alpha=0.25
    )

# line (straight, no distortion)
ax.plot(
    x_vals, y_vals,
    color="darkred",
    linewidth=2.4
)

# markers
ax.scatter(
    x_vals, y_vals,
    s=70,
    color="white",
    edgecolor="black",
    linewidth=1.3,
    zorder=3
)

# labels above points
for i, v in enumerate(y_vals):
    ax.text(
        x_vals[i], v + 0.8,
        f"{v:.2f}",
        ha="center",
        fontsize=10,
        fontweight="bold"
    )

# x-labels
ax.set_xticks(x_vals)
ax.set_xticklabels(labels, rotation=45, ha="right")

# axis labels + title
ax.set_ylabel("Average Safety Score", fontsize=12)
ax.set_title(
    "Top 10 Cities by Average Safety Score",
    fontsize=15, fontweight="bold"
)

# grid (subtle)
ax.grid(axis="y", linestyle="--", alpha=0.35)

# clean spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
st.pyplot(fig)


# ---------------------------------------------------------
# 3️⃣ CITY FILTER
# ---------------------------------------------------------
cities = ["All"] + sorted(df["city"].unique().tolist())
selected_city = st.sidebar.selectbox("Select City", cities)

df_view = df if selected_city == "All" else df[df["city"] == selected_city]
# make a copy to avoid SettingWithCopyWarning when adding columns
df_view = df_view.copy()

st.subheader(f"Showing Data For: {selected_city}")

# ---------------------------------------------------------
# ⬇️ DOWNLOAD JSON BUTTONS
# ---------------------------------------------------------
st.header("Download Data")

# Convert to JSON strings
full_json = df.to_json(orient="records", indent=2)
filtered_json = df_view.to_json(orient="records", indent=2)

# Download full dataset
st.download_button(
    label="Download All Cities Data (JSON)",
    data=full_json,
    file_name="all_cities_data.json",
    mime="application/json"
)

# Download filtered dataset
st.download_button(
    label=f"Download Filtered Data ({selected_city}) (JSON)",
    data=filtered_json,
    file_name=f"{selected_city.replace(' ', '_').lower()}_data.json",
    mime="application/json"
)

# ---------------------------------------------------------
# 4️⃣ TOP 10 SAFEST & NEW TABLES
# ---------------------------------------------------------
st.header("School Rankings")

st.subheader("Top 10 Safest Schools (by Overall Safety Index)")
safest = df_view.sort_values("overall_safety_index", ascending=False).head(10)
st.dataframe(safest[["school_name", "city", "overall_safety_index"]])


# ---------------------------------------------------------
# 5️⃣ LABELED GRAPHS (with axis scales/ticks and annotations)
# ---------------------------------------------------------
st.header("Safety Distribution Charts")

def plot_hist_with_scale(series, title, xlabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    data = series.dropna()

    if data.empty:
        ax.text(0.5, 0.5, "No data", ha='center', va='center')
        st.pyplot(fig)
        return

    # -------------------------------
    # Force bin width = 5
    # -------------------------------
    bin_width = 5
    xmin = 0
    xmax = 100
    bins = np.arange(xmin, xmax + bin_width, bin_width)

    # -------------------------------
    # Histogram
    # -------------------------------
    counts, bins, patches = ax.hist(
        data,
        bins=bins,
        edgecolor='black',
        alpha=0.6,
        color="#4A90E2"
    )

    # Make histogram touch Y axis (remove padding)
    ax.set_xlim(left=xmin, right=xmax)

    # -------------------------------
    # KDE curve
    # -------------------------------
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(data)
    xs = np.linspace(xmin, xmax, 500)
    ax.plot(xs, kde(xs) * len(data) * bin_width, color="darkred", linewidth=2)

    # -------------------------------
    # Vertical lines at bin centers
    # -------------------------------
    bin_centers = (bins[:-1] + bins[1:]) / 2
    for c in bin_centers:
        ax.axvline(c, color="darkblue", linestyle="--", alpha=0.25)

    # Labels
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("Number of Schools", fontsize=12)

    ax.grid(True, linestyle="--", alpha=0.5)

    # -------------------------------
    # Scale label box
    # -------------------------------
    y_tick_interval = int(ax.get_yticks()[1] - ax.get_yticks()[0])

    box_text = (
        f"X-bin width: {bin_width}\n"
        f"Y-scale: {y_tick_interval} per tick"
    )

    ax.text(
        0.98, 0.98,
        box_text,
        transform=ax.transAxes,
        fontsize=9,
        ha="right",
        va="top",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="black")
    )

    plt.tight_layout()
    st.pyplot(fig)

# Overall Safety
plot_hist_with_scale(df_view["overall_safety_index"], "Overall Safety Index Distribution", "Safety Index")

# Pedestrian Safety
plot_hist_with_scale(df_view["pedestrian_safety_index"], "Pedestrian Safety Index Distribution", "Pedestrian Index")

# Emergency Safety
plot_hist_with_scale(df_view["emergency_safety_index"], "Emergency Safety Index Distribution", "Emergency Safety Index")

# 3d
import plotly.graph_objects as go

def plot_3d_donut(labels, values, colors):
    fig = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.45,           # donut size
            pull=[0.06]*len(values),  # explode slices
            textinfo="percent",
            textfont=dict(size=16, color="white"),
            marker=dict(
                colors=colors,
                line=dict(color="rgba(0,0,0,0.55)", width=5)  # bevel edge = 3D look
            )
        )]
    )

    fig.update_layout(
        showlegend=False,
        height=380,
        width=380,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Increase edge shading (3D walls)
    fig.update_traces(marker=dict(line=dict(width=7, color="rgba(0,0,0,0.45)")))

    return fig

# ---------------------------------------------------------
# 6️⃣ PIE CHARTS – 3D DONUT STYLE + LABELS + DETAILS
# ---------------------------------------------------------
st.header("Infrastructure Safety Features")

colA, colB, colC = st.columns([1, 1, 1])

# ----------------------- TRAFFIC LIGHTS -----------------------
with colA:
    st.write("<h4 style='text-align:center;'>Traffic Lights</h4>", unsafe_allow_html=True)

    counts = df_view["traffic_light"].fillna(False).astype(bool).value_counts()
    labels = ["No", "Yes"]
    values = [counts.get(False, 0), counts.get(True, 0)]
    colors = ["#3498db", "#2ecc71"]  # blue = No, green = Yes

    figA = plot_3d_donut(labels, values, colors)
    st.plotly_chart(figA, use_container_width=True)

    # Legend
    st.markdown("""
    <div style="text-align:center; font-size:14px;">
        <span style="color:#3498db; font-weight:bold;">⬤ No</span> &nbsp;&nbsp;
        <span style="color:#2ecc71; font-weight:bold;">⬤ Yes</span>
    </div>
    """, unsafe_allow_html=True)

    # Explanation text
    st.markdown("""
    <div style="font-size:13px; text-align:center; color:#dcdcdc;">
    Blue represents schools <span style="font-weight:900;"><strong>WITHOUT TRAFFIC LIGHTS</strong></span>.<br>
    Green represents schools <span style="font-weight:900;"><strong>WITH TRAFFIC LIGHTS</strong></span> present.
      </div>
""", unsafe_allow_html=True)




# ----------------------- CROSSWALKS -----------------------
with colB:
    st.write("<h4 style='text-align:center;'>Crosswalks</h4>", unsafe_allow_html=True)

    counts = df_view["crosswalk"].fillna(False).astype(bool).value_counts()
    labels = ["No", "Yes"]
    values = [counts.get(False, 0), counts.get(True, 0)]
    colors = ["#e74c3c", "#f1c40f"]  # red = No, yellow = Yes

    figB = plot_3d_donut(labels, values, colors)
    st.plotly_chart(figB, use_container_width=True)

    # Legend
    st.markdown("""
    <div style="text-align:center; font-size:14px;">
        <span style="color:#e74c3c; font-weight:bold;">⬤ No</span> &nbsp;&nbsp;
        <span style="color:#f1c40f; font-weight:bold;">⬤ Yes</span>
    </div>
    """, unsafe_allow_html=True)

    # Explanation text
    st.markdown("""
<div style="font-size:13px; text-align:center; color:#dcdcdc;">
    Red represents schools <span style="font-weight:900;"><strong>WITHOUT CROSSWALKS</strong></span>.<br>
    Yellow shows schools <span style="font-weight:900;"><strong>WITH CROSSWALK AVAILABILITY</strong></span>.
</div>
""", unsafe_allow_html=True)




# ----------------------- SAFETY CATEGORIES -----------------------
with colC:
    st.write("<h4 style='text-align:center;'>Safety Categories</h4>", unsafe_allow_html=True)

    # UPDATED CATEGORY RANGES
    df_view["safety_category"] = pd.cut(
        df_view["overall_safety_index"].fillna(0),
        bins=[-1, 10, 40, 100],       # <---- UPDATED BINS
        labels=["Low", "Medium", "High"]
    )

    counts = df_view["safety_category"].value_counts().reindex(["Low","Medium","High"], fill_value=0)
    labels = ["Low", "Medium", "High"]
    values = counts.tolist()
    colors = ["#e74c3c", "#f1c40f", "#2ecc71"]  # red, yellow, green

    figC = plot_3d_donut(labels, values, colors)
    st.plotly_chart(figC, use_container_width=True)

    # Legend under chart
    st.markdown("""
    <div style="text-align:center; font-size:14px;">
        <span style="color:#e74c3c; font-weight:bold;">⬤ Low</span> &nbsp;&nbsp;
        <span style="color:#f1c40f; font-weight:bold;">⬤ Medium</span> &nbsp;&nbsp;
        <span style="color:#2ecc71; font-weight:bold;">⬤ High</span>
    </div>
    """, unsafe_allow_html=True)

    # UPDATED Explanation text
    st.markdown("""
    <div style="font-size:13px; text-align:center; color:#dcdcdc;">
        <span style="font-weight:900;"><strong>LOW</strong></span> (Red): Safety Index 0–10 <br>
        <span style="font-weight:900;"><strong>MEDIUM</strong></span> (Yellow): Safety Index 11–40 <br>
        <span style="font-weight:900;"><strong>HIGH</strong></span> (Green): Safety Index 41–100
    </div>
    """, unsafe_allow_html=True)



# ---------------------------------------------------------
# 7️⃣ GEOSPATIAL MAP (HTML VERSION)
# ---------------------------------------------------------
st.header("Full Geospatial Map")

try:
    with open("all_cities_safety_map.html", "r", encoding="utf-8") as f:
        html_data = f.read()

    st.components.v1.html(html_data, height=700, scrolling=True)

except Exception as e:
    st.error("❌ HTML map file not found. Make sure all_cities_safety_map.html is uploaded.")
    st.write(e)
