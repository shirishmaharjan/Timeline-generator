import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import textwrap

# Page configuration
st.set_page_config(
    page_title="Fully Customizable Timeline Generator",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 Fully Customizable Disaster Response Timeline Generator")
st.markdown(
    "Configure your titles, fonts, colors, and categories in the sidebar, edit"
    " your timeline data, and download your customized graphic instantly."
)

# -----------------------------------------------------------------------------
# 1. SESSION STATE SETUP
# -----------------------------------------------------------------------------
if "categories" not in st.session_state:
  st.session_state.categories = {
      "Emergency Alert": "#C0392B",
      "Field Assessment": "#D35400",
      "Road & Logistics": "#2980B9",
      "Geological Survey": "#8E44AD",
      "Relief & Recovery": "#27AE60",
  }

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
# 2. SIDEBAR: FULL CUSTOMIZATION DASHBOARD
# -----------------------------------------------------------------------------
st.sidebar.header("🛠️ Customization Dashboard")

# --- TAB 1: LEGEND CATEGORIES ---
with st.sidebar.expander("🎨 1. Legend & Categories", expanded=True):
  st.markdown("Define category names and their matching hex colors:")
  cat_df = pd.DataFrame([
      {"Category Name": k, "Color (Hex)": v}
      for k, v in st.session_state.categories.items()
  ])
  edited_cat_df = st.data_editor(
      cat_df, num_rows="dynamic", key="cat_editor", use_container_width=True
  )

  new_categories = {}
  for _, row in edited_cat_df.iterrows():
    name = str(row["Category Name"]).strip()
    color = str(row["Color (Hex)"]).strip()
    if name and name != "nan":
      if not color.startswith("#"):
        color = "#3B82F6"
      new_categories[name] = color
  st.session_state.categories = new_categories

# --- TAB 2: TITLES & TEXT ---
with st.sidebar.expander("📝 2. Titles & Footers", expanded=False):
  main_title_text = st.text_input(
      "Main Chart Title", "DISASTER RESPONSE TIMELINE"
  )
  subtitle_text = st.text_input(
      "Subtitle / Date Range",
      "Emergency Operations Timeline  —  October 12 – 17, 2026",
  )
  source_text = st.text_input(
      "Source Footer",
      "Source: District Disaster Management Committee (DDMC) SitReps",
  )

# --- TAB 3: FONTS & SIZES ---
with st.sidebar.expander("🔤 3. Fonts & Text Sizes", expanded=False):
  font_family_choice = st.selectbox(
      "Font Family", ["DejaVu Sans", "Arial", "Helvetica", "Times New Roman"]
  )
  title_fontsize = st.slider("Main Title Font Size", 20, 45, 34)
  subtitle_fontsize = st.slider("Subtitle Font Size", 12, 26, 19)
  date_fontsize = st.slider("Date Box Font Size", 10, 24, 17)
  activity_fontsize = st.slider("Activity Text Font Size", 10, 24, 15)
  legend_fontsize = st.slider("Legend Font Size", 10, 24, 16)

# --- TAB 4: COLORS & THEME ---
with st.sidebar.expander("🎨 4. Theme & Colors", expanded=False):
  bg_color_choice = st.color_picker(
      "Background Color", "#FFFFFF"
  )  # Background
  card_fill_choice = st.color_picker(
      "Card Fill Color", "#F7F9FB"
  )  # Activity Box Fill
  card_edge_choice = st.color_picker(
      "Card Border Color", "#D8DEE7"
  )  # Activity Box Border
  line_color_choice = st.color_picker("Timeline Line Color", "#C2CAD6")  # Spine
  text_color_choice = st.color_picker(
      "Main Text Color", "#1A2332"
  )  # Activity Text Color
  subtext_color_choice = st.color_picker(
      "Subtext / Footer Color", "#5B6B7F"
  )  # Subtitle Color

# -----------------------------------------------------------------------------
# 3. MAIN AREA: EDIT TIMELINE DATA
# -----------------------------------------------------------------------------
st.subheader("📝 Edit Timeline Data")
st.markdown(
    "The **Category** dropdown choices automatically sync with your custom"
    " legend categories defined in the sidebar."
)

df_input = pd.DataFrame(st.session_state.data)
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

    fig, ax = plt.subplots(figsize=(26, 14.5), facecolor=bg_color_choice)
    ax.set_facecolor(bg_color_choice)

    # Track band
    ax.axhspan(-0.045, 0.045, xmin=0.0, xmax=1.0, color="#EEF1F5", zorder=0)
    ax.plot(
        [x_coords[0] - 0.6, x_ongoing + 0.55],
        [spine_y, spine_y],
        color=line_color_choice,
        lw=2.6,
        zorder=1,
        solid_capstyle="round",
    )

    for i, row in edited_df.iterrows():
      x = x_coords[i]
      is_up = i % 2 == 0
      sign = 1 if is_up else -1
      va = "bottom" if is_up else "top"

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
          fontsize=date_fontsize,
          fontweight="bold",
          color=cat_color,
          ha="center",
          va=va,
          family=font_family_choice,
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
          fontsize=activity_fontsize,
          color=text_color_choice,
          ha="center",
          va=va,
          linespacing=1.55,
          fontweight="medium",
          family=font_family_choice,
          bbox=dict(
              boxstyle="round,pad=0.6",
              facecolor=card_fill_choice,
              edgecolor=card_edge_choice,
              lw=1.2,
          ),
      )

    # Ongoing marker
    ongoing_color_val = "#475569"
    ax.scatter(
        x_ongoing,
        spine_y,
        color="white",
        s=460,
        zorder=3,
        edgecolors=ongoing_color_val,
        linewidth=2.8,
    )
    ax.scatter(
        x_ongoing,
        spine_y,
        marker="$\u2192$",
        color=ongoing_color_val,
        s=260,
        zorder=4,
    )
    ax.text(
        x_ongoing,
        0.64,
        "ONGOING\nMONITORING",
        fontsize=date_fontsize,
        fontweight="bold",
        color=ongoing_color_val,
        ha="center",
        va="bottom",
        family=font_family_choice,
        linespacing=1.3,
        bbox=dict(
            boxstyle="round,pad=0.36",
            facecolor="white",
            edgecolor=ongoing_color_val,
            lw=1.6,
            linestyle="--",
        ),
    )

    ax.set_xlim(x_coords[0] - 0.75, x_ongoing + 0.85)
    ax.set_ylim(-2.3, 2.3)
    ax.axis("off")

    # Dynamic Titles & Footers with user choices
    fig.text(
        0.5,
        0.975,
        main_title_text,
        fontsize=title_fontsize,
        fontweight="bold",
        color=text_color_choice,
        ha="center",
        family=font_family_choice,
    )
    fig.text(
        0.5,
        0.945,
        subtitle_text,
        fontsize=subtitle_fontsize,
        color=subtext_color_choice,
        ha="center",
        style="italic",
        family=font_family_choice,
    )
    fig.add_artist(
        plt.Line2D(
            [0.08, 0.92],
            [0.925, 0.925],
            transform=fig.transFigure,
            color=line_color_choice,
            lw=1.2,
        )
    )

    # Dynamic Legend
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
        fontsize=legend_fontsize,
        bbox_to_anchor=(0.5, 0.025),
        labelcolor=text_color_choice,
        handletextpad=0.6,
        columnspacing=1.8,
    )
    fig.add_artist(
        plt.Line2D(
            [0.08, 0.92],
            [0.075, 0.075],
            transform=fig.transFigure,
            color=line_color_choice,
            lw=1.0,
        )
    )
    fig.text(
        0.92,
        0.02,
        source_text,
        fontsize=12,
        color=subtext_color_choice,
        ha="right",
        style="italic",
        family=font_family_choice,
    )

    plt.tight_layout(rect=[0.02, 0.09, 0.98, 0.915])

    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(
        buf,
        format="png",
        dpi=300,
        facecolor=bg_color_choice,
        bbox_inches="tight",
    )
    buf.seek(0)
    plt.close()

    st.success(
        "Timeline successfully generated with your custom design settings!"
    )
    st.image(
        buf, caption="Generated Timeline Preview", use_container_width=True
    )

    st.download_button(
        label="📥 Download High-Resolution Image (PNG)",
        data=buf,
        file_name="Custom_Timeline.png",
        mime="image/png",
    )
