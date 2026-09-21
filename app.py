import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import textwrap

# Page configuration
st.set_page_config(
    page_title="Custom Timeline Generator", page_icon="📊", layout="wide"
)

st.title("📊 Custom Disaster Response Timeline Generator")
st.markdown(
    "Define your custom legend categories in the sidebar, edit your timeline"
    " events below, and generate your high-res graphic instantly."
)

# -----------------------------------------------------------------------------
# 1. SESSION STATE FOR CUSTOM CATEGORIES (LEGEND)
# -----------------------------------------------------------------------------
if "categories" not in st.session_state:
  st.session_state.categories = {
      "Emergency Alert": "#C0392B",
      "Field Assessment": "#D35400",
      "Road & Logistics": "#2980B9",
      "Geological Survey": "#8E44AD",
      "Relief & Recovery": "#27AE60",
  }

# Initialize default timeline data
if "data" not in st.session_state:
  st.session_state.data = [
      {
          "Date": "12-Oct",
          "Activity": (
              "Heavy rainfall triggers massive landslide; Emergency alert"
              " issued; Local police & rescue teams mobilized"
          ),
          "Location": "Sindhupalchok",
          "Category": "Emergency Alert",
      },
      {
          "Date": "13-Oct",
          "Activity": (
              "Initial ground assessment by disaster management team;"
              " Temporary shelters set up for displaced families"
          ),
          "Location": "Affected Ward 4",
          "Category": "Field Assessment",
      },
      {
          "Date": "14-Oct",
          "Activity": (
              "Heavy machinery deployed to clear blocked national highway;"
              " Medical camp established"
          ),
          "Location": "Araniko Highway",
          "Category": "Road & Logistics",
      },
      {
          "Date": "15-Oct",
          "Activity": (
              "Geological survey team evaluates ongoing slope instability;"
              " High-risk zones evacuated"
          ),
          "Location": "Upper Ridge",
          "Category": "Geological Survey",
      },
      {
          "Date": "17-Oct",
          "Activity": (
              "Distribution of food rations, tents, and emergency medical kits;"
              " District coordination meeting held"
          ),
          "Location": "Relief Camp",
          "Category": "Relief & Recovery",
      },
  ]

# -----------------------------------------------------------------------------
# 2. SIDEBAR: DEFINE LEGEND & CATEGORIES FIRST
# -----------------------------------------------------------------------------
st.sidebar.header("🎨 1. Define Legend Categories")
st.sidebar.markdown(
    "Add or remove your custom categories and pick their colors here first:"
)

# Convert session categories to a dataframe for easy editing in sidebar
cat_df = pd.DataFrame([
    {"Category Name": k, "Color (Hex)": v}
    for k, v in st.session_state.categories.items()
])
edited_cat_df = st.sidebar.data_editor(
    cat_df, num_rows="dynamic", key="cat_editor", use_container_width=True
)

# Update session categories based on sidebar input
new_categories = {}
for _, row in edited_cat_df.iterrows():
  name = str(row["CategoryName"]).strip()
  color = str(row["Color(Hex)"]).strip()
  if name and name != "nan":
    if not color.startswith("#"):
      color = "#3B82F6"  # Fallback hex if mistyped
    new_categories[name] = color

st.session_state.categories = new_categories

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Chart Settings")
subtitle_text = st.sidebar.text_input(
    "Subtitle / Date Range",
    "Emergency Operations Timeline  —  October 12 – 17, 2026",
)
source_text = st.sidebar.text_input(
    "Source Footer",
    "Source: District Disaster Management Committee (DDMC) SitReps",
)

# -----------------------------------------------------------------------------
# 3. MAIN AREA: EDIT TIMELINE DATA WITH DYNAMIC DROPDOWN
# -----------------------------------------------------------------------------
st.subheader("📝 2. Edit Timeline Data")
st.markdown(
    "The **Category** column dropdown below automatically syncs with the"
    " categories you defined in the sidebar!"
)

df_input = pd.DataFrame(st.session_state.data)

# Available choices for the dropdown derived directly from user-defined categories
available_categories = list(st.session_state.categories.keys())

edited_df = st.data_editor(
    df_input,
    num_rows="dynamic",
    column_config={
        "Category": st.column_config.SelectboxColumn(
            "Category",
            help="Select from your custom defined categories",
            options=available_categories,
            required=True,
        )
    },
    use_container_width=True,
)

# Styling Constants
BG_COLOR = "#FFFFFF"
CARD_EDGE = "#D8DEE7"
CARD_FILL = "#F7F9FB"
TEXT_COLOR = "#1A2332"
SUBTEXT_COLOR = "#5B6B7F"
LINE_COLOR = "#C2CAD6"
ONGOING_COLOR = "#475569"


def format_activity(text, wrap_width=20):
  points = [p.strip() for p in str(text).split(";") if p.strip()]
  lines = []
  for p in points:
    wrapped = textwrap.fill(p, width=wrap_width)
    wrapped_lines = wrapped.split("\n")
    wrapped_lines[0] = "\u2022 " + wrapped_lines[0]
    wrapped_lines[1:] = ["  " + ln for ln in wrapped_lines[1:]]
    lines.extend(wrapped_lines)
  return "\n".join(lines)


# -----------------------------------------------------------------------------
# 4. CHART GENERATION BUTTON
# -----------------------------------------------------------------------------
if st.button("🚀 Generate & Update Chart", type="primary"):
  if edited_df.empty:
    st.warning("Please enter at least one timeline entry.")
  elif not st.session_state.categories:
    st.warning("Please define at least one category in the sidebar.")
  else:
    n_events = len(edited_df)
    x_coords = np.arange(1, n_events + 1) * 1.0
    spine_y = 0
    x_ongoing = x_coords[-1] + 1.15

    fig, ax = plt.subplots(figsize=(26, 14.5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.axhspan(-0.045, 0.045, xmin=0.0, xmax=1.0, color="#EEF1F5", zorder=0)
    ax.plot(
        [x_coords[0] - 0.6, x_ongoing + 0.55],
        [spine_y, spine_y],
        color=LINE_COLOR,
        lw=2.6,
        zorder=1,
        solid_capstyle="round",
    )

    for i, row in edited_df.iterrows():
      x = x_coords[i]
      is_up = i % 2 == 0
      sign = 1 if is_up else -1
      va = "bottom" if is_up else "top"

      # Fetch color dynamically from user-defined categories
      cat_name = row.get("Category")
      cat_color = st.session_state.categories.get(cat_name, "#3B82F6")
      formatted = format_activity(row.get("Activity", ""))

      stem_top = sign * 0.50
      ax.plot(
          [x, x],
          [spine_y, stem_top],
          color=cat_color,
          lw=1.6,
          linestyle=(0, (4, 2)),
          zorder=2,
          alpha=0.85,
      )
      ax.scatter(
          x,
          spine_y,
          color="white",
          s=460,
          zorder=3,
          edgecolors=cat_color,
          linewidth=2.8,
      )
      ax.scatter(x, spine_y, color=cat_color, s=120, zorder=4)

      y_date = sign * 0.64
      ax.text(
          x,
          y_date,
          str(row.get("Date", "")).upper(),
          fontsize=17,
          fontweight="bold",
          color=cat_color,
          ha="center",
          va=va,
          family="DejaVu Sans",
          bbox=dict(
              boxstyle="round,pad=0.36",
              facecolor="white",
              edgecolor=cat_color,
              lw=1.6,
          ),
      )

      y_activity = sign * 1.05
      ax.text(
          x,
          y_activity,
          formatted,
          fontsize=15,
          color=TEXT_COLOR,
          ha="center",
          va=va,
          linespacing=1.55,
          fontweight="medium",
          bbox=dict(
              boxstyle="round,pad=0.6",
              facecolor=CARD_FILL,
              edgecolor=CARD_EDGE,
              lw=1.2,
          ),
      )

    # Ongoing marker
    ax.scatter(
        x_ongoing,
        spine_y,
        color="white",
        s=460,
        zorder=3,
        edgecolors=ONGOING_COLOR,
        linewidth=2.8,
    )
    ax.scatter(
        x_ongoing, spine_y, marker="$\u2192$", color=ONGOING_COLOR, s=260, zorder=4
    )
    ax.text(
        x_ongoing,
        0.64,
        "ONGOING\nMONITORING",
        fontsize=17,
        fontweight="bold",
        color=ONGOING_COLOR,
        ha="center",
        va="bottom",
        family="DejaVu Sans",
        linespacing=1.3,
        bbox=dict(
            boxstyle="round,pad=0.36",
            facecolor="white",
            edgecolor=ONGOING_COLOR,
            lw=1.6,
            linestyle="--",
        ),
    )

    ax.set_xlim(x_coords[0] - 0.75, x_ongoing + 0.85)
    ax.set_ylim(-2.3, 2.3)
    ax.axis("off")

    # Title & Subtitle
    fig.text(
        0.5,
        0.975,
        "DISASTER RESPONSE TIMELINE",
        fontsize=34,
        fontweight="bold",
        color=TEXT_COLOR,
        ha="center",
        family="DejaVu Sans",
    )
    fig.text(
        0.5,
        0.945,
        subtitle_text,
        fontsize=19,
        color=SUBTEXT_COLOR,
        ha="center",
        style="italic",
    )
    fig.add_artist(
        plt.Line2D(
            [0.08, 0.92],
            [0.925, 0.925],
            transform=fig.transFigure,
            color=LINE_COLOR,
            lw=1.2,
        )
    )

    # Dynamic Legend built from user-defined categories
    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=cat,
            markerfacecolor=color,
            markersize=15,
            markeredgecolor=color,
        )
        for cat, color in st.session_state.categories.items()
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=len(st.session_state.categories)
        if len(st.session_state.categories) > 0
        else 1,
        frameon=False,
        fontsize=16,
        bbox_to_anchor=(0.5, 0.025),
        labelcolor=TEXT_COLOR,
        handletextpad=0.6,
        columnspacing=1.8,
    )
    fig.add_artist(
        plt.Line2D(
            [0.08, 0.92],
            [0.075, 0.075],
            transform=fig.transFigure,
            color=LINE_COLOR,
            lw=1.0,
        )
    )
    fig.text(
        0.92,
        0.02,
        source_text,
        fontsize=12,
        color=SUBTEXT_COLOR,
        ha="right",
        style="italic",
    )

    plt.tight_layout(rect=[0.02, 0.09, 0.98, 0.915])

    # Save to buffer for download
    buf = io.BytesIO()
    plt.savefig(
        buf, format="png", dpi=300, facecolor=BG_COLOR, bbox_inches="tight"
    )
    buf.seek(0)
    plt.close()

    st.success("Timeline successfully generated with your custom legend!")
    st.image(
        buf, caption="Generated Timeline Preview", use_container_width=True
    )

    st.download_button(
        label="📥 Download High-Resolution Image (PNG)",
        data=buf,
        file_name="Custom_Timeline.png",
        mime="image/png",
    )
