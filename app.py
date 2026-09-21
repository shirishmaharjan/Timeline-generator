import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import textwrap

# Page configuration
st.set_page_config(
    page_title="Landslide Response Timeline Generator",
    page_icon="🏔️",
    layout="wide",
)

st.title("🏔️ Landslide Disaster Response Timeline Generator")
st.markdown(
    "Modify the landslide emergency data below, customize settings, and"
    " generate/download your high-res timeline graphic instantly."
)

# Initialize default data for a landslide response scenario
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

# Sidebar configurations
st.sidebar.header("⚙️ Chart Settings")
subtitle_text = st.sidebar.text_input(
    "Subtitle / Date Range",
    "Emergency Operations Timeline  —  October 12 – 17, 2026",
)
source_text = st.sidebar.text_input(
    "Source Footer",
    "Source: District Disaster Management Committee (DDMC) SitReps",
)

st.subheader("📝 Edit Timeline Data")
st.markdown(
    "Add rows, delete rows, or edit text directly in the table below. (Categories"
    " allowed: Emergency Alert, Field Assessment, Road & Logistics, Geological"
    " Survey, Relief & Recovery)"
)

df_input = pd.DataFrame(st.session_state.data)
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# Colors tailored for landslide/environmental themes
BG_COLOR = "#FFFFFF"
CARD_EDGE = "#D8DEE7"
CARD_FILL = "#F7F9FB"
TEXT_COLOR = "#1A2332"
SUBTEXT_COLOR = "#5B6B7F"
LINE_COLOR = "#C2CAD6"
ONGOING_COLOR = "#475569"

CATEGORY_COLORS = {
    "Emergency Alert": "#C0392B",  # Red
    "Field Assessment": "#D35400",  # Dark Orange
    "Road & Logistics": "#2980B9",  # Blue
    "Geological Survey": "#8E44AD",  # Purple
    "Relief & Recovery": "#27AE60",  # Green
}


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


if st.button("🚀 Generate & Update Chart", type="primary"):
  if edited_df.empty:
    st.warning("Please enter at least one timeline entry.")
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
      cat_color = CATEGORY_COLORS.get(row.get("Category"), "#3B82F6")
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
        "LANDSLIDE EMERGENCY RESPONSE TIMELINE",
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

    # Legend
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
        for cat, color in CATEGORY_COLORS.items()
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=len(CATEGORY_COLORS),
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

    st.success("Landslide Timeline successfully generated!")
    st.image(
        buf, caption="Generated Timeline Preview", use_container_width=True
    )

    st.download_button(
        label="📥 Download High-Resolution Image (PNG)",
        data=buf,
        file_name="Landslide_Response_Timeline.png",
        mime="image/png",
    )
